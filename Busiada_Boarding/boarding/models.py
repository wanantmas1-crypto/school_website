from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import os
import hashlib
import time
from .utils import document_upload_to, image_upload_to, video_upload_to

try:
    import bleach
except Exception:
    bleach = None
    
import re

def _basic_sanitize(html):
    # remove script tags
    html = re.sub(r'<script.*?>.*?</script>', '', html, flags=re.I | re.S)
    # remove on* attributes (onclick, onerror, etc.)
    html = re.sub(r'\son\w+\s*=\s*"[^"]*"', '', html, flags=re.I)
    html = re.sub(r"\son\w+\s*=\s*'[^']*'", '', html, flags=re.I)
    # remove javascript: in href/src
    html = re.sub(r'(href|src)\s*=\s*"javascript:[^"]*"', '\1=""', html, flags=re.I)
    html = re.sub(r"(href|src)\s*=\s*'javascript:[^']*'", "\1=''", html, flags=re.I)
    return html

class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    """Simple singleton-like model to store site-wide settings (logo, tagline).

    Upload path: media/branding/<filename>
    Access in templates via context processor as `site_settings`.
    """
    site_name = models.CharField(max_length=200, default='Busiada Girls Senior School')
    tagline = models.CharField(max_length=255, blank=True, default='Unleash Your Potential')
    logo = models.ImageField(upload_to='branding/', blank=True, null=True, help_text='Upload a square logo (PNG/SVG) into media/branding/')
    principal_name = models.CharField(max_length=200, blank=True, default='Principal Name', help_text='Full name of the principal')
    principal_title = models.CharField(max_length=100, blank=True, default='Principal', help_text='Principal title or position')
    principal_message = models.TextField(blank=True, default='', help_text='Rich text content for the principal message section')
    principal_image = models.ImageField(upload_to='principals/', blank=True, null=True, help_text='Upload a principal portrait image (recommended 600x800 px)')

    def __str__(self):
        return 'Site settings'

    def save(self, *args, **kwargs):
        if self.principal_message:
            if bleach:
                allowed_tags = [
                    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'span', 'div',
                    'h1', 'h2', 'h3', 'h4', 'blockquote', 'code', 'pre', 'img', 'figure', 'figcaption'
                ]
                allowed_attrs = {
                    '*': ['class', 'style'],
                    'a': ['href', 'title', 'rel', 'target'],
                    'img': ['src', 'alt', 'width', 'height', 'style'],
                }
                try:
                    self.principal_message = bleach.clean(self.principal_message, tags=allowed_tags, attributes=allowed_attrs, strip=True)
                except Exception:
                    pass
            else:
                try:
                    self.principal_message = _basic_sanitize(self.principal_message)
                except Exception:
                    pass
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Site settings'
        verbose_name_plural = 'Site settings'


class SitePage(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, blank=True, help_text='Optional category or department for this page')
    content = models.TextField()
    # Ordered blocks for flexible page building. Each block is a dict with a `type` and block-specific keys.
    # Example: [{"type": "text", "title": "Intro", "content": "<p>...</p>"}, ...]
    try:
        JSONField = models.JSONField
    except AttributeError:
        # Fallback for very old Django versions (unlikely in this project)
        from django.contrib.postgres.fields import JSONField
        JSONField = JSONField
    sections = JSONField(blank=True, null=True, default=list, help_text='Ordered list of blocks (JSON)')
    featured_image = models.ImageField(upload_to='site_pages/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        # sanitize HTML content if bleach is available
        if bleach and self.content:
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'a', 'span', 'div',
                'h1', 'h2', 'h3', 'h4', 'blockquote', 'code', 'pre'
            ]
            allowed_attrs = {
                '*': ['class', 'style'],
                'a': ['href', 'title', 'rel', 'target'],
            }
            try:
                self.content = bleach.clean(self.content, tags=allowed_tags, attributes=allowed_attrs, strip=True)
            except Exception:
                pass
        elif self.content:
            try:
                self.content = _basic_sanitize(self.content)
            except Exception:
                pass
        super().save(*args, **kwargs)


class PageImage(models.Model):
    page = models.ForeignKey(SitePage, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=image_upload_to)
    title = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.title:
            return f"{self.page.title} - {self.title}"
        return f"Image for {self.page.title}"

    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Page image'
        verbose_name_plural = 'Page images'

    def srcset(self):
        """Return a srcset string for templates (if responsive versions exist)."""
        base_name, _ = os.path.splitext(self.image.name)
        sizes = [320, 640, 1200]
        parts = []
        for w in sizes:
            candidate = f"{base_name}_{w}w.jpg"
            if default_storage.exists(candidate):
                parts.append(f"{default_storage.url(candidate)} {w}w")
        if parts:
            return ', '.join(parts)
        return f"{default_storage.url(self.image.name)} {self.image.width}w" if self.image else ''


class PageVideo(models.Model):
    page = models.ForeignKey(SitePage, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to=video_upload_to)
    title = models.CharField(max_length=200, blank=True)
    caption = models.CharField(max_length=250, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        if self.title:
            return f"{self.page.title} - {self.title}"
        return f"Video for {self.page.title}"

    class Meta:
        ordering = ['order', 'uploaded_at']
        verbose_name = 'Page video'
        verbose_name_plural = 'Page videos'


class Document(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=document_upload_to)
    page = models.ForeignKey(SitePage, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Document'
        verbose_name_plural = 'Documents'

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=100, blank=True, default='General')
    content = models.TextField()
    image = models.ImageField(upload_to='announcements/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    event_date = models.DateTimeField(blank=True, null=True, help_text='Optional countdown date for events')
    is_live_event = models.BooleanField(default=False)
    event_start = models.DateTimeField(blank=True, null=True, help_text='Start time for live events')
    event_end = models.DateTimeField(blank=True, null=True, help_text='End time for live events')
    event_location = models.CharField(max_length=255, blank=True, help_text='Optional location for the event')
    event_link = models.URLField(blank=True, help_text='Optional live event or registration link')
    video_url = models.URLField(blank=True, help_text='Optional video or livestream URL')
    document_link = models.URLField(blank=True, help_text='Optional external document link')
    document_label = models.CharField(max_length=200, blank=True, help_text='Optional label for the document link')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    cta_text = models.CharField(max_length=80, blank=True, help_text='Optional CTA label')
    cta_link = models.URLField(blank=True, help_text='Optional CTA link')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date']

# Signals to generate responsive images after save
from django.db.models.signals import post_save
from django.dispatch import receiver
from .image_utils import generate_responsive_versions


@receiver(post_save, sender=PageImage)
def generate_image_sizes(sender, instance, **kwargs):
    try:
        generate_responsive_versions(instance.image)
    except Exception:
        pass
