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
        # Basic security headers
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('Referrer-Policy', 'no-referrer-when-downgrade')
        response.setdefault('X-XSS-Protection', '1; mode=block')
        response.setdefault('Permissions-Policy', 'geolocation=(), microphone=()')
        # X-Frame-Options from settings (default DENY)
        try:
            xframe = getattr(settings, 'X_FRAME_OPTIONS', 'DENY')
            response.setdefault('X-Frame-Options', xframe)
        except Exception:
            response.setdefault('X-Frame-Options', 'DENY')
        # Build CSP from project settings so source lists stay consistent.
        script_src = ' '.join(settings.CSP_SCRIPT_SRC)
        style_src = ' '.join(settings.CSP_STYLE_SRC)
        font_src = ' '.join(settings.CSP_FONT_SRC)
        # Restrict connect-src to self and known APIs if configured
        connect_src_list = getattr(settings, 'CSP_CONNECT_SRC', ("'self'",))
        connect_src = ' '.join(connect_src_list)
        csp = (
            "default-src 'self'; "
            f"script-src {script_src}; "
            f"style-src {style_src}; "
            f"font-src {font_src}; "
            "img-src 'self' data: https:; "
            "frame-src 'self' https://www.google.com https://maps.google.com https://www.google.co.ke https://www.google.co.uk; "
            "child-src 'self' https://www.google.com https://maps.google.com https://www.google.co.ke https://www.google.co.uk; "
            f"connect-src {connect_src};"
        )
        response.setdefault('Content-Security-Policy', csp)
        # Apply XSS and content type protections from settings
        try:
            if getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False):
                response.setdefault('X-XSS-Protection', '1; mode=block')
            if getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False):
                response.setdefault('X-Content-Type-Options', 'nosniff')
        except Exception:
            pass
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
