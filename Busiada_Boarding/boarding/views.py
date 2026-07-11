import os
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.files.storage import default_storage
from .models import Inquiry, SitePage, Announcement, HistoryImage


def _safe_file_url(field_file):
    if not field_file:
        return ''

    try:
        if isinstance(field_file, str):
            name = field_file
        else:
            name = getattr(field_file, 'name', '') or ''

        if not name:
            return ''

        candidates = [name]
        basename = os.path.basename(name)
        if basename:
            candidates.extend([
                os.path.join('boarding.utils.image_upload_to', basename),
                os.path.join('site_pages', basename),
            ])

        for candidate in candidates:
            if default_storage.exists(candidate):
                return default_storage.url(candidate)
    except Exception:
        return ''

    return ''


def _gallery_items_for_page(page):
    items = []
    if not page:
        return items

    try:
        featured_image = getattr(page, 'featured_image', None)
        featured_url = _safe_file_url(featured_image)
        if featured_url:
            items.append({
                'src': featured_url,
                'srcset': '',
                'title': getattr(page, 'title', '') or 'Featured image',
                'caption': '',
                'description': '',
                'uploaded_at': getattr(page, 'updated_at', None),
                'alt': getattr(page, 'title', '') or 'Featured image',
            })
    except Exception:
        pass

    try:
        for img in getattr(page, 'images', None).all() if getattr(page, 'images', None) is not None else []:
            url = _safe_file_url(getattr(img, 'image', None))
            if not url:
                continue

            srcset = ''
            try:
                srcset = img.srcset()
            except Exception:
                srcset = ''

            items.append({
                'src': url,
                'srcset': srcset,
                'title': getattr(img, 'title', '') or 'Photo',
                'caption': getattr(img, 'caption', '') or '',
                'description': getattr(img, 'description', '') or '',
                'uploaded_at': getattr(img, 'uploaded_at', None),
                'alt': getattr(img, 'title', '') or getattr(page, 'title', '') or 'Photo',
            })
    except Exception:
        pass

    return items


def _render_dynamic_page(request, page, template_name='boarding/site_page.html', embed_map=None):
    featured_image_url = _safe_file_url(getattr(page, 'featured_image', None))
    featured_image_srcset = ''
    gallery_items = _gallery_items_for_page(page)
    return render(request, template_name, {
        'page': page,
        'embed_map': embed_map,
        'featured_image_url': featured_image_url,
        'featured_image_srcset': featured_image_srcset,
        'gallery_items': gallery_items,
    })


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

    # Pass gallery items to the template
    gallery_items = _gallery_items_for_page(page)
    page_content = getattr(page, 'content', '') or ''

    return render(request, 'boarding/index.html', {
        'page': page,
        'page_content': page_content,
        'slides': slides_meta,
        'slide_interval': slide_interval,
        'hero_total_duration': hero_total_duration,
        'gallery_items': gallery_items,
    })


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
        'width="100%" height="320" style="min-height:320px; border:0; border-radius:1rem;" '
        'loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
        'allowfullscreen></iframe>'
    )
    return _render_dynamic_page(request, page, template_name='boarding/about.html', embed_map=embed_map)


def school_history(request):
    history_images = []
    for i, image in enumerate(HistoryImage.objects.all()):
        history_images.append({
            'object': image,
            'delay': i * 8,
        })

    return render(request, 'boarding/history.html', {
        'history_images': history_images,
    })


def school_chaplaincy(request):
    page = (
        SitePage.objects
        .filter(slug='school-chaplaincy', status='published')
        .prefetch_related('images')
        .first()
    )

    if not page:
        page = (
            SitePage.objects
            .filter(slug='school-chaplaincy')
            .prefetch_related('images')
            .first()
        )

    if not page:
        page, _created = SitePage.objects.get_or_create(
            slug='school-chaplaincy',
            defaults={
                'title': 'School Chaplaincy',
                'category': 'About',
                'content': (
                    '<p>Update this page from Django Admin to manage the School Chaplaincy content, background and images.</p>'
                ),
                'status': 'published',
            },
        )

    images = list(page.images.all())
    section_one_image = images[0] if len(images) > 0 else None
    section_two_image = images[1] if len(images) > 1 else None
    transition_images = images[2:5] or images[:3]

    return render(request, 'boarding/chaplaincy.html', {
        'page': page,
        'section_one_image': section_one_image,
        'section_two_image': section_two_image,
        'transition_images': transition_images,
    })


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

    return _render_dynamic_page(request, page)


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
    return render(request, 'boarding/academics_2-6-3-3-3.html', context)


