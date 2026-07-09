from django.core.files.storage import default_storage
from boarding.models import PageImage, SitePage, SiteSettings, Announcement, Document, PageVideo

def resolve(name):
    if not name:
        return None
    # Already an absolute URL
    if name.startswith('http://') or name.startswith('https://'):
        return name
    if default_storage.exists(name):
        return name
    parts = name.replace('\\\\','/').replace('\\','/').split('/')
    basename = parts[-1] if parts else name
    candidates = [
        f'boarding.utils.image_upload_to/{basename}',
        f'site_pages/{basename}',
        f'site_pages/backgrounds/{basename}',
        f'announcements/{basename}',
        f'documents/{basename}',
        basename,
    ]
    for c in candidates:
        try:
            if default_storage.exists(c):
                return c
        except Exception:
            continue
    return None

updated = 0

for PI in PageImage.objects.all():
    cur = getattr(PI.image, 'name', None)
    new = resolve(cur)
    if new and new != cur:
        PI.image.name = new
        PI.save(update_fields=['image'])
        print('PageImage', PI.id, 'updated->', new)
        updated += 1

for SP in SitePage.objects.all():
    for field in ('featured_image','background_image'):
        f = getattr(SP, field, None)
        cur = getattr(f, 'name', None)
        new = resolve(cur)
        if new and new != cur:
            setattr(SP, field, new)
            SP.save(update_fields=[field])
            print('SitePage', SP.id, field, 'updated->', new)
            updated += 1

SS = SiteSettings.objects.first()
if SS:
    for field in ('principal_image','logo'):
        f = getattr(SS, field, None)
        cur = getattr(f, 'name', None)
        new = resolve(cur)
        if new and new != cur:
            setattr(SS, field, new)
            SS.save(update_fields=[field])
            print('SiteSettings', field, 'updated->', new)
            updated += 1

for A in Announcement.objects.all():
    cur = getattr(A, 'image').name if getattr(A, 'image', None) else None
    new = resolve(cur)
    if new and new != cur:
        A.image.name = new
        A.save(update_fields=['image'])
        print('Announcement', A.id, 'updated->', new)
        updated += 1

for D in Document.objects.all():
    cur = getattr(D, 'file').name if getattr(D, 'file', None) else None
    new = resolve(cur)
    if new and new != cur:
        D.file.name = new
        D.save(update_fields=['file'])
        print('Document', D.id, 'updated->', new)
        updated += 1

for V in PageVideo.objects.all():
    cur = getattr(V, 'video').name if getattr(V, 'video', None) else None
    new = resolve(cur)
    if new and new != cur:
        V.video.name = new
        V.save(update_fields=['video'])
        print('PageVideo', V.id, 'updated->', new)
        updated += 1

print('Total updates:', updated)
