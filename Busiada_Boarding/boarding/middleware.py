from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
from django.conf import settings

try:
    from django.core.cache import cache
except Exception:
    cache = None


class SecurityHeadersMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # HSTS only in production
        if not settings.DEBUG:
            response.setdefault('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload')
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'no-referrer-when-downgrade')
        response.setdefault('X-XSS-Protection', '1; mode=block')
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=()')
        # Basic CSP allowing common CDNs used in this project
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.quilljs.com https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.quilljs.com https://cdn.tailwindcss.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "frame-src 'self' https://www.google.com https://maps.google.com https://www.google.co.ke https://www.google.co.uk; "
            "child-src 'self' https://www.google.com https://maps.google.com https://www.google.co.ke https://www.google.co.uk; "
            "connect-src 'self' https://api.openai.com;"
        )
        response.setdefault('Content-Security-Policy', csp)
        return response


class IpRateLimitMiddleware(MiddlewareMixin):
    """Very small IP-based rate limiter middleware.

    Exempts admin and static/media paths.
    """
    def process_request(self, request):
        try:
            path = request.path
            if path.startswith('/admin/') or path.startswith(settings.STATIC_URL) or path.startswith(settings.MEDIA_URL):
                return None

            if cache is None:
                return None

            ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
            key = f"ip_rl:{ip}"
            count = cache.get(key, 0)
            limit = getattr(settings, 'IP_RATE_LIMIT', 300)  # default 300 req per minute
            if count >= limit:
                return HttpResponse('Too many requests', status=429)
            cache.set(key, count + 1, timeout=60)
        except Exception:
            return None
        return None
