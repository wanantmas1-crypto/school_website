import hashlib
import time
import os
from django.utils.crypto import get_random_string


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
