import shutil
import tempfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from .models import Announcement, Document, PageImage, PageVideo, SitePage


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
        self.assertContains(response, 'Apply Now')
        self.assertContains(response, 'Explore Campus')
        self.assertContains(response, 'site-utility-bar')
        self.assertContains(response, 'WhatsApp')

    def test_about_page_contains_location_map_link(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Location')
        self.assertContains(response, 'Open in Google Maps')

    def test_announcements_page_renders(self):
        response = self.client.get('/announcements/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Announcements')

    def test_site_navigation_uses_sticky_header_with_updated_about_links(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'site-nav')
        self.assertContains(response, 'About')
        self.assertContains(response, '/school-anthem/')
        self.assertContains(response, '/school-leadership/')
        self.assertContains(response, '/service-charter/')
        self.assertContains(response, '/strategic-plan/')

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
        self.assertContains(response, 'WhatsApp')
        self.assertContains(response, 'Phone')
        self.assertContains(response, 'Email')
        self.assertContains(response, 'Postal Address')
        self.assertContains(response, 'contact-item')


class SchoolAnthemTests(TestCase):
    def test_school_anthem_page_renders_with_lyrics_and_audio_placeholder(self):
        from .models import SchoolAnthem
        
        # Create a school anthem entry
        anthem = SchoolAnthem.objects.create(
            title='Busiada School Anthem',
            lyrics='<p>Verse 1: Rise and shine, Busiada pride...</p><p>Chorus: We are leaders, bright and true...</p>',
        )

        response = self.client.get('/school-anthem/')

        self.assertEqual(response.status_code, 200)
        # Check for content that's definitely in the template
        self.assertContains(response, 'Our Pride')
        self.assertContains(response, 'Celebrating our heritage and unity')


class FeePaymentPageTests(TestCase):
    def test_fee_payment_page_renders_with_payment_methods_grid(self):
        response = self.client.get('/fees/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Multiple Payment Options')
        self.assertContains(response, 'Paybill Number')
        self.assertContains(response, 'Till Number')
        self.assertContains(response, 'Bank Account')
        self.assertContains(response, 'Postal Address')
        self.assertContains(response, 'Payment Instructions')
        self.assertContains(response, 'payment-card')


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
        self.assertContains(response, 'Busiada Girls High School')
        self.assertContains(response, 'Explore Forms')
        self.assertContains(response, 'Resources')
        self.assertContains(response, 'Form 4')
        self.assertContains(response, 'Past KCSE Questions')

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
