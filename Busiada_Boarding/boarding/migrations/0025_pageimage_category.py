from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boarding', '0024_default_school_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='pageimage',
            name='category',
            field=models.CharField(
                blank=True,
                choices=[
                    ('academics', 'Academics & Labs'),
                    ('sports', 'Sports & Games'),
                    ('arts', 'Arts & Culture'),
                    ('boarding', 'Boarding Life'),
                    ('events', 'Events'),
                ],
                default='',
                help_text='Used by the School Gallery filters.',
                max_length=20,
            ),
        ),
    ]
