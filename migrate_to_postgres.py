"""Safely copy a verified SQLite export into an empty PostgreSQL database.

This utility does not change Django settings or transfer uploaded media.
Run it only with a verified source database and a newly provisioned target.
"""

import argparse
from collections import Counter
from contextlib import closing
from datetime import datetime
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile


PROJECT_DIR = Path(__file__).resolve().parent / 'Busiada_Boarding'
DEFAULT_SOURCE = PROJECT_DIR / 'db.sqlite3'
EXCLUDED_MODELS = (
    'contenttypes',
    'auth.permission',
    'admin.logentry',
)


def sqlite_table_counts(database_path):
    with closing(sqlite3.connect(database_path)) as database:
        integrity = database.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            raise RuntimeError(
                f'SQLite integrity check failed for {database_path}.'
            )
        tables = database.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        counts = {}
        for (table_name,) in tables:
            quoted_name = table_name.replace('"', '""')
            counts[table_name] = database.execute(
                f'SELECT COUNT(*) FROM "{quoted_name}"'
            ).fetchone()[0]
        return counts


def create_verified_backup(source_path):
    backup_path = source_path.with_name(
        f'{source_path.stem}.backup-{datetime.now():%Y%m%d-%H%M%S-%f}'
        f'{source_path.suffix}'
    )
    with closing(sqlite3.connect(source_path)) as source_db:
        with closing(sqlite3.connect(backup_path)) as backup_db:
            source_db.backup(backup_db)

    if sqlite_table_counts(source_path) != sqlite_table_counts(backup_path):
        backup_path.unlink(missing_ok=True)
        raise RuntimeError(
            f'SQLite backup verification failed: {backup_path}'
        )
    return backup_path


def require_empty_postgres_target(connection):
    if connection.vendor != 'postgresql':
        raise RuntimeError(
            'DATABASE_URL must point to PostgreSQL; no data was changed.'
        )
    tables = connection.introspection.table_names()
    if tables:
        raise RuntimeError(
            'The target database is not empty. Refusing to apply migrations '
            'or load data into it. Use a new PostgreSQL database.'
        )


def expected_model_counts(fixture_path):
    with fixture_path.open(encoding='utf-8') as fixture_file:
        objects = json.load(fixture_file)
    return Counter(item['model'].lower() for item in objects)


def verify_model_counts(counts, apps, target_connection):
    mismatches = []
    for model_label, expected in sorted(counts.items()):
        app_label, model_name = model_label.split('.', maxsplit=1)
        model = apps.get_model(app_label, model_name)
        actual = model.objects.using(target_connection.alias).count()
        if actual != expected:
            mismatches.append(
                f'{model_label}: source={expected}, target={actual}'
            )
    if mismatches:
        raise RuntimeError(
            'Record-count verification failed:\n' + '\n'.join(mismatches)
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--source',
        type=Path,
        default=DEFAULT_SOURCE,
        help=(
            'Verified SQLite source/export file (default: workspace db.sqlite3; '
            'this may not be the live production database).'
        ),
    )
    parser.add_argument(
        '--apply',
        action='store_true',
        help='Create a verified backup, migrate the target, and load data.',
    )
    args = parser.parse_args()

    if not os.environ.get('DATABASE_URL'):
        parser.error('Set DATABASE_URL to the new PostgreSQL database first.')

    source_path = args.source.resolve()
    if not source_path.is_file():
        parser.error(f'SQLite source file does not exist: {source_path}')

    sys.path.insert(0, str(PROJECT_DIR))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    import django

    django.setup()

    from django.apps import apps
    from django.conf import settings
    from django.core.management import call_command
    from django.db import connections

    target_connection = connections['default']
    require_empty_postgres_target(target_connection)
    print(f'Source SQLite file: {source_path}')
    print('Target PostgreSQL database: reachable and empty')

    if not args.apply:
        print('Dry run only. Review the source and target, then rerun with --apply.')
        return

    backup_path = create_verified_backup(source_path)
    print(f'Verified SQLite backup created: {backup_path}')

    settings.DATABASES['migration_source'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': source_path,
    }
    fixture_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            encoding='utf-8',
            delete=False,
        ) as fixture_file:
            fixture_path = Path(fixture_file.name)

        call_command(
            'dumpdata',
            database='migration_source',
            natural_foreign=True,
            exclude=EXCLUDED_MODELS,
            output=str(fixture_path),
        )
        source_counts = expected_model_counts(fixture_path)

        call_command('migrate', database='default', interactive=False)
        call_command(
            'loaddata',
            str(fixture_path),
            database='default',
            verbosity=1,
        )
        verify_model_counts(source_counts, apps, target_connection)
    finally:
        if fixture_path is not None:
            fixture_path.unlink(missing_ok=True)

    print(
        'Database schema and fixture data were migrated and record counts '
        'verified. Uploaded media must be migrated and verified separately.'
    )


if __name__ == '__main__':
    main()
