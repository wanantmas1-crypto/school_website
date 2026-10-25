import os
from html import unescape
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.core.files.storage import default_storage
from django.db.models.functions import Trim
from django.utils import timezone
from django.utils.html import strip_tags
from .models import Inquiry, SitePage, PageVideo, Announcement, HistoryImage, SchoolAnthem, GalleryCategory, Leadership
from .utils import safe_file_url


ACADEMICS_844_RESOURCES = {
    'assignments': {
        'page_slug': '844-assignments',
        'title': 'Assignments',
        'description': 'Assignments and practical tasks for Form 3 and Form 4 learners.',
    },
    'revision-materials': {
        'page_slug': '844-revision-materials',
        'title': 'Revision Materials',
        'description': 'Revision notes, summaries, and study materials for 8-4-4 learners.',
    },
    'past-kcse-papers': {
        'page_slug': '844-past-kcse-papers',
        'title': 'Past KCSE Papers',
        'description': 'Past KCSE examination papers for practice and exam preparation.',
    },
}


def _safe_file_url(field_file):
    return safe_file_url(field_file)


def _page_document_links(page):
    if not page:
        return []

    documents = []
    for document in page.documents.all():
        url = document.external_url or _safe_file_url(document.file)
        if url:
            documents.append({
                'title': document.title,
                'description': document.description,
                'uploaded_at': document.uploaded_at,
                'url': url,
            })
    return documents


def _has_page_content(page):
    if not page:
        return False
    return bool(unescape(strip_tags(page.content or '')).strip())


def _gallery_items_for_page(page):
    return _page_gallery_items(page, include_featured=True)


def _page_gallery_items(page, include_featured):
    items = []
    if not page:
        return items

    if include_featured:
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
                    'category': '',
                    'uploaded_at': getattr(page, 'updated_at', None),
                    'alt': getattr(page, 'title', '') or 'Featured image',
                })
        except Exception:
            pass

    try:
        page_images = getattr(page, 'images', None)
        image_queryset = page_images.select_related('category') if page_images is not None else []
        for img in image_queryset:
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
                'category': img.category.slug if getattr(img, 'category_id', None) else '',
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


