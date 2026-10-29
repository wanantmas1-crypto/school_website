from .models import SitePage, SiteSettings
from .utils import safe_file_url


def photo_highlights(request):
    home_page = SitePage.objects.filter(slug='home').first()
    photos = []

    if home_page:
        for image in home_page.images.exclude(
            category__slug='why-parents-choose-us'
        ).order_by('order', 'uploaded_at')[:4]:
            src = image.display_url()
            if src:
                photos.append({
                    'src': src,
                    'alt': image.caption or image.title or 'Busiada Girls School photo',
                })

    return {'photo_highlights': photos}


def site_settings(request):
    try:
        settings = SiteSettings.objects.first()
        if settings:
            settings.principal_image_url = safe_file_url(getattr(settings, 'principal_image', None))
            settings.logo_url = safe_file_url(getattr(settings, 'logo', None))
            settings.phone_number_href = ''.join(
                character for character in settings.phone_number
                if character.isdigit() or character == '+'
            )
    except Exception:
        settings = None
    return {'site_settings': settings}
