from pathlib import Path
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from boarding.models import PageImage, SitePage, SiteSettings, Announcement, Document, PageVideo

MEDIA_ROOT = Path(settings.MEDIA_ROOT)

moved = 0
updated = 0

def move_and_normalize(name):
    if not name:
        return None
    # ignore URLs
    if name.startswith('http://') or name.startswith('https://'):
        return name
    src_path = MEDIA_ROOT / name
    # If file exists at stored path, and is already under site_pages, leave it
    if src_path.exists():
        # Normalize to site_pages if it's under boarding.utils.*
        if 'boarding.utils.image_upload_to' in name:
            basename = Path(name).name
            dest = MEDIA_ROOT / 'site_pages' / basename
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.move(str(src_path), str(dest))
                return f'site_pages/{basename}'
            else:
                # destination exists; remove source
                try:
                    src_path.unlink()
                except Exception:
                    pass
                return f'site_pages/{basename}'
        return name

    # If file not at stored path, try to find it under boarding.utils.image_upload_to or site_pages
    basename = Path(name).name
    candidates = [
        MEDIA_ROOT / 'boarding.utils.image_upload_to' / basename,
        MEDIA_ROOT / 'site_pages' / basename,
        MEDIA_ROOT / basename,
    ]
    for c in candidates:
        if c.exists():
            # move to site_pages if not already
            dest = MEDIA_ROOT / 'site_pages' / basename
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists():
                shutil.move(str(c), str(dest))
                return f'site_pages/{basename}'
            else:
                try:
                    c.unlink()
                except Exception:
                    pass
                return f'site_pages/{basename}'
    return None

# Update PageImage
for pi in PageImage.objects.all():
    cur = getattr(pi.image, 'name', None)
    new = move_and_normalize(cur)
    if new and new != cur:
        pi.image.name = new
        pi.save(update_fields=['image'])
        print('PageImage', pi.id, '->', new)
        updated += 1

# Update SitePage featured/background
for sp in SitePage.objects.all():
    for field in ('featured_image', 'background_image'):
        f = getattr(sp, field, None)
        cur = getattr(f, 'name', None)
        new = move_and_normalize(cur)
        if new and new != cur:
            setattr(sp, field, new)
            sp.save(update_fields=[field])
            print('SitePage', sp.id, field, '->', new)
            updated += 1

# Update SiteSettings
ss = SiteSettings.objects.first()
if ss:
    for field in ('principal_image', 'logo'):
        f = getattr(ss, field, None)
        cur = getattr(f, 'name', None)
        new = move_and_normalize(cur)
        if new and new != cur:
            setattr(ss, field, new)
            ss.save(update_fields=[field])
            print('SiteSettings', field, '->', new)
            updated += 1

# Announcements
for a in Announcement.objects.all():
    cur = getattr(a, 'image').name if getattr(a, 'image', None) else None
    new = move_and_normalize(cur)
    if new and new != cur:
        a.image.name = new
        a.save(update_fields=['image'])
        print('Announcement', a.id, '->', new)
        updated += 1

# Documents
for d in Document.objects.all():
    cur = getattr(d, 'file').name if getattr(d, 'file', None) else None
    new = move_and_normalize(cur)
    if new and new != cur:
        d.file.name = new
        d.save(update_fields=['file'])
        print('Document', d.id, '->', new)
        updated += 1

# Videos
for v in PageVideo.objects.all():
    cur = getattr(v, 'video').name if getattr(v, 'video', None) else None
    new = move_and_normalize(cur)
    if new and new != cur:
        v.video.name = new
        v.save(update_fields=['video'])
        print('PageVideo', v.id, '->', new)
        updated += 1

print('Moved files and updated DB entries count:', updated)
