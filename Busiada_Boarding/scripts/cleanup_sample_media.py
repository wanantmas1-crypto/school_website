import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.core.files.storage import default_storage
from boarding.models import PageImage, PageVideo, Document, Announcement, SiteSettings
from django.db import transaction

# Determine project root robustly (support running via exec/open where __file__ may be missing)
try:
    THIS_DIR = os.path.dirname(__file__)
except NameError:
    THIS_DIR = os.getcwd()
MEDIA_DIR = os.path.abspath(os.path.join(THIS_DIR, '..', 'media'))
# Only clean up announcements (test data). Preserve images, videos, documents, principals.
TARGET_DIRS = ['announcements']

deleted_files = []
deleted_pageimages = []
deleted_pagevideos = []
deleted_documents = []
cleared_announcements = []
cleared_sitesettings = []

print('Removing media files in:', TARGET_DIRS)

# Delete PageImage instances whose image path starts with target dirs
for pi in PageImage.objects.all():
    name = (pi.image.name or '')
    if any(name.startswith(d + '/') for d in TARGET_DIRS):
        try:
            if name and default_storage.exists(name):
                default_storage.delete(name)
                deleted_files.append(name)
        except Exception as e:
            print('Error deleting file', name, e)
        deleted_pageimages.append((pi.pk, name))
        pi.delete()

# Delete PageVideo instances
for pv in PageVideo.objects.all():
    name = (pv.video.name or '')
    if any(name.startswith(d + '/') for d in TARGET_DIRS):
        try:
            if name and default_storage.exists(name):
                default_storage.delete(name)
                deleted_files.append(name)
        except Exception as e:
            print('Error deleting video', name, e)
        deleted_pagevideos.append((pv.pk, name))
        pv.delete()

# Delete Document instances
for d in Document.objects.all():
    name = (d.file.name or '')
    if any(name.startswith(d0 + '/') for d0 in TARGET_DIRS):
        try:
            if name and default_storage.exists(name):
                default_storage.delete(name)
                deleted_files.append(name)
        except Exception as e:
            print('Error deleting document file', name, e)
        deleted_documents.append((d.pk, name))
        d.delete()

# Clear Announcement.image fields that point to target dirs
for a in Announcement.objects.all():
    name = (a.image.name or '')
    if any(name.startswith(d + '/') for d in TARGET_DIRS):
        try:
            if name and default_storage.exists(name):
                default_storage.delete(name)
                deleted_files.append(name)
        except Exception as e:
            print('Error deleting announcement image', name, e)
        a.image = None
        a.save(update_fields=['image'])
        cleared_announcements.append((a.pk, name))

# Clear SiteSettings logo/principal_image if they point to target dirs
ss = SiteSettings.objects.first()
if ss:
    changed = False
    if ss.logo and any((ss.logo.name or '').startswith(d + '/') for d in TARGET_DIRS):
        try:
            if default_storage.exists(ss.logo.name):
                default_storage.delete(ss.logo.name)
                deleted_files.append(ss.logo.name)
        except Exception as e:
            print('Error deleting site logo', ss.logo.name, e)
        ss.logo = None
        changed = True
    if ss.principal_image and any((ss.principal_image.name or '').startswith(d + '/') for d in TARGET_DIRS):
        try:
            if default_storage.exists(ss.principal_image.name):
                default_storage.delete(ss.principal_image.name)
                deleted_files.append(ss.principal_image.name)
        except Exception as e:
            print('Error deleting principal image', ss.principal_image.name, e)
        ss.principal_image = None
        changed = True
    if changed:
        ss.save()
        cleared_sitesettings.append(ss.pk)

# Additionally remove any leftover files under media/<target_dir> on filesystem if present
fs_deleted = []
root_media = os.path.abspath(os.path.join(THIS_DIR, '..', 'media'))
for d in TARGET_DIRS:
    dirpath = os.path.join(root_media, d)
    if os.path.isdir(dirpath):
        for fname in os.listdir(dirpath):
            fpath = os.path.join(dirpath, fname)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
                    fs_deleted.append(os.path.join(d, fname))
            except Exception as e:
                print('Failed to remove file', fpath, e)

print('\nSummary:')
print('Deleted files via storage:', len(deleted_files))
for f in deleted_files[:50]:
    print(' -', f)
print('Deleted PageImage instances:', len(deleted_pageimages))
print('Deleted PageVideo instances:', len(deleted_pagevideos))
print('Deleted Document instances:', len(deleted_documents))
print('Cleared Announcement images:', len(cleared_announcements))
print('Cleared SiteSettings:', len(cleared_sitesettings))
print('Filesystem deletions:', len(fs_deleted))
for f in fs_deleted[:50]:
    print(' -', f)

print('\nDone.')
