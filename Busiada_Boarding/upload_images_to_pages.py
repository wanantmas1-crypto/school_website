"""
Script to upload images to specific dynamic pages.

Usage:
    python upload_images_to_pages.py <page_slug> <image_path> [image_path2] ...

Example:
    python upload_images_to_pages.py about path/to/image1.jpg path/to/image2.png
    python upload_images_to_pages.py school-gallery path/to/school*.jpg
"""

import os
import sys
import django
from pathlib import Path
from django.core.files.base import ContentFile
from glob import glob

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from boarding.models import SitePage, PageImage
from boarding.utils import image_upload_to


def upload_images_to_page(page_slug, image_paths):
    """Upload images to a specific page."""
    
    # Get the page
    try:
        page = SitePage.objects.get(slug=page_slug)
    except SitePage.DoesNotExist:
        print(f"❌ Page '{page_slug}' not found!")
        return False
    
    print(f"📄 Page: {page.title} ({page.slug})")
    print(f"📊 Current images: {page.images.count()}")
    print()
    
    # Process each image
    uploaded_count = 0
    for image_path in image_paths:
        # Expand wildcards
        expanded_paths = glob(image_path)
        
        if not expanded_paths:
            print(f"⚠️  No files found for: {image_path}")
            continue
        
        for file_path in expanded_paths:
            if not os.path.exists(file_path):
                print(f"❌ File not found: {file_path}")
                continue
            
            try:
                # Read the image file
                with open(file_path, 'rb') as f:
                    file_content = f.read()
                
                # Extract filename
                filename = os.path.basename(file_path)
                
                # Create PageImage record
                page_image = PageImage(
                    page=page,
                    title=filename.replace(os.path.splitext(filename)[1], '').replace('-', ' ').title(),
                    caption='',
                    description='',
                    order=page.images.count() + 1,
                )
                
                # Save the file using the upload_to function
                page_image.image.save(filename, ContentFile(file_content), save=True)
                
                print(f"✅ Uploaded: {filename}")
                print(f"   URL: {page_image.image.url}")
                uploaded_count += 1
                
            except Exception as e:
                print(f"❌ Failed to upload {file_path}: {str(e)}")
    
    print()
    print(f"✅ Uploaded {uploaded_count} image(s) to '{page.title}'")
    print(f"📊 Total images on page now: {page.images.count()}")
    
    return True


def list_pages():
    """List all available pages."""
    print("=" * 60)
    print("AVAILABLE PAGES FOR IMAGE UPLOAD")
    print("=" * 60)
    
    pages = SitePage.objects.all().order_by('slug')
    for page in pages:
        status_icon = "✅" if page.status == 'published' else "📋"
        print(f"{status_icon} {page.slug:30} | {page.title}")
    
    print()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python upload_images_to_pages.py <page_slug> [image_path1] [image_path2] ...")
        print()
        list_pages()
        sys.exit(0)
    
    page_slug = sys.argv[1]
    image_paths = sys.argv[2:]
    
    if not image_paths:
        print("No image paths provided!")
        list_pages()
        sys.exit(1)
    
    # Expand any glob patterns
    all_paths = []
    for path in image_paths:
        all_paths.extend(glob(path))
    
    if not all_paths:
        print(f"❌ No images found in: {', '.join(image_paths)}")
        sys.exit(1)
    
    upload_images_to_page(page_slug, all_paths)
