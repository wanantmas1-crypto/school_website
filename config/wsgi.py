"""WSGI config for outer config package.

This file exists only to satisfy Python package imports in the repo root.
It should not be used during normal Render deployment.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Busiada_Boarding.config.settings')

application = get_wsgi_application()
