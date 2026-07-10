"""Compatibility WSGI entrypoint.

This module makes `python -m gunicorn config.wsgi` work from the repo root
by delegating to the real WSGI application in `Busiada_Boarding.config.wsgi`.
"""
import os
from importlib import import_module

# Ensure the Django settings point to the package settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Busiada_Boarding.config.settings')

# Import the real application and expose it as `application`
_mod = import_module('Busiada_Boarding.config.wsgi')
application = getattr(_mod, 'application')
