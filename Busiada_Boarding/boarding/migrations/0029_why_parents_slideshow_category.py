from django.db import migrations


def create_why_parents_category(apps, schema_editor):
    GalleryCategory = apps.get_model('boarding', 'GalleryCategory')
    GalleryCategory.objects.using(schema_editor.connection.alias).get_or_create(
        slug='why-parents-choose-us',
        defaults={
            'name': 'Why Parents Choose Us Slideshow',
            'order': 5,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ('boarding', '0028_announcement_is_important'),
    ]

    operations = [
        migrations.RunPython(create_why_parents_category, migrations.RunPython.noop),
    ]
