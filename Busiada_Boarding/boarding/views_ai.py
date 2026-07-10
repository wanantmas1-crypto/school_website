"""
AI integration removed.

This placeholder module existed to provide optional OpenAI-powered admin suggestions.
It has been removed for privacy and compliance. If you need automated suggestions later,
re-implement a secure integration with an external service and an explicit opt-in setting.
"""

from django.http import JsonResponse


def admin_suggest(request):
    return JsonResponse({'error': 'AI integration disabled'}, status=410)


def user_chat(request):
    return JsonResponse({'error': 'AI integration disabled'}, status=410)
