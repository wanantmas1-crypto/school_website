import hashlib
import time
import os
from django.utils.crypto import get_random_string
from django.core.files.storage import default_storage


def _hash_filename(filename):
    name, ext = os.path.splitext(filename)
    stamp = str(int(time.time()))
    rand = get_random_string(6)
    h = hashlib.sha256((name + stamp + rand).encode('utf-8')).hexdigest()[:40]
    return f"{h}{ext.lower()}"


def image_upload_to(instance, filename):
    """Upload images into media/site_pages/ with hashed filename."""
    fname = _hash_filename(filename)
    return os.path.join('site_pages', fname)


def video_upload_to(instance, filename):
    fname = _hash_filename(filename)
    return os.path.join('videos', fname)


def document_upload_to(instance, filename):
    fname = _hash_filename(filename)
    return os.path.join('documents', fname)


def anthem_audio_upload_to(instance, filename):
    fname = _hash_filename(filename)
    return os.path.join('anthem', fname)


def safe_file_url(field_file):
    if not field_file:
        return ''

    try:
        if not isinstance(field_file, str):
            name = getattr(field_file, 'name', '') or ''
            if not name:
                return ''

            try:
                if default_storage.exists(name):
                    return default_storage.url(name)
            except Exception:
                return getattr(field_file, 'url', '') or ''
        else:
            name = field_file

        if not name:
            return ''

        candidates = [name]
        basename = os.path.basename(name)
        if basename:
            candidates.extend([
                os.path.join('boarding.utils.image_upload_to', basename),
                os.path.join('site_pages', basename),
            ])

        for candidate in candidates:
            try:
                if default_storage.exists(candidate):
                    return default_storage.url(candidate)
            except Exception:
                continue
    except Exception:
        return ''

    return ''
