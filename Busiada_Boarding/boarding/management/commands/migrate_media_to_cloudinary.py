from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

from django.apps import apps
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.core.files.storage import default_storage
from django.db.models import FileField


class Command(BaseCommand):
    help = (
        'Copy locally stored FileField assets to Cloudinary without deleting '
        'the source files. Dry-run unless --apply is provided.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-dir',
            type=Path,
            default=settings.MEDIA_ROOT,
            help='Verified directory containing the source media files.',
        )
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Upload files and update database names after successful uploads.',
        )
        parser.add_argument(
            '--include-documents',
            action='store_true',
            help=(
                'Also migrate Document.file assets. Use only after confirming '
                'they are intended to be publicly accessible.'
            ),
        )

    def handle(self, *args, **options):
        if args:
            raise CommandError('Unexpected positional arguments.')

        source_root = options['source_dir'].resolve()
        if not source_root.is_dir():
            raise CommandError(f'Source media directory not found: {source_root}')

        if options['apply']:
            if settings.DEBUG:
                raise CommandError(
                    'Set DJANGO_DEBUG=False before applying media migration.'
                )
            backend = settings.STORAGES['default']['BACKEND']
            if backend != 'cloudinary_storage.storage.MediaCloudinaryStorage':
                raise CommandError(
                    'The configured default storage is not Cloudinary.'
                )

        references = 0
        uploaded = 0
        already_present = 0
        external = 0
        documents_skipped = 0
        uploaded_names = {}

        for model in apps.get_models():
            is_document = model._meta.label_lower == 'boarding.document'
            for field in model._meta.get_fields():
                if not isinstance(field, FileField):
                    continue

                queryset = model.objects.using('default').only(
                    'pk', field.name
                )
                for instance in queryset.iterator():
                    field_file = getattr(instance, field.name)
                    name = field_file.name
                    if not name:
                        continue
                    references += 1

                    if is_document and not options['include_documents']:
                        documents_skipped += 1
                        continue
                    if urlparse(name).scheme in ('http', 'https'):
                        external += 1
                        continue

                    relative_path = PurePosixPath(name)
                    if relative_path.is_absolute() or '..' in relative_path.parts:
                        raise CommandError(
                            f'Unsafe media path in {model._meta.label} '
                            f'{instance.pk}, field {field.name}.'
                        )
                    source_path = (
                        source_root.joinpath(*relative_path.parts).resolve()
                    )
                    if source_root not in source_path.parents:
                        raise CommandError(
                            f'Media path escapes the source directory for '
                            f'{model._meta.label} {instance.pk}.'
                        )
                    if not source_path.is_file():
                        raise CommandError(
                            f'Source media file is missing for '
                            f'{model._meta.label} {instance.pk}, '
                            f'field {field.name}: {relative_path.as_posix()}'
                        )

                    if not options['apply']:
                        continue

                    migrated_name = uploaded_names.get(name)
                    if migrated_name is None:
                        if default_storage.exists(name):
                            migrated_name = name
                            already_present += 1
                        else:
                            with source_path.open('rb') as source_file:
                                migrated_name = default_storage.save(
                                    name, File(source_file)
                                )
                            if not default_storage.exists(migrated_name):
                                raise CommandError(
                                    'Cloudinary upload did not pass its '
                                    f'accessibility check for {relative_path.as_posix()}.'
                                )
                            uploaded += 1
                        uploaded_names[name] = migrated_name

                    if migrated_name != name:
                        setattr(instance, field.name, migrated_name)
                        instance.save(update_fields=[field.name])

        self.stdout.write(
            self.style.SUCCESS(
                f'Media references: {references}; uploaded: {uploaded}; '
                f'already in Cloudinary: {already_present}; external URLs: '
                f'{external}; protected documents skipped: {documents_skipped}.'
            )
        )
        if not options['apply']:
            self.stdout.write(
                'Dry run only. Original media files were not changed. '
                'Add --apply to upload eligible files.'
            )
