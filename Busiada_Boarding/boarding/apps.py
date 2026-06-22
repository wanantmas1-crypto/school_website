from django.apps import AppConfig
import sys
from django.conf import settings


def _is_dev_runserver():
    """Return True when running the development server (manage.py runserver).

    This avoids executing on management commands like `migrate` or `makemigrations`.
    """
    argv = sys.argv
    return any(arg.startswith('runserver') for arg in argv)


class BoardingConfig(AppConfig):
    name = 'boarding'

    def ready(self):
        # Auto-fill slugs when running the local development server only.
        try:
            if settings.DEBUG and _is_dev_runserver():
                # Delay import to avoid side-effects during migrations
                from django.core.management import call_command
                # Run the fill_slugs command; ignore failures
                try:
                    call_command('fill_slugs')
                except Exception:
                    # Safe to ignore; admin/manual run can fix any issues
                    pass
        except Exception:
            # Be resilient to import issues in restricted environments
            pass
