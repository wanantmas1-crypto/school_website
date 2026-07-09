from django.core.files.storage import default_storage
from boarding.models import PageImage, SitePage, SiteSettings, Announcement, Document, PageVideo

changed = 0

def ensure(field_obj):
    if not field_obj:
        return None
    name = getattr(field_obj, 'name', None)
    if not name:
        return None
    try:
        if default_storage.exists(name):
            return name
    except Exception:
        pass
    # file missing -> clear the field
    return None

for pi in PageImage.objects.all():
    cur = getattr(pi.image, 'name', None)
    ok = ensure(getattr(pi, 'image', None))
    if ok is None and cur:
        pi.image.delete(save=False)
        pi.image.name = ''
        pi.save(update_fields=['image'])
        print('Cleared PageImage', pi.id, 'was', cur)
        changed += 1

for sp in SitePage.objects.all():
    for field in ('featured_image','background_image'):
        f = getattr(sp, field, None)
        cur = getattr(f, 'name', None)
        ok = ensure(f)
        if ok is None and cur:
            try:
                f.delete(save=False)
            except Exception:
                pass
            setattr(sp, field, None)
            sp.save(update_fields=[field])
            print('Cleared SitePage', sp.id, field, 'was', cur)
            changed += 1

ss = SiteSettings.objects.first()
if ss:
    for field in ('principal_image','logo'):
        f = getattr(ss, field, None)
        cur = getattr(f, 'name', None)
        ok = ensure(f)
        if ok is None and cur:
            try:
                f.delete(save=False)
            except Exception:
                pass
            setattr(ss, field, None)
            ss.save(update_fields=[field])
            print('Cleared SiteSettings', field, 'was', cur)
            changed += 1

for a in Announcement.objects.all():
    f = getattr(a, 'image', None)
    cur = getattr(f, 'name', None) if f else None
    ok = ensure(f)
    if ok is None and cur:
        try:
            f.delete(save=False)
        except Exception:
            pass
        a.image = None
        a.save(update_fields=['image'])
        print('Cleared Announcement', a.id, 'was', cur)
        changed += 1

for d in Document.objects.all():
    f = getattr(d, 'file', None)
    cur = getattr(f, 'name', None) if f else None
    ok = ensure(f)
    if ok is None and cur:
        try:
            f.delete(save=False)
        except Exception:
            pass
        d.file = None
        d.save(update_fields=['file'])
        print('Cleared Document', d.id, 'was', cur)
        changed += 1

for v in PageVideo.objects.all():
    f = getattr(v, 'video', None)
    cur = getattr(f, 'name', None) if f else None
    ok = ensure(f)
    if ok is None and cur:
        try:
            f.delete(save=False)
        except Exception:
            pass
        v.video = None
        v.save(update_fields=['video'])
        print('Cleared PageVideo', v.id, 'was', cur)
        changed += 1

print('Total cleared fields:', changed)
