import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.text import Truncator

try:
    from django.conf import settings
    OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', None)
except Exception:
    OPENAI_API_KEY = None


@require_POST
@staff_member_required
def admin_suggest(request):
    """Return a simple summary and SEO suggestions for given content.
    If OPENAI_API_KEY is set in settings, this will attempt to call OpenAI (optional).
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        content = payload.get('content', '')
    except Exception:
        content = ''

    # Basic heuristic suggestions
    plain = Truncator(content).chars(800)
    summary = Truncator(plain).words(40, truncate='...') if plain else 'No content provided.'
    seo_title = Truncator(plain).chars(60)
    meta_description = Truncator(plain).chars(160)

    # Placeholder for external AI integration
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            prompt = f"Generate a concise summary (max 40 words), an SEO-friendly title (max 60 chars), and a meta description (max 160 chars) for the following page content:\n\n{plain}"
            resp = openai.Completion.create(
                engine='text-davinci-003',
                prompt=prompt,
                max_tokens=250,
                temperature=0.6,
            )
            ai_text = resp.choices[0].text.strip()
            # naive parse: split by lines
            parts = [p.strip() for p in ai_text.split('\n') if p.strip()]
            if parts:
                summary = parts[0]
                if len(parts) > 1:
                    seo_title = parts[1]
                if len(parts) > 2:
                    meta_description = parts[2]
        except Exception:
            pass

    return JsonResponse({
        'summary': summary,
        'seo_title': seo_title,
        'meta_description': meta_description,
    })


@require_POST
def user_chat(request):
    """A lightweight user chatbot endpoint. Protected by CSRF and simple per-IP rate limiting.

    Returns canned responses unless `OPENAI_API_KEY` is configured in settings.
    """
    try:
        payload = json.loads(request.body.decode('utf-8'))
        message = payload.get('message', '')
    except Exception:
        message = ''

    if not message:
        return JsonResponse({'reply': "I didn't get a message."}, status=400)

    # Simple rate limiting per IP: 10 messages per minute
    try:
        from django.core.cache import cache
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))
        key = f"chat_rate_{ip}"
        count = cache.get(key, 0)
        if count >= 10:
            return JsonResponse({'reply': 'Rate limit exceeded. Please wait a minute.'}, status=429)
        cache.set(key, count + 1, 60)
    except Exception:
        pass

    reply = "I'm here to help — please provide more details about your question."

    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            resp = openai.Completion.create(
                engine='text-davinci-003',
                prompt=f'User: {message}\nAssistant:',
                max_tokens=150,
                temperature=0.7,
            )
            reply = resp.choices[0].text.strip()
        except Exception:
            pass

    return JsonResponse({'reply': reply})