STUDENT_LIFE_PAGES = {
    'boarding': {
        'title': 'Home Away from Home: Boarding Life at Busiada',
        'intro': 'A secure, nurturing, and disciplined residential environment designed to foster independence, focus, and deep sisterhood among our girls.',
        'category': 'Boarding Life',
        'cards': [
            {'title': 'Comfort & Security', 'body': '24/7 school security, resident matrons, and spacious, well-ventilated dormitories support every learner’s personal well-being.'},
            {'title': 'Balanced Nutrition', 'body': 'Hygienically prepared, wholesome meals support the health and growth of our learners.'},
            {'title': 'Structured Daily Routine', 'body': 'A balanced timetable brings together morning preparation, classes, co-curricular activities, evening study, and rest.'},
        ],
        'sections': [
            {'title': 'A balanced day', 'items': [
                'Morning Devotions & Prep — 5:00 AM–6:00 AM',
                'Classes & Practical Lessons — 8:00 AM–4:00 PM',
                'Games, Clubs & Co-curriculars — 4:15 PM–5:30 PM',
                'Evening Preps & Personal Study — 6:30 PM–9:30 PM',
                'Lights Out — 10:00 PM',
            ]},
            {'title': 'Parent information', 'items': [
                'Please confirm the essential personal items required for boarders with the school before opening day.',
                'Visiting days and weekend exeats follow the school’s current parent communication and approval policy.',
            ]},
        ],
    },
    'guiding-and-counselling': {
        'title': 'Guidance & Psychological Support',
        'intro': 'Empowering every learner with emotional resilience, personal confidence, moral clarity, and academic mentorship.',
        'category': 'Student Life',
        'cards': [
            {'title': 'CBE Pathway Advisory', 'body': 'Support for learners as they explore strengths and pathways in STEM, Social Sciences, and Arts & Sports Science.'},
            {'title': 'Personal & Emotional Counselling', 'body': 'Individual support for adolescent development, time management, stress, and self-esteem.'},
            {'title': 'Life Skills & Mentorship', 'body': 'Group learning on discipline, financial literacy, digital responsibility, and interpersonal relationships.'},
            {'title': 'Peer Counselling', 'body': 'Student leaders help build positive peer support and a caring dormitory culture.'},
        ],
        'callout': {'title': 'A respectful, private space', 'body': 'Counselling conversations are handled with empathy and privacy, with appropriate support and referrals when needed.'},
    },
    'games-sports': {
        'title': 'Sports & Athletic Excellence',
        'intro': 'Building physical fitness, sportsmanship, resilience, and leadership through active sports engagement.',
        'category': 'Student Life',
        'cards': [
            {'title': 'Ball Games', 'body': 'Basketball, volleyball, football, netball, and handball.'},
            {'title': 'Track & Field', 'body': 'Sprints, middle- and long-distance races, jumps, and throws.'},
            {'title': 'Indoor & Strategic Games', 'body': 'Chess, table tennis, and badminton.'},
        ],
        'sections': [
            {'title': 'CBE Arts & Sports Science pathway', 'body': 'Sport can build a foundation for further learning and careers in coaching, physical education, sports management, and sports journalism.', 'items': []},
            {'title': 'Competition and participation', 'body': 'School teams take part in zonal, county, and regional activities, building teamwork, resilience, and sportsmanship through competition.', 'items': []},
        ],
    },
    'clubs-societies': {
        'title': 'Clubs & Experiential Learning',
        'intro': 'Where passion meets innovation, public speaking, creativity, and community service.',
        'category': 'Student Life',
        'cards': [
            {'title': 'STEM & Innovation', 'body': 'Computer & Coding Club, Science & Robotics Club, and Young Farmers & Environmental Club.'},
            {'title': 'Academic & Debate', 'body': 'Journalism & Media Club, Writers & Debating Society, and French and Kiswahili language clubs.'},
            {'title': 'Leadership & Service', 'body': 'President’s Award Scheme, Girl Guides, Red Cross, St. John Ambulance, and Christian Union / YCS.'},
        ],
        'sections': [
            {'title': 'Community Service Learning', 'body': 'Club projects can help learners apply classroom knowledge through meaningful service. Learners should record activities and hours according to the school’s CBE guidance.', 'items': []},
        ],
    },
    'performing-visual-arts': {
        'title': 'Performing & Visual Arts',
        'intro': 'Celebrating creativity, cultural diversity, and aesthetic expression through music, drama, dance, and fine art.',
        'category': 'Student Life',
        'cards': [
            {'title': 'Music & Dance', 'body': 'Vocal training, instrumental mastery, traditional folk dances, and choral performance.'},
            {'title': 'Theatre & Drama', 'body': 'Scriptwriting, stage acting, solo verses, public speaking, and theatrical production.'},
            {'title': 'Visual Arts & Design', 'body': 'Drawing, painting, sculpture, graphic design, and textile crafting.'},
        ],
        'sections': [
            {'title': 'Festivals & exhibitions', 'body': 'Showcase annual entries, performances, and verified awards from the Kenya National Music Festivals and Kenya Schools and Colleges Drama Festivals.', 'items': []},
            {'title': 'Arts & Sports Science pathway', 'body': 'Creative practice connects with the Arts & Sports Science pathway and supports learners as they develop artistic skills and portfolios.', 'items': []},
        ],
    },
    'student-welfare': {
        'title': 'Student Welfare & Governance',
        'intro': 'Ensuring every learner’s health, safety, rights, and leadership voice are prioritized in a caring environment.',
        'category': 'Student Life',
        'cards': [
            {'title': 'Student Council Governance', 'body': 'A student leadership structure gives learners opportunities to participate constructively in school life.'},
            {'title': 'On-Campus Healthcare', 'body': 'The school sickbay and referral arrangements support learners who need medical attention.'},
            {'title': 'Sanitation & Cleanliness', 'body': 'Hygiene, clean water, and personal care practices help maintain a healthy school environment.'},
            {'title': 'Balanced Dietary Care', 'body': 'Nutritious meal planning supports learners’ energy and wellbeing.'},
            {'title': 'Safety & Anti-Bullying', 'body': 'Learners are encouraged to use open reporting channels. Bullying and unsafe conduct are not tolerated.'},
        ],
    },
}


