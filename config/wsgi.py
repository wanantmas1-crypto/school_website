"""WSGI config for outer config package.

This file exists only to satisfy Python package imports in the repo root.
It should not be used during normal Render deployment.
"""
import os
from django.core.wsgi import get_wsgi_application
import sys

# Ensure the inner project directory is on sys.path so imports like
# 'boarding' resolve when the process starts from the repo root.
# This covers cases where Render runs the module path directly.
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INNER_PROJECT = os.path.join(ROOT_DIR, 'Busiada_Boarding')
if INNER_PROJECT not in sys.path:
	sys.path.insert(0, INNER_PROJECT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Busiada_Boarding.config.settings')

application = get_wsgi_application()
