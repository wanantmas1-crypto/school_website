from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Inquiry, SitePage, Announcement

def home(request):
    """Render the clean new homepage."""
    return render(request, 'boarding/home_new.html')


def about(request):
    page = (
        SitePage.objects
        .filter(slug='about', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )

    if not page:
        page = (
            SitePage.objects
            .filter(slug='about')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )

    if not page:
        page, _created = SitePage.objects.get_or_create(
            slug='about',
            defaults={
                'title': 'About Busiada Girls Senior School',
                'category': 'About',
                'content': (
                    '<p>Update this page from Django Admin to manage the About page content.</p>'
                    '<p>You can add rich text, images, videos, and documents here.</p>'
                ),
                'status': 'published',
            },
        )

    embed_map = (
        '<iframe src="https://www.google.com/maps?q=Busiada%20Girls%20Senior%20School%20Kenya&z=13&output=embed" '
        'title="Busiada Girls Senior School location" '
        'width="100%" height="320" style="min-height:320px; border:0; border-radius:1rem;" '
        'loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
        'allowfullscreen></iframe>'
    )
    return render(request, 'boarding/about.html', {'page': page, 'embed_map': embed_map})

def admissions(request):
    return render(request, 'boarding/admissions.html')

def academics(request):
    page = (
        SitePage.objects
        .filter(slug='academics', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )

    if not page:
        page = (
            SitePage.objects
            .filter(slug='academics')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )

    if not page:
        page, _created = SitePage.objects.get_or_create(
            slug='academics',
            defaults={
                'title': 'Academics',
                'category': 'Departments',
                'content': (
                    '<p>Update this page from Django Admin to manage the Academics content for the department section.</p>'
                    '<p>You can add rich text, images, videos, and documents here.</p>'
                ),
                'status': 'published',
            },
        )

    return render(request, 'boarding/site_page.html', {'page': page})

def boarding_page(request):
    return render(request, 'boarding/boarding.html')

def site_page(request, slug):
    page = get_object_or_404(
        SitePage.objects.prefetch_related('images', 'videos', 'documents'),
        slug=slug,
    )
    embed_map = None
    if slug == 'location':
        embed_map = (
            '<iframe src="https://www.google.com/maps?q=Busiada%20Girls%20Senior%20School%20Kenya&z=15&output=embed" '
            'title="Busiada Girls Senior School location" '
            'width="100%" height="480" style="min-height:320px; border:0; border-radius:1rem;" '
            'loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            'allowfullscreen></iframe>'
        )
    return render(request, 'boarding/site_page.html', {'page': page, 'embed_map': embed_map})


def submit_inquiry(request):
    if request.method == "POST":
        Inquiry.objects.create(
            name=request.POST.get('name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone', ''),
            message=request.POST.get('message', '')
        )
        if request.headers.get('HX-Request'):
            return HttpResponse('<div class="p-4 bg-emerald-100 text-emerald-700 rounded-2xl text-center">Thank you! Enquiry received.</div>')
    return redirect('home')
def announcements(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'boarding/announcements.html', {'announcements': announcements})