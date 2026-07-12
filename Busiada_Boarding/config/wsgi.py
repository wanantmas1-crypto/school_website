"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

django_app = get_wsgi_application()

# Wrap with WhiteNoise for static file serving
BASE_DIR = Path(__file__).resolve().parent.parent
static_root = str(BASE_DIR / 'staticfiles')
application = WhiteNoise(django_app, root=static_root, prefix='static/')
