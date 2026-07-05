"""
Management command to setup test images on multiple pages.

Usage:
    python manage.py setup_page_images --help
    python manage.py setup_page_images --pages home about academics-8-4-4 --delete
    python manage.py setup_page_images --all
"""

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from boarding.models import SitePage, PageImage
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os


class Command(BaseCommand):
    help = 'Setup test images on dynamic pages'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            nargs='+',
            help='Specific page slugs to setup images for'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Setup images for all pages'
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete existing images before adding new ones'
        )

    def create_test_image(self, title, page_title):
        """Create a simple test image with text."""
        # Create image
        img = Image.new('RGB', (800, 600), color='#0A2540')
        draw = ImageDraw.Draw(img)
        
        # Add text
        text = f"{page_title}\nTest Image"
        text_bbox = draw.textbbox((0, 0), text, font=None)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        x = (800 - text_width) // 2
        y = (600 - text_height) // 2
        
        draw.text((x, y), text, fill='white')
        
        # Save to BytesIO
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        img_io.seek(0)
        
        return img_io

    def handle(self, *args, **options):
        pages_to_setup = []
        
        if options['all']:
            pages_to_setup = SitePage.objects.filter(status='published').values_list('slug', flat=True)
        elif options['pages']:
            pages_to_setup = options['pages']
        else:
            self.stdout.write(self.style.WARNING("Please specify --pages or --all"))
            return

        for page_slug in pages_to_setup:
            try:
                page = SitePage.objects.get(slug=page_slug)
            except SitePage.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Page not found: {page_slug}"))
                continue

            # Delete existing images if requested
            if options['delete']:
                count = page.images.count()
                page.images.all().delete()
                self.stdout.write(self.style.WARNING(f"🗑️  Deleted {count} images from {page.slug}"))

            # Add test images
            for i in range(1, 4):  # Add 3 test images per page
                try:
                    img_io = self.create_test_image(f"Image {i}", page.title)
                    
                    page_image = PageImage(
                        page=page,
                        title=f"{page.title} - Image {i}",
                        caption=f"Test image for {page.title}",
                        description="This is a test image created by setup_page_images command",
                        order=i,
                    )
                    
                    page_image.image.save(
                        f"{page_slug}_test_{i}.png",
                        ContentFile(img_io.read()),
                        save=True
                    )
                    
                    self.stdout.write(self.style.SUCCESS(f"✅ Added image {i} to {page.slug}"))
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Failed to add image to {page.slug}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS("\n✅ Setup complete!"))
