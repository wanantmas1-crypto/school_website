from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.db import DatabaseError, connection
from django.db.migrations.executor import MigrationExecutor
from django.http import Http404, HttpResponse
from django.views.static import serve
from django.views.generic.base import TemplateView
import logging


logger = logging.getLogger(__name__)


def health_check(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        executor = MigrationExecutor(connection)
        pending_migrations = executor.migration_plan(
            executor.loader.graph.leaf_nodes()
        )
    except DatabaseError as error:
        logger.error(
            'Health check failed because the database is unavailable (%s).',
            type(error).__name__,
        )
        return HttpResponse('Service unavailable', status=503)
    if pending_migrations:
        logger.error(
            'Health check failed because %s database migrations are pending.',
            len(pending_migrations),
        )
        return HttpResponse('Service unavailable', status=503)
    return HttpResponse('ok', content_type='text/plain')


def serve_site_page_media(request, path):
    """Serve media from site_pages directory, with fallback to old location."""
    try:
        return serve(request, path, document_root=settings.MEDIA_ROOT / 'site_pages')
    except Http404:
        return serve(request, path, document_root=settings.BASE_DIR / 'site_pages')

urlpatterns = [
    path('healthz/', health_check, name='health_check'),
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
