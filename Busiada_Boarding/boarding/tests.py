from django.test import TestCase

from .models import Announcement, SitePage


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

    def test_about_page_contains_location_map_link(self):
        response = self.client.get('/about/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Our Location')
        self.assertContains(response, 'Open in Google Maps')

    def test_announcements_page_renders(self):
        response = self.client.get('/announcements/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Announcements')


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


class AcademicsPageTests(TestCase):
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
