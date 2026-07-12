from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.http import Http404
from django.views.static import serve
from django.views.generic.base import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


def serve_site_page_media(request, path):
    """Serve media from site_pages directory, with fallback to old location."""
    try:
        return serve(request, path, document_root=settings.MEDIA_ROOT / 'site_pages')
    except Http404:
        return serve(request, path, document_root=settings.BASE_DIR / 'site_pages')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('', include('boarding.urls')),
]

# Serve media files locally when enabled
if settings.SERVE_MEDIA_FILES:
    urlpatterns += [
        # Site page media (images, videos, documents)
        re_path(r'^media/site_pages/(?P<path>.*)$', serve_site_page_media),
        # All media files (including uploaded admin content)
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]

# Serve static files locally in development
if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