def _render_student_life_page(request, slug):
    page_data = STUDENT_LIFE_PAGES[slug]
    page, _created = SitePage.objects.get_or_create(
        slug=slug,
        defaults={
            'title': page_data['title'],
            'category': page_data['category'],
            'content': '',
            'status': 'published',
        },
    )
    page = SitePage.objects.prefetch_related('images', 'videos', 'documents').get(pk=page.pk)
    video_items = []
    for video in page.videos.all():
        video_url = video.display_url()
        if video_url:
            video_items.append({
                'src': video_url,
                'external': bool(video.external_url),
                'title': video.title or 'School video',
                'caption': video.caption,
                'description': video.description,
            })

    document_items = []
    for document in page.documents.all():
        document_url = document.display_url()
        if document_url:
            document_items.append({
                'url': document_url,
                'title': document.title,
                'description': document.description,
                'uploaded_at': document.uploaded_at,
            })

    return render(request, 'boarding/student_life_page.html', {
        'page': page,
        'student_life': page_data,
        'featured_image_url': _safe_file_url(page.featured_image),
        'gallery_items': _page_gallery_items(page, include_featured=False),
        'video_items': video_items,
        'document_items': document_items,
    })


def home(request):
    page = (
        SitePage.objects
        .filter(slug='home', status='published')
        .prefetch_related('images', 'videos')
        .first()
    )
    if not page:
        page = (
            SitePage.objects
            .filter(slug='home')
            .prefetch_related('images', 'videos')
            .first()
        )

    page_background_image_url = _safe_file_url(getattr(page, 'background_image', None))
    hero_video = PageVideo.objects.filter(page=page).exclude(video='').first() if page else None
    hero_video_url = _safe_file_url(hero_video.video) if hero_video else ''
    hero_images = []
    if page:
        for image in page.images.all():
            image_url = image.display_url()
            if image_url:
                hero_images.append({
                    'url': image_url,
                    'alt': image.caption or image.title or 'Busiada school',
                })

    # Pass gallery items to the template
    gallery_items = _gallery_items_for_page(page)

    return render(request, 'boarding/index.html', {
        'page': page,
        'page_background_image_url': page_background_image_url,
        'hero_video_url': hero_video_url,
        'hero_images': hero_images,
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
            'image_url': _safe_file_url(getattr(image, 'image', None)),
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

    page_background_image_url = _safe_file_url(getattr(page, 'background_image', None))
    featured_image_url = _safe_file_url(getattr(page, 'featured_image', None))
    featured_images = []
    gallery_images = []
    if featured_image_url:
        featured_images.append({
            'image_url': featured_image_url,
            'title': 'School chaplaincy',
            'caption': '',
        })

    for image in page.images.all():
        image_url = _safe_file_url(getattr(image, 'image', None))
        if image_url:
            image_data = {
                'image_url': image_url,
                'title': image.title,
                'caption': image.caption,
                'description': image.description,
            }
            featured_images.append(image_data)
            gallery_images.append(image_data)

    return render(request, 'boarding/chaplaincy.html', {
        'page': page,
        'page_background_image_url': page_background_image_url,
        'featured_image_url': featured_image_url,
        'featured_images': featured_images,
        'gallery_images': gallery_images,
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
    for resource in ACADEMICS_844_RESOURCES.values():
        SitePage.objects.get_or_create(
            slug=resource['page_slug'],
            defaults={
                'title': resource['title'],
                'category': '8-4-4 Learning Resources',
                'content': '',
                'status': 'published',
            },
        )

    context = {
        'title': '8-4-4 Curriculum',
        'content': (
            '<h2 class="text-2xl font-bold mb-4">8-4-4 Curriculum</h2>'
            '<p>This page provides an overview of the 8-4-4 curriculum. Update content in the template or through Django Admin.</p>'
        ),
    }
    return render(request, 'boarding/academics_844.html', context)


def academics_844_resource(request, slug):
    resource = ACADEMICS_844_RESOURCES.get(slug)
    if resource is None:
        raise Http404('8-4-4 resource not found')

    page, _created = SitePage.objects.get_or_create(
        slug=resource['page_slug'],
        defaults={
            'title': resource['title'],
            'category': '8-4-4 Learning Resources',
            'content': '',
            'status': 'published',
        },
    )
    downloads = []
    for document in page.documents.all():
        url = document.display_url()
        if url:
            downloads.append({'document': document, 'url': url})
    return render(request, 'boarding/academics_844_resource.html', {
        'page': page,
        'resource': resource,
        'downloads': downloads,
    })


def academics_26333(request):
    page, _created = SitePage.objects.get_or_create(
        slug='academics-2-6-3-3-3',
        defaults={
            'title': 'Senior School: 2-6-3-3-3 Curriculum',
            'category': 'Academics',
            'content': '',
            'status': 'published',
        },
    )
    page = SitePage.objects.prefetch_related('images').get(pk=page.pk)

    pathway_images = {
        'stem': [],
        'social_sciences': [],
        'arts_sports': [],
    }
    for image in page.images.all():
        image_title = (image.title or '').strip().casefold()
        image_key = (
            'stem'
            if image_title in {'stem', 'stem laboratory', 'computer lab'}
            else 'social_sciences'
            if image_title in {'social sciences', 'social science'}
            else 'arts_sports'
            if image_title in {'arts & sports science', 'arts and sports science', 'arts & sports', 'arts and sports'}
            else None
        )
        if image_key:
            image_url = image.display_url()
            if image_url:
                pathway_images[image_key].append({
                    'url': image_url,
                    'alt': image.caption or image.title or 'Pathway image',
                })

    context = {
        'title': '2-6-3-3-3 Curriculum',
        'page': page,
        'pathway_images': pathway_images,
        'page_background_image_url': _safe_file_url(getattr(page, 'background_image', None)),
        'content': (
            '<h2 class="text-2xl font-bold mb-4">2-6-3-3-3 Curriculum</h2>'
            '<p>This page provides an overview of the 2-6-3-3-3 curriculum. Update content in the template or through Django Admin.</p>'
        ),
    }
    return render(request, 'boarding/academics_2-6-3-3-3.html', context)


def boarding_page(request):
    return _render_student_life_page(request, 'boarding')

def student_health(request):
    return render(request, 'boarding/student_health.html', {
        'page_title': 'Student Health',
        'page_subtitle': 'Learner wellbeing and health support',
    })


def performing_visual_arts(request):
    return _render_student_life_page(request, 'performing-visual-arts')


def site_page(request, slug):
    if slug in STUDENT_LIFE_PAGES:
        return _render_student_life_page(request, slug)

    if slug == 'school-gallery':
        page, _created = SitePage.objects.get_or_create(
            slug=slug,
            defaults={
                'title': 'Busiada in Pictures',
                'category': 'Student Life',
                'content': '',
                'status': 'published',
            },
        )
        page = SitePage.objects.prefetch_related('images').get(pk=page.pk)
        return render(request, 'boarding/school_gallery.html', {
            'page': page,
            'gallery_items': _page_gallery_items(page, include_featured=False),
            'gallery_categories': GalleryCategory.objects.all(),
        })

    page = SitePage.objects.filter(slug=slug).prefetch_related('images', 'videos', 'documents').first()
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
    return render(request, 'boarding/fee_payment.html', {'page': page})



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
            'key': 'whatsapp',
            'label': 'WhatsApp',
            'value': 'WhatsApp contact details are not available yet.',
            'description': 'For quick updates or urgent inquiries, email the school office for assistance.',
            'icon': 'fa-brands fa-whatsapp',
            'accent': '#10b981',
            'accent_bg': 'rgba(16, 185, 129, 0.14)',
            'accent_border': 'rgba(16, 185, 129, 0.22)',
            'action_label': 'Email the office',
            'action_href': 'mailto:info@busiadagirls.ac.ke',
            'value_href': '',
        },
        {
            'key': 'phone',
            'label': 'Phone',
            'value': 'Phone contact details are not available yet.',
            'description': 'For direct-call assistance, email the school office and we will direct your inquiry.',
            'icon': 'fa-solid fa-phone',
            'accent': '#3b82f6',
            'accent_bg': 'rgba(59, 130, 246, 0.14)',
            'accent_border': 'rgba(59, 130, 246, 0.22)',
            'action_label': 'Email the office',
            'action_href': 'mailto:info@busiadagirls.ac.ke',
            'value_href': '',
        },
        {
            'key': 'email',
            'label': 'Email',
            'value': 'info@busiadagirls.ac.ke',
            'description': 'Send formal communication or admissions requests.',
            'icon': 'fa-solid fa-envelope',
            'accent': '#f97316',
            'accent_bg': 'rgba(249, 115, 22, 0.14)',
            'accent_border': 'rgba(249, 115, 22, 0.22)',
            'action_label': 'Write to us',
            'action_href': 'mailto:info@busiadagirls.ac.ke',
            'value_href': 'mailto:info@busiadagirls.ac.ke',
        },
        {
            'key': 'address',
            'label': 'Postal Address',
            'value': 'P.O. Box 35-50404, Bumala, Busia County, Kenya',
            'description': 'Mail letters or official documents to the school office.',
            'icon': 'fa-solid fa-map-marker-alt',
            'accent': '#ef4444',
            'accent_bg': 'rgba(239, 68, 68, 0.14)',
            'accent_border': 'rgba(239, 68, 68, 0.22)',
            'action_label': 'View location',
            'action_href': 'https://www.google.com/maps/search/?api=1&query=Busiada+Girls+High+School+Bumala+Busia+Kenya',
            'value_href': '',
        },
    ]

    return render(request, 'boarding/contact_page.html', {'page': page, 'contact_details': contact_details})


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
    return render(request, 'boarding/strategic_plan.html', {
        'page': page,
        'page_has_content': _has_page_content(page),
        'page_documents': _page_document_links(page),
    })


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
    return render(request, 'boarding/service_charter.html', {
        'page': page,
        'page_has_content': _has_page_content(page),
        'page_documents': _page_document_links(page),
    })


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
    anthem = SchoolAnthem.objects.order_by('-updated_at').first()
    if anthem is None:
        anthem = SchoolAnthem(title='School Anthem')
    return render(request, 'boarding/school_anthem.html', {
        'page': page,
        'anthem': anthem,
    })


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
    section_config = [
        {
            'key': 'board',
            'title': 'Board of Management',
            'label': 'Governance',
            'description': 'Provides strategic leadership, oversight, and institutional accountability.',
            'icon': 'building',
        },
        {
            'key': 'principal',
            'title': 'Principal',
            'label': 'Executive leadership',
            'description': 'Provides visionary leadership and oversees daily school operations.',
            'icon': 'leader',
        },
        {
            'key': 'deputy',
            'title': 'Deputy Principals',
            'label': 'Organisation',
            'description': 'Coordinate school administration, academic programmes, and institutional leadership.',
            'icon': 'organisation',
            'categories': ['deputy-academic', 'deputy-admin'],
        },
        {
            'key': 'senior-master',
            'title': 'Senior Masters',
            'label': 'Academic coordination',
            'description': 'Support academic coordination, learner guidance, and daily school operations.',
            'icon': 'books',
        },
        {
            'key': 'boarding-masters',
            'title': 'Boarding Masters',
            'label': 'Residential life',
            'description': 'Oversee hostel routines, student welfare, and a supportive residential environment.',
            'icon': 'home',
        },
        {
            'key': 'department-heads',
            'title': 'Academic Leadership',
            'label': 'Teaching & learning',
            'description': 'Lead departments and support quality teaching, learning, and curriculum delivery.',
            'icon': 'books',
        },
        {
            'key': 'student-leaders',
            'title': 'Student Leaders',
            'label': 'Student representation',
            'description': 'Represent learners and strengthen communication, teamwork, and student participation.',
            'icon': 'people',
        },
        {
            'key': 'additional-leadership',
            'title': 'Additional Leadership',
            'label': 'Coordination',
            'description': 'Provide focused coordination and support across the school community.',
            'icon': 'coordination',
        },
    ]
    active_leaders = Leadership.objects.filter(is_active=True).order_by(
        'role_category', 'order', 'name'
    )
    for leader in active_leaders:
        leader.portrait_url = _safe_file_url(leader.portrait)

    leaders_by_category = {}
    for leader in active_leaders:
        leaders_by_category.setdefault(leader.role_category, []).append(leader)

    sections = []
    for config in section_config:
        category_keys = config.get('categories', [config['key']])
        members = [
            leader
            for category_key in category_keys
            for leader in leaders_by_category.get(category_key, [])
        ]
        sections.append({**config, 'members': members})

    return render(request, 'boarding/school_leadership.html', {
        'page': page,
        'leadership_sections': sections,
    })


def announcements(request):
    published_announcements = (
        Announcement.objects.filter(is_active=True)
        .annotate(trimmed_content=Trim('content'))
        .exclude(trimmed_content='')
        .order_by('-date', '-pk')
    )

    category_names = {}
    for value in published_announcements.order_by().values_list('category', flat=True).distinct():
        name = value.strip() or 'General'
        category_names.setdefault(name.casefold(), name)
    categories = sorted(category_names.values(), key=str.casefold)

    featured_announcement = (
        published_announcements.filter(is_featured=True).first()
        or published_announcements.first()
    )
    upcoming_events = published_announcements.filter(
        event_date__gt=timezone.now()
    ).order_by('event_date', '-date')[:4]

    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        if selected_category.casefold() not in category_names:
            selected_category = ''
        elif selected_category.casefold() == 'general':
            published_announcements = published_announcements.filter(
                Q(category__iexact='general') | Q(category='')
            )
        else:
            published_announcements = published_announcements.filter(
                category__iexact=category_names[selected_category.casefold()]
            )

    search_query = request.GET.get('q', '').strip()
    if search_query:
        published_announcements = published_announcements.filter(
            Q(title__icontains=search_query)
            | Q(subtitle__icontains=search_query)
            | Q(content__icontains=search_query)
        )

    has_separate_featured = bool(
        featured_announcement
        and not selected_category
        and not search_query
        and published_announcements.count() > 1
    )
    show_featured = has_separate_featured and request.GET.get('page', '1') == '1'
    if has_separate_featured:
        published_announcements = published_announcements.exclude(
            pk=featured_announcement.pk
        )

    page_obj = Paginator(published_announcements, 9).get_page(request.GET.get('page'))
    pagination_params = request.GET.copy()
    pagination_params.pop('page', None)
    for announcement in page_obj.object_list:
        announcement.safe_image_url = _safe_file_url(getattr(announcement, 'image', None))
    if featured_announcement:
        featured_announcement.safe_image_url = _safe_file_url(
            getattr(featured_announcement, 'image', None)
        )

    return render(request, 'boarding/announcements.html', {
        'announcements': page_obj.object_list,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'featured_announcement': featured_announcement,
        'show_featured': show_featured,
        'upcoming_events': upcoming_events,
        'has_filters': bool(categories and len(categories) > 1),
        'pagination_query': pagination_params.urlencode(),
    })


def announcement_detail(request, pk):
    announcement = get_object_or_404(
        Announcement.objects.filter(is_active=True)
        .annotate(trimmed_content=Trim('content'))
        .exclude(trimmed_content=''),
        pk=pk,
    )
    announcement.safe_image_url = _safe_file_url(getattr(announcement, 'image', None))
    return render(request, 'boarding/announcement_detail.html', {
        'announcement': announcement,
    })