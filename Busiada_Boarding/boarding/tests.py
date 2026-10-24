import os
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Announcement, Document, HistoryImage, PageImage, PageVideo, SitePage, SiteSettings


TEST_MEDIA_ROOT = tempfile.mkdtemp()


class AnnouncementAdminFieldsTests(TestCase):
    def test_announcement_accepts_media_live_event_and_external_links(self):
        announcement = Announcement.objects.create(
            title='Open Day Live Stream',
            subtitle='Watch the event online',
            content='Join the live session.',
            video_url='https://www.youtube.com/watch?v=example',
            is_live_event=True,
            event_start='2026-06-20T10:00:00Z',
            event_end='2026-06-20T12:00:00Z',
            event_location='Main Hall',
            event_link='https://example.org/live',
            document_link='https://example.org/handbook.pdf',
            document_label='Student Handbook',
        )

        saved = Announcement.objects.get(pk=announcement.pk)

        self.assertEqual(saved.video_url, 'https://www.youtube.com/watch?v=example')
        self.assertTrue(saved.is_live_event)
        self.assertEqual(saved.event_location, 'Main Hall')
        self.assertEqual(saved.event_link, 'https://example.org/live')
        self.assertEqual(saved.document_link, 'https://example.org/handbook.pdf')
        self.assertEqual(saved.document_label, 'Student Handbook')