def boarding_page(request):
    page = (
        SitePage.objects
        .filter(slug='boarding', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )

    if not page:
        page = (
            SitePage.objects
            .filter(slug='boarding')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )

    if not page:
        page, _created = SitePage.objects.get_or_create(
            slug='boarding',
            defaults={
                'title': 'Boarding Life',
                'category': 'Boarding',
                'content': (
                    '<p>Update this page from Django Admin to manage the Boarding page content.</p>'
                    '<p>You can add rich text, images, videos, and documents here.</p>'
                ),
                'status': 'published',
            },
        )

    return _render_dynamic_page(request, page)

STATIC_PAGE_TEMPLATES = {
    'guiding-and-counselling': 'boarding/guiding_and_counselling.html',
    'games-sports': 'boarding/games_sports.html',
    'clubs-societies': 'boarding/clubs_societies.html',
    'student-welfare': 'boarding/student_welfare.html',
    'performing-visual-arts': 'boarding/performing_visual_arts.html',
}


def student_health(request):
    return render(request, 'boarding/student_health.html', {
        'page_title': 'Student Health',
        'page_subtitle': 'Learner wellbeing and health support',
    })


def performing_visual_arts(request):
    return render(request, 'boarding/performing_visual_arts.html', {
        'page_title': 'Performing & Visual Arts',
        'page_subtitle': 'Creativity, expression and cultural growth',
    })


def site_page(request, slug):
    page = SitePage.objects.filter(slug=slug).prefetch_related('images', 'videos', 'documents').first()
    if page is None and slug in STATIC_PAGE_TEMPLATES:
        return render(request, STATIC_PAGE_TEMPLATES[slug], {
            'slug': slug,
            'page_title': slug.replace('-', ' ').title(),
            'page_subtitle': 'Student life and support services',
        })

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
    return _render_dynamic_page(request, page, embed_map=embed_map)


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

def fee_payment(request):
    page = (
        SitePage.objects
        .filter(slug='fee-payment', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='fee-payment')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    
    payment_methods = [
        {
            'title': 'Paybill Number',
            'label': 'Mobile Money',
            'value': '[Enter Paybill here]',
            'description': 'Pay via your mobile money account with secure verification.',
            'icon': 'fa-solid fa-mobile-screen-button',
            'accent': '#0ea5e9',
            'accent_bg': 'rgba(14, 165, 233, 0.14)',
            'accent_border': 'rgba(14, 165, 233, 0.25)',
            'tooltip': 'Copy the Paybill number for mobile payment',
        },
        {
            'title': 'Till Number',
            'label': 'Till/USSD',
            'value': '[Enter Till here]',
            'description': 'Fast payment using a Till number or USSD transfer.',
            'icon': 'fa-solid fa-wallet',
            'accent': '#2563eb',
            'accent_bg': 'rgba(37, 99, 235, 0.14)',
            'accent_border': 'rgba(37, 99, 235, 0.25)',
            'tooltip': 'Copy the Till number for quick payment',
        },
        {
            'title': 'Bank Account',
            'label': 'Bank Transfer',
            'value': '[Enter Bank Name & Account Number here]',
            'description': 'Direct bank transfer using the school account details.',
            'icon': 'fa-solid fa-building-columns',
            'accent': '#4338ca',
            'accent_bg': 'rgba(67, 56, 202, 0.14)',
            'accent_border': 'rgba(67, 56, 202, 0.25)',
            'tooltip': 'Copy bank details for secure transfer',
        },
        {
            'title': 'Postal Address',
            'label': 'Postal/Reference',
            'value': '[Enter Postal Address or Reference here]',
            'description': 'Mail payment or reference documentation to the school address.',
            'icon': 'fa-solid fa-envelope',
            'accent': '#0f766e',
            'accent_bg': 'rgba(15, 118, 110, 0.14)',
            'accent_border': 'rgba(15, 118, 110, 0.25)',
            'tooltip': 'Copy postal reference details for payment',
        },
    ]
    
    return render(request, 'boarding/fee_payment.html', {'page': page, 'payment_methods': payment_methods})



def contact_page(request):
    page = (
        SitePage.objects
        .filter(slug__in=['contact', 'contacts'], status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug__in=['contact', 'contacts'])
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )

    if not page:
        page, _created = SitePage.objects.get_or_create(
            slug='contact',
            defaults={
                'title': 'Contact Us',
                'category': 'Contact',
                'content': '<p>Update this page from Django Admin to manage contact details and location information.</p>',
                'status': 'published',
            },
        )

    contact_details = [
        {
            'label': 'WhatsApp',
            'value': '[Enter WhatsApp Number]',
            'description': 'Reach us quickly for school updates or urgent inquiries.',
            'icon': 'fa-brands fa-whatsapp',
            'accent': '#10b981',
            'accent_bg': 'rgba(16, 185, 129, 0.14)',
            'accent_border': 'rgba(16, 185, 129, 0.22)',
            'badge': 'Chat now',
            'tooltip': 'Click to chat on WhatsApp',
            'href': 'https://wa.me/',
            'clickable': True,
        },
        {
            'label': 'Phone',
            'value': '[Enter Phone Number]',
            'description': 'Use this for direct calls and urgent school matters.',
            'icon': 'fa-solid fa-phone',
            'accent': '#3b82f6',
            'accent_bg': 'rgba(59, 130, 246, 0.14)',
            'accent_border': 'rgba(59, 130, 246, 0.22)',
            'badge': 'Call now',
            'tooltip': 'Call the school office directly',
            'href': 'tel:',
            'clickable': True,
        },
        {
            'label': 'Email',
            'value': '[Enter Email Address]',
            'description': 'Send formal communication or admissions requests.',
            'icon': 'fa-solid fa-envelope',
            'accent': '#f97316',
            'accent_bg': 'rgba(249, 115, 22, 0.14)',
            'accent_border': 'rgba(249, 115, 22, 0.22)',
            'badge': 'Write us',
            'tooltip': 'Send an email to the school office',
            'href': 'mailto:',
            'clickable': True,
        },
        {
            'label': 'Postal Address',
            'value': '[Enter Postal Address]',
            'description': 'Mail letters or official documents to the school office.',
            'icon': 'fa-solid fa-map-marker-alt',
            'accent': '#ef4444',
            'accent_bg': 'rgba(239, 68, 68, 0.14)',
            'accent_border': 'rgba(239, 68, 68, 0.22)',
            'badge': 'Mail us',
            'tooltip': 'Use the school postal address',
            'href': '#',
            'clickable': False,
        },
    ]

    return render(request, 'boarding/contact_page.html', {'page': page, 'contact_details': contact_details})


def school_anthem(request):
    page = (
        SitePage.objects
        .filter(slug='school-anthem', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='school-anthem')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    return render(request, 'boarding/school_anthem.html', {'page': page})


def strategic_plan(request):
    page = (
        SitePage.objects
        .filter(slug='strategic-plan', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='strategic-plan')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    return render(request, 'boarding/strategic_plan.html', {'page': page})


def service_charter(request):
    page = (
        SitePage.objects
        .filter(slug='service-charter', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='service-charter')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    return render(request, 'boarding/service_charter.html', {'page': page})


def school_anthem(request):
    page = (
        SitePage.objects
        .filter(slug='school-anthem', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='school-anthem')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    return render(request, 'boarding/school_anthem.html', {'page': page})


def school_leadership(request):
    page = (
        SitePage.objects
        .filter(slug='school-leadership', status='published')
        .prefetch_related('images', 'videos', 'documents')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='school-leadership')
            .prefetch_related('images', 'videos', 'documents')
            .first()
        )
    return render(request, 'boarding/school_leadership.html', {'page': page})


def announcements(request):
    announcements = Announcement.objects.filter(is_active=True)
    return render(request, 'boarding/announcements.html', {'announcements': announcements})