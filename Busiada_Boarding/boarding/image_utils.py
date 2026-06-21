import io
import os
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def generate_responsive_versions(fieldfile, sizes=(320, 640, 1200)):
    """Generate resized JPEG versions for an ImageField `fieldfile`.
    Saves files alongside the original with suffix _{width}w.jpg.
    """
    if not fieldfile:
        return

    try:
        from PIL import Image
    except Exception:
        # Pillow not available; skip
        return

    name = fieldfile.name
    if not name:
        return

    base_name, _ext = os.path.splitext(name)

    # open via storage
    try:
        with fieldfile.open('rb') as f:
            img = Image.open(f)
            img = img.convert('RGB')
            orig_w, orig_h = img.size

            for w in sizes:
                dest_name = f"{base_name}_{w}w.jpg"
                if default_storage.exists(dest_name):
                    continue

                if orig_w <= w:
                    resized = img
                else:
                    h = int(orig_h * w / orig_w)
                    resized = img.resize((w, h), Image.LANCZOS)

                buf = io.BytesIO()
                resized.save(buf, format='JPEG', quality=85)
                buf.seek(0)
                content = ContentFile(buf.read())
                default_storage.save(dest_name, content)
    except Exception:
        # Fail gracefully; don't interrupt save
        return