class PublicPagesTests(TestCase):
    def test_admission_process_page_renders_updated_steps_and_help_contact(self):
        SitePage.objects.create(
            slug='admission-process',
            title='Admission Process',
            category='Admissions',
            content='',
            status='published',
        )

        response = self.client.get('/page/admission-process/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Complete Grade 9')
        self.assertContains(response, 'Your child finishes Junior School and sits for the KJSEA examination.')
        self.assertContains(response, 'https://www.knec.ac.ke')
        self.assertContains(response, 'Select Pathway and Schools')
        self.assertContains(response, 'Together with teachers, choose one pathway, subject combination, and eight senior schools.')
        self.assertContains(response, 'The Junior School submits the choices through the official portal:')
        self.assertContains(response, 'https://selection-placement.kemis.go.ke')
        self.assertContains(response, 'Ministry Placement')
        self.assertContains(response, 'The Ministry of Education places learners into Senior Schools based on performance and the choices made.')
        self.assertContains(response, 'Check Placement Result')
        self.assertContains(response, 'https://placement.education.go.ke')
        self.assertContains(response, '22263')
        self.assertContains(response, 'Download Admission Letter')
        self.assertContains(response, 'This is the only valid admission letter.')
        self.assertContains(response, 'Report to School')
        self.assertContains(response, 'Complete Admission')
        self.assertContains(response, 'More Official Information')
        self.assertContains(response, 'https://www.education.go.ke')
        self.assertContains(response, 'Placement is done by the Ministry of Education, not by individual schools.')
        self.assertContains(response, 'target="_blank" rel="noopener noreferrer"', html=False)
        self.assertContains(response, 'admission-step-apply')
        self.assertContains(response, 'admission-step-interview')
        self.assertContains(response, 'admission-step-enroll')

    def test_school_chaplaincy_shows_image_placeholders_without_admin_uploads(self):
        SitePage.objects.create(
            slug='school-chaplaincy',
            title='School Chaplaincy',
            status='published',
        )

        response = self.client.get('/school-chaplaincy/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Spiritual care, guidance, and pastoral support for every girl at Busiada.')
        self.assertContains(response, 'No featured chaplaincy image uploaded')
        self.assertContains(response, 'No chaplaincy gallery photos uploaded')
        self.assertNotContains(response, 'chaplaincy-slide')

    @patch(
        'boarding.views._safe_file_url',
        side_effect=lambda file_field: {
            'site_pages/chaplaincy-background.jpg': '/media/site_pages/chaplaincy-background.jpg',
            'site_pages/chaplaincy-featured.jpg': '/media/site_pages/chaplaincy-featured.jpg',
            'pages/chaplaincy-gallery.jpg': '/media/pages/chaplaincy-gallery.jpg',
        }.get(getattr(file_field, 'name', ''), ''),
    )
    def test_school_chaplaincy_uses_uploaded_page_images(self, _safe_file_url):
        page = SitePage.objects.create(
            slug='school-chaplaincy',
            title='School Chaplaincy',
            status='published',
            background_image='site_pages/chaplaincy-background.jpg',
            featured_image='site_pages/chaplaincy-featured.jpg',
        )
        PageImage.objects.create(
            page=page,
            image='pages/chaplaincy-gallery.jpg',
            title='Chapel gathering',
            caption='A moment of fellowship',
        )

        response = self.client.get('/school-chaplaincy/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/media/site_pages/chaplaincy-background.jpg')
        self.assertContains(response, '/media/site_pages/chaplaincy-featured.jpg')
        self.assertContains(response, '/media/pages/chaplaincy-gallery.jpg')
        self.assertContains(response, 'A moment of fellowship')
        self.assertContains(response, 'background: rgba(30, 58, 95, .52)')
    def test_history_page_renders_supplied_milestones_when_no_admin_entries(self):
        response = self.client.get('/history/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our History')
        self.assertContains(response, 'Founding Years')
        self.assertContains(response, 'Growth &amp; Development')
        self.assertContains(response, 'Rise in Academic Performance')
        self.assertContains(response, 'C2 Senior School')
        self.assertContains(response, 'Meet Our Leadership')
        self.assertNotContains(response, 'Content will be uploaded soon')

    @patch(
        'boarding.views._safe_file_url',
        side_effect=lambda file_field: (
            '/media/history/milestone.jpg'
            if getattr(file_field, 'name', '') == 'history/milestone.jpg'
            else ''
        ),
    )
    def test_history_page_renders_uploaded_milestones(self, _safe_file_url):
        HistoryImage.objects.create(
            year='1985',
            title='A school milestone',
            description='A milestone shared by the school community.',
            image='history/milestone.jpg',
        )

        response = self.client.get('/history/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '1985')
        self.assertContains(response, 'A school milestone')
        self.assertContains(response, 'A milestone shared by the school community.')
        self.assertContains(response, '/media/history/milestone.jpg')
        self.assertNotContains(response, 'Founding Years')

    def test_home_page_renders_successfully(self):
        page = SitePage.objects.create(
            slug='home',
            title='Home',
            content='<p>Welcome to the homepage.</p>',
            status='published',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.title)
        self.assertContains(response, 'Welcome to the homepage.')

    def test_home_page_displays_services_we_offer_section(self):
        SitePage.objects.create(
            slug='home',
            title='Home',
            content='<p>Welcome to the homepage.</p>',
            status='published',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Services We Offer')
        self.assertContains(response, 'Academics')
        self.assertContains(response, 'Co-Curricular & Talent Development')
        self.assertContains(response, 'Learner Support Services')
        self.assertContains(response, 'Parental & Stakeholder Engagement')
        self.assertContains(response, 'Additional Value-Added Services')
        self.assertContains(response, '/student-health/')
        self.assertContains(response, '/page/guiding-and-counselling/')

    def test_home_page_features_modern_ctas_and_contact_bar(self):
        SitePage.objects.create(
            slug='home',
            title='Home',
            content='<p>Welcome to the homepage.</p>',
            status='published',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admission Process')
        self.assertContains(response, 'Our History')
        self.assertContains(response, 'Contact Us')
        self.assertContains(response, 'site-utility-bar')
        self.assertContains(response, 'mailto:info@busiadagirls.ac.ke')

    def test_home_page_uses_cms_identity_and_renders_contact_social_links(self):
        SiteSettings.objects.create(
            site_name='Busiada Girls Senior School',
            tagline='Unleash Your Potential',
            principal_name='CMS Principal',
            principal_title='Principal',
            principal_message='<p>Welcome to our school.</p>',
        )

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Busiada Girls Senior School')
        self.assertContains(response, 'Unleash Your Potential')
        self.assertContains(response, 'CMS Principal')
        self.assertContains(response, 'Welcome to our school.')
        self.assertContains(response, 'href="/contact/"')
        self.assertContains(response, 'View Announcements')
        self.assertContains(response, 'Principal portrait placeholder')
        self.assertContains(response, 'home-map-frame')
        self.assertContains(response, 'Busiada, Kenya')
        self.assertContains(response, 'P.O. Box 35-50404, Bumala, Busia County, Kenya')
        self.assertContains(response, '<svg', html=False)
        for social_url in (
            'https://www.tiktok.com/',
            'https://www.facebook.com/',
            'https://www.instagram.com/',
            'https://x.com/',
        ):
            self.assertContains(response, social_url)

        html = response.content.decode()
        self.assertLess(html.index('class="site-nav'), html.index('class="site-utility-bar'))
        self.assertContains(response, 'tel:+254700000000')

    @patch(
        'boarding.views._safe_file_url',
        side_effect=lambda file_field: (
            '/media/videos/hero.mp4'
            if getattr(file_field, 'name', '') == 'videos/hero.mp4'
            else ''
        ),
    )
    def test_home_page_uses_uploaded_video_as_animated_hero_background(self, _safe_file_url):
        page = SitePage.objects.create(
            slug='home',
            title='Home',
            content='<p>Existing hero content.</p>',
            status='published',
        )
        PageVideo.objects.create(page=page, video='videos/hero.mp4', order=0)

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<video class="hero-background-media" autoplay muted loop playsinline', html=False)
        self.assertContains(response, '<source src="/media/videos/hero.mp4">', html=False)
        self.assertContains(response, 'animation: hero-ken-burns 20s ease-in-out infinite alternate')
        self.assertContains(response, 'rgba(30, 58, 95, 0.52)')
        self.assertContains(response, 'Existing hero content.')

    @patch(
        'boarding.models.safe_file_url',
        side_effect=lambda file_field: {
            'pages/hero-first.jpg': '/media/pages/hero-first.jpg',
            'pages/hero-second.jpg': '/media/pages/hero-second.jpg',
        }.get(getattr(file_field, 'name', ''), ''),
    )
    def test_home_page_uses_ordered_uploaded_images_as_transitioning_hero(self, _safe_file_url):
        page = SitePage.objects.create(
            slug='home',
            title='Home',
            content='<p>Homepage with image slideshow.</p>',
            status='published',
        )
        PageImage.objects.create(
            page=page,
            title='Second image',
            image='pages/hero-second.jpg',
            order=2,
        )
        PageImage.objects.create(
            page=page,
            title='First image',
            image='pages/hero-first.jpg',
            order=1,
        )

        response = self.client.get('/')
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="hero-background-media hero-background-slide is-active"')
        self.assertLess(html.index('/media/pages/hero-first.jpg'), html.index('/media/pages/hero-second.jpg'))
        self.assertContains(response, 'transition: opacity 1.4s ease-in-out')
        self.assertContains(response, '}, 7000);')
        self.assertContains(response, 'Homepage with image slideshow.')

    def test_about_page_contains_location_map_link(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Location')
        self.assertContains(response, 'Open in Google Maps')

    def test_announcements_page_renders(self):
        response = self.client.get('/announcements/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Announcements')

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, MEDIA_URL='/media/')
    def test_announcements_page_excludes_missing_image_urls(self):
        announcement = Announcement.objects.create(
            title='Broken Image Announcement',
            content='Image is missing.',
            is_active=True,
        )
        announcement.image.name = 'announcements/missing-file.jpg'
        announcement.save()

        response = self.client.get('/announcements/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Broken Image Announcement')
        self.assertNotContains(response, 'announcements/missing-file.jpg')
        self.assertNotContains(response, 'data-lightbox-src="/media/announcements/missing-file.jpg"')
        self.assertNotContains(response, 'src="/media/announcements/missing-file.jpg"')

    @override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT, MEDIA_URL='/media/')
    def test_announcements_page_renders_valid_image_url(self):
        image_content = ContentFile(b'\x47\x49\x46\x38\x39\x61', name='announcement.gif')
        announcement = Announcement.objects.create(
            title='Valid Image Announcement',
            content='Image is present.',
            image=SimpleUploadedFile('announcement.gif', image_content.read(), content_type='image/gif'),
            is_active=True,
        )

        response = self.client.get('/announcements/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Valid Image Announcement')
        self.assertContains(response, '/media/announcements/announcement.gif')

    def test_site_navigation_uses_sticky_header_with_updated_about_links(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'site-nav')
        self.assertContains(response, 'About')
        self.assertContains(response, '/school-anthem/')
        self.assertContains(response, '/school-leadership/')
        self.assertContains(response, '/service-charter/')
        self.assertContains(response, '/strategic-plan/')

    def test_contact_ribbon_shows_admin_configured_phone_and_stays_sticky(self):
        SiteSettings.objects.create()

        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'tel:+254700000000')
        self.assertContains(response, '+254700000000')
        self.assertContains(response, 'position: fixed;')
        self.assertContains(response, 'top: var(--site-nav-height, 5rem);')
        self.assertContains(response, 'z-index: 40;')

    def test_school_leadership_page_enables_reveal_script(self):
        response = self.client.get('/school-leadership/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IntersectionObserver')
        self.assertContains(response, "classList.add('visible')")

    def test_contact_page_renders_clean_contact_card_with_admin_ready_details(self):
        response = self.client.get('/contact/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Contact Us')
        self.assertContains(response, 'Reach the school office')
        self.assertContains(response, 'admissions, general inquiries, and official communication')
        self.assertContains(response, 'WhatsApp')
        self.assertContains(response, 'Phone')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Postal Address')
        self.assertContains(response, 'contact-card')
        self.assertContains(response, 'WhatsApp contact details are not available yet.')
        self.assertContains(response, 'Phone contact details are not available yet.')
        self.assertContains(response, 'mailto:info@busiadagirls.ac.ke')
        self.assertContains(response, 'P.O. Box 35-50404, Bumala, Busia County, Kenya')
        self.assertContains(response, 'Our Location')
        self.assertContains(response, 'https://www.google.com/maps/search/?api=1&amp;query=Busiada+Girls+High+School+Bumala+Busia+Kenya')
        self.assertNotContains(response, '[Enter')
        self.assertNotContains(response, '+254 700 000 000')
        self.assertNotContains(response, 'href="tel:')


class SchoolAnthemTests(TestCase):
    def test_school_anthem_page_renders_with_lyrics_and_audio_placeholder(self):
        from .models import SchoolAnthem

        anthem = SchoolAnthem.objects.create(
            title='Busiada School Anthem',
            lyrics='<p>Verse 1: Rise and shine, Busiada pride...</p><p>Chorus: We are leaders, bright and true...</p>',
        )

        response = self.client.get('/school-anthem/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, anthem.title)
        self.assertContains(response, 'The song that unites every Busiada girl in pride and purpose.')
        self.assertContains(response, 'School Anthem Lyrics')
        self.assertContains(response, 'Verse 1: Rise and shine, Busiada pride...')
        self.assertContains(response, 'Chorus: We are leaders, bright and true...')
        self.assertContains(response, 'The School Anthem is sung with pride during assemblies')
        self.assertContains(response, 'No audio available yet')
        self.assertContains(response, 'The school anthem recording will be available soon. Please check back later.')
        self.assertNotContains(response, '<audio', html=False)

    def test_school_anthem_page_renders_without_an_admin_record(self):
        response = self.client.get('/school-anthem/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'School Anthem')
        self.assertContains(response, 'We rise with pride beneath the Kenyan sun')
        self.assertContains(response, 'No audio available yet')

    def test_school_anthem_audio_player_is_available_without_autoplay(self):
        from .models import SchoolAnthem

        SchoolAnthem.objects.create(
            title='Busiada School Anthem',
            audio_file='anthem/school-anthem.mp3',
        )

        response = self.client.get('/school-anthem/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<audio controls preload="metadata" aria-label="Listen to the Busiada school anthem">',
            html=False,
        )
        self.assertContains(response, 'school-anthem.mp3')
        self.assertNotContains(response, 'autoplay')
        self.assertNotContains(response, 'No audio available yet')


class FeePaymentPageTests(TestCase):
    def assert_fee_payment_content(self, response):
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Fee Payment')
        self.assertContains(response, 'Always use the student’s Admission Number or Student ID as the payment reference.')
        self.assertContains(response, 'M-Pesa Paybill')
        self.assertContains(response, '[Enter School Paybill]')
        self.assertContains(response, 'M-Pesa Till Number')
        self.assertContains(response, '[Enter School Till]')
        self.assertContains(response, 'Bank Deposit / Transfer')
        self.assertContains(response, '[Bank Name]')
        self.assertContains(response, 'Busiada Girls’ High School')
        self.assertContains(response, '[Account Number]')
        self.assertContains(response, 'Cash Payment')
        self.assertContains(response, 'working hours')
        self.assertContains(response, 'official receipt')
        self.assertContains(response, 'Important Instructions for Parents')
        self.assertContains(response, 'M-Pesa confirmation message or bank slip')
        self.assertContains(response, 'href="/contact/"')
        self.assertContains(response, 'Payment values shown in brackets are placeholders.')
        self.assertNotContains(response, 'Multiple Payment Options')
        self.assertNotContains(response, 'processed immediately')

    def test_fee_payment_page_renders_payment_guidance(self):
        response = self.client.get('/fees/')

        self.assert_fee_payment_content(response)

    def test_fee_payment_site_page_renders_the_same_guidance(self):
        SitePage.objects.create(
            slug='fee-payment',
            title='Fee Payment',
            category='Admissions',
            content='<p>Old payment copy should not replace the current instructions.</p>',
            status='published',
        )

        response = self.client.get('/page/fee-payment/')

        self.assert_fee_payment_content(response)
        self.assertNotContains(response, 'Old payment copy should not replace the current instructions.')


class AboutPageDynamicContentTests(TestCase):
    def test_about_page_uses_dynamic_sitepage_content(self):
        page = SitePage.objects.create(
            slug='about',
            title='About Busiada',
            content='<p>Dynamic about content from admin.</p>',
            status='published',
        )

        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.title)
        self.assertContains(response, 'Dynamic about content from admin.')


class SecurityHeadersTests(TestCase):
    def test_about_page_allows_google_maps_iframes_in_csp(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn('frame-src', csp)
        self.assertIn('https://www.google.com', csp)

    def test_csp_allows_google_fonts_and_icon_fonts(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        csp = response.headers.get('Content-Security-Policy', '')
        self.assertIn('https://fonts.googleapis.com', csp)
        self.assertIn('https://fonts.gstatic.com', csp)
        self.assertIn('https://use.fontawesome.com', csp)
        self.assertIn('https://cdn.jsdelivr.net', csp)


class AcademicsPageTests(TestCase):
    def test_academics_844_page_has_landing_and_resource_sections(self):
        response = self.client.get('/academics/8-4-4/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Busiada Girls’ High School')
        self.assertContains(response, 'Outgoing curriculum')
        self.assertContains(response, 'A focused and supportive learning environment for learners completing the 8-4-4 journey.')
        self.assertContains(response, 'Explore Forms')
        self.assertContains(response, 'Revision Resources')
        self.assertContains(response, 'We continue to support our Form 3 and Form 4 learners')
        self.assertContains(response, 'Form 4')
        self.assertContains(response, 'personalised support help every learner perform at her best in KCSE.')
        self.assertContains(response, 'continuous assessment, and early preparation')
        self.assertContains(response, 'Assignments')
        self.assertContains(response, 'Revision Materials')
        self.assertContains(response, 'Past KCSE Papers')
        self.assertContains(response, 'finish strong and step confidently into the next stage of her education.')
        self.assertContains(response, 'href="#forms"')
        self.assertContains(response, 'href="#resources"')

    def test_academics_view_uses_admin_page_when_present(self):
        page = SitePage.objects.create(
            slug='academics',
            title='Academics',
            content='<p>Admin-managed academics content.</p>',
            status='published',
        )

        response = self.client.get('/academics/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.title)
        self.assertContains(response, 'Admin-managed academics content.')

    def test_academics_view_creates_editable_page_if_missing(self):
        SitePage.objects.filter(slug='academics').delete()

        response = self.client.get('/academics/')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(SitePage.objects.filter(slug='academics', status='published').exists())
        self.assertContains(response, 'Academics')

    def test_senior_school_page_hides_empty_pathway_galleries_and_unset_populations(self):
        response = self.client.get('/academics/2-6-3-3-3/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Arts &amp; Sports Science')
        self.assertContains(response, 'Possible Careers')
        self.assertContains(response, 'Why CBE Matters')
        self.assertContains(response, 'What Parents Should Know')
        self.assertContains(response, 'Pathway Choice')
        self.assertContains(response, 'Core Values')
        self.assertNotContains(response, 'STEM pathway images')
        self.assertNotContains(response, 'Social Sciences pathway images')
        self.assertNotContains(response, 'Arts and Sports Science pathway images')
        self.assertNotContains(response, 'learners</p>')
        self.assertTrue(SitePage.objects.filter(slug='academics-2-6-3-3-3').exists())

    @patch(
        'boarding.models.safe_file_url',
        side_effect=lambda file_field: {
            'pages/stem-laboratory.jpg': '/media/pages/stem-laboratory.jpg',
            'pages/computer-lab.jpg': '/media/pages/computer-lab.jpg',
            'pages/stem-event.jpg': '/media/pages/stem-event.jpg',
            'pages/social-sciences.jpg': '/media/pages/social-sciences.jpg',
            'pages/arts-sports.jpg': '/media/pages/arts-sports.jpg',
        }.get(getattr(file_field, 'name', ''), ''),
    )
    def test_senior_school_page_uses_admin_images_and_pathway_populations(self, _safe_file_url):
        page = SitePage.objects.create(
            slug='academics-2-6-3-3-3',
            title='Senior School',
            stem_learner_population=28,
            social_sciences_learner_population=34,
            status='published',
        )
        PageImage.objects.create(
            page=page,
            title='STEM Laboratory',
            image='pages/stem-laboratory.jpg',
        )
        PageImage.objects.create(
            page=page,
            title='Computer Lab',
            image='pages/computer-lab.jpg',
        )
        PageImage.objects.create(
            page=page,
            title='STEM',
            image='pages/stem-event.jpg',
            order=1,
        )
        PageImage.objects.create(
            page=page,
            title='Social Sciences',
            image='pages/social-sciences.jpg',
        )
        PageImage.objects.create(
            page=page,
            title='Arts & Sports Science',
            image='pages/arts-sports.jpg',
        )

        response = self.client.get('/academics/2-6-3-3-3/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/media/pages/stem-laboratory.jpg')
        self.assertContains(response, '/media/pages/computer-lab.jpg')
        self.assertContains(response, '/media/pages/stem-event.jpg')
        self.assertContains(response, '/media/pages/social-sciences.jpg')
        self.assertContains(response, '/media/pages/arts-sports.jpg')
        self.assertContains(response, '28 learners')
        self.assertContains(response, '34 learners')
        self.assertNotContains(response, 'Upload via Admin')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class DynamicPageImageSourceTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_dynamic_page_uses_announcement_style_hero_and_gallery_structure(self):
        page = SitePage.objects.create(
            slug='announcement-style-page',
            title='Announcement Style Page',
            content='<p>Dynamic content.</p>',
            featured_image=self.uploaded_image('hero.jpg'),
            status='published',
        )
        PageImage.objects.create(
            page=page,
            title='Gallery image',
            image=self.uploaded_image('gallery.jpg'),
        )

        response = self.client.get('/page/announcement-style-page/')
        body = response.content.decode('utf-8', errors='ignore')

        self.assertEqual(response.status_code, 200)
        self.assertIn('dynamic-hero-figure', body)
        self.assertIn('dynamic-gallery', body)
        self.assertIn('<figcaption', body)

    def uploaded_image(self, name):
        return SimpleUploadedFile(name, b'image-bytes', content_type='image/jpeg')

    def test_dynamic_page_uses_its_own_featured_image(self):
        other = SitePage.objects.create(
            slug='other-page',
            title='Other Page',
            content='<p>Other content.</p>',
            featured_image=self.uploaded_image('other-feature.jpg'),
            status='published',
        )
        page = SitePage.objects.create(
            slug='student-welfare',
            title='Student Welfare',
            content='<p>Student welfare content.</p>',
            featured_image=self.uploaded_image('welfare-feature.jpg'),
            status='published',
        )

        response = self.client.get('/page/student-welfare/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page.featured_image.url)
        self.assertNotContains(response, other.featured_image.url)

    def test_dynamic_gallery_uses_images_from_current_page_only(self):
        other_page = SitePage.objects.create(
            slug='games-sports',
            title='Games and Sports',
            content='<p>Other content.</p>',
            status='published',
        )
        page = SitePage.objects.create(
            slug='clubs-societies',
            title='Clubs and Societies',
            content='<p>Clubs content.</p>',
            status='published',
        )
        other_image = PageImage.objects.create(
            page=other_page,
            title='Other gallery image',
            image=self.uploaded_image('other-gallery.jpg'),
        )
        page_image = PageImage.objects.create(
            page=page,
            title='Page gallery image',
            image=self.uploaded_image('clubs-gallery.jpg'),
        )

        response = self.client.get('/page/clubs-societies/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, page_image.image.url)
        self.assertNotContains(response, other_image.image.url)

    def test_dynamic_gallery_omits_missing_local_image_file(self):
        page = SitePage.objects.create(
            slug='games-sports',
            title='Games and Sports',
            content='<p>Sports content.</p>',
            status='published',
        )
        page_image = PageImage.objects.create(
            page=page,
            title='Rugby',
            image='site_pages/rugby.jpg',
        )

        response = self.client.get('/page/games-sports/')

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, page_image.image.url)

    def test_dynamic_gallery_resolves_legacy_upload_folder_by_filename(self):
        default_storage.save(
            'boarding.utils.image_upload_to/legacy-sports.jpg',
            ContentFile(b'image-bytes'),
        )
        page = SitePage.objects.create(
            slug='legacy-sports',
            title='Legacy Sports',
            content='<p>Legacy sports content.</p>',
            status='published',
        )
        PageImage.objects.create(
            page=page,
            title='Legacy sports image',
            image='site_pages/legacy-sports.jpg',
        )

        response = self.client.get('/page/legacy-sports/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/media/boarding.utils.image_upload_to/legacy-sports.jpg')
        self.assertNotContains(response, '/media/site_pages/legacy-sports.jpg')

    def test_dynamic_page_renders_uploaded_videos(self):
        page = SitePage.objects.create(
            slug='video-page',
            title='Video Page',
            content='<p>Video content.</p>',
            status='published',
        )
        PageVideo.objects.create(
            page=page,
            title='Campus Tour',
            video=self.uploaded_image('campus-tour.mp4'),
        )

        response = self.client.get('/page/video-page/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Campus Tour')
        self.assertContains(response, '/media/')
        self.assertContains(response, 'video')

    def test_dynamic_page_renders_media_sections_in_image_video_download_order(self):
        page = SitePage.objects.create(
            slug='media-order',
            title='Media Order',
            content='<p>Media ordering content.</p>',
            status='published',
        )
        PageImage.objects.create(
            page=page,
            title='Gallery image',
            image=self.uploaded_image('gallery.jpg'),
        )
        PageVideo.objects.create(
            page=page,
            title='Campus Tour',
            video=self.uploaded_image('campus-tour.mp4'),
        )
        Document.objects.create(
            page=page,
            title='School Handbook',
            file=self.uploaded_image('handbook.pdf'),
        )

        response = self.client.get('/page/media-order/')
        body = response.content.decode('utf-8', errors='ignore')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body.count('<section class="dynamic-gallery'), 1)
        self.assertLess(body.find('Gallery'), body.find('Videos'))
        self.assertLess(body.find('Videos'), body.find('Downloads'))

    def test_boarding_route_uses_boarding_admin_page_image(self):
        page = SitePage.objects.create(
            slug='boarding',
            title='Boarding Life',
            content='<p>Admin-managed boarding content.</p>',
            featured_image=self.uploaded_image('boarding-feature.jpg'),
            status='published',
        )

        response = self.client.get('/boarding/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin-managed boarding content.')
        self.assertContains(response, page.featured_image.url)
