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

# Import Django settings to get the configured STATIC_ROOT
from django.conf import settings

django_app = get_wsgi_application()

# Use Django's configured STATIC_ROOT for WhiteNoise
static_root = str(settings.STATIC_ROOT)
application = WhiteNoise(django_app, root=static_root, prefix='static/')
