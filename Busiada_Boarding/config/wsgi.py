"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

# Ensure local project root is on sys.path when Render starts inside Busiada_Boarding.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Configure WhiteNoise for static files serving in production
static_root = PROJECT_ROOT / 'staticfiles'
application = WhiteNoise(
    application, 
    root=str(static_root),
    prefix='static/',
    compress=True,
    max_age=60 * 60 * 24 * 365  # 1 year cache
)
