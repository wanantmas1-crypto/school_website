from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Inquiry, SitePage, Announcement

def home(request):
    # Try to render an editable SitePage with slug 'home' if present
    try:
        page = SitePage.objects.filter(slug='home').prefetch_related('images').first()
    except Exception:
        page = None

    page_images = list(page.images.all()) if page else []
    hero_background = None

    if page_images:
        hero_background = page_images[0].image.url
    elif page and getattr(page.featured_image, 'name', None):
        hero_background = page.featured_image.url

    return render(
        request,
        'boarding/index.html',
        {
            'page': page,
            'page_images': page_images,
            'hero_background': hero_background,
        },
    )

def about(request):
    page = (
        SitePage.objects
        .filter(slug='about', status='published')
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
        'class="w-full h-[320px] sm:h-[400px] border-0 rounded-2xl" '
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
    page = get_object_or_404(SitePage, slug=slug)
    return render(request, 'boarding/site_page.html', {'page': page})


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