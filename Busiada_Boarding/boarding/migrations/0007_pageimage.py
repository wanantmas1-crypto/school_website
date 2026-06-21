from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('boarding', '0006_alter_sitepage_options_sitepage_author_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sitepage',
            name='image',
        ),
        migrations.CreateModel(
            name='PageImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='site_pages/')),
                ('title', models.CharField(blank=True, max_length=200)),
                ('caption', models.CharField(blank=True, max_length=250)),
                ('description', models.TextField(blank=True)),
                ('order', models.PositiveIntegerField(default=0)),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='boarding.sitepage')),
                ('uploaded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order', 'uploaded_at'],
            },
        ),
    ]
