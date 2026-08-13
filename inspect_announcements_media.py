import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import pathlib

django.setup()
from django.conf import settings
from boarding.models import Announcement

print('cwd=', os.getcwd())
print('MEDIA_ROOT=', settings.MEDIA_ROOT)
print('SERVE_MEDIA_FILES=', settings.SERVE_MEDIA_FILES)
print('DEFAULT_FILE_STORAGE=', settings.DEFAULT_FILE_STORAGE)
print('ANNOUNCEMENT_COUNT=', Announcement.objects.count())
root = pathlib.Path(settings.MEDIA_ROOT)
print('MEDIA_ROOT exists=', root.exists())
for a in Announcement.objects.all()[:20]:
    name = a.image.name
    url = a.image.url if name else None
    exists = bool(name and (root / name).exists())
    print(a.pk, repr(a.title), repr(name), repr(url), 'exists=', exists)
