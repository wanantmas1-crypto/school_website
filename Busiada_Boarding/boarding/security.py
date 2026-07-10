import secrets

def generate_csp_nonce(length: int = 16) -> str:
    """Generate a URL-safe nonce for CSP usage."""
    return secrets.token_urlsafe(length)


class CSPNonceMiddleware:
    """Middleware that generates a per-request CSP nonce and stores it on the
    request object for templates and later middleware to use.

    Add this near the top of `MIDDLEWARE` so downstream views/templates can
    access `request.csp_nonce`.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.csp_nonce = generate_csp_nonce()
        response = self.get_response(request)
        return response
