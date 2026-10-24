from .models import SiteSettings
from .utils import safe_file_url


def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        if settings:
            settings.principal_image_url = safe_file_url(getattr(settings, 'principal_image', None))
            settings.logo_url = safe_file_url(getattr(settings, 'logo', None))
    except Exception:
        settings = None
    return {'site_settings': settings}
