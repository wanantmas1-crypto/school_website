from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Inquiry, SitePage, Announcement

def home(request):
    page = SitePage.objects.filter(slug='home', status='published').first()
    if not page:
        page = SitePage.objects.filter(slug='home').first()

    # Build a list of slides with per-slide delay: prefer featured_image, then page images
    slides = []
    try:
        if page:
            if getattr(page, 'featured_image', None) and getattr(page.featured_image, 'url', None):
                slides.append(page.featured_image.url)
            for img in page.images.all():
                url = getattr(getattr(img, 'image', None), 'url', None)
                if url and url not in slides:
                    slides.append(url)
    except Exception:
        slides = []

    slide_interval = 12
    # Build slides metadata with per-slide delay (seconds)
    slides_meta = []
    for i, url in enumerate(slides):
        slides_meta.append({'url': url, 'delay': i * slide_interval})

    hero_total_duration = max(len(slides) * slide_interval, 12)

    return render(request, 'boarding/index.html', {
        'page': page,
        'slides': slides_meta,
        'slide_interval': slide_interval,
        'hero_total_duration': hero_total_duration,
    })


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


def academics_844(request):
    context = {
        'title': '8-4-4 Curriculum',
        'content': (
            '<h2 class="text-2xl font-bold mb-4">8-4-4 Curriculum</h2>'
            '<p>This page provides an overview of the 8-4-4 curriculum. Update content in the template or through Django Admin.</p>'
        ),
    }
    return render(request, 'boarding/academics_844.html', context)


def academics_26333(request):
    context = {
        'title': '2-6-3-3-3 Curriculum',
        'content': (
            '<h2 class="text-2xl font-bold mb-4">2-6-3-3-3 Curriculum</h2>'
            '<p>This page provides an overview of the 2-6-3-3-3 curriculum. Update content in the template or through Django Admin.</p>'
        ),
    }
    return render(request, 'boarding/academics_26333.html', context)


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