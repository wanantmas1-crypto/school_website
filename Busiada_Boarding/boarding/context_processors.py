from .models import SiteSettings


def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
    except Exception:
        settings = None
    return {'site_settings': settings}


def csp_nonce(request):
    """Expose `csp_nonce` to templates when present on the request."""
    return {'csp_nonce': getattr(request, 'csp_nonce', None)}
