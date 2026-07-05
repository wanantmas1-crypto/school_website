#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from boarding.models import SitePage, PageImage, PageVideo

print("=" * 60)
print("PAGES IN SYSTEM")
print("=" * 60)
for page in SitePage.objects.all():
    img_count = page.images.count()
    vid_count = page.videos.count() if hasattr(page, 'videos') else 0
    print(f"\n📄 {page.slug}")
    print(f"   Title: {page.title}")
    print(f"   Status: {page.status}")
    print(f"   Images: {img_count}")
    print(f"   Videos: {vid_count}")

print("\n" + "=" * 60)
print("ALL IMAGES")
print("=" * 60)
for img in PageImage.objects.select_related('page').all():
    print(f"  {img.page.slug}: {img.image.name}")
    print(f"    URL: {img.image.url if img.image.name else 'N/A'}")

print("\n" + "=" * 60)
print("ALL VIDEOS")
print("=" * 60)
try:
    for vid in PageVideo.objects.select_related('page').all():
        print(f"  {vid.page.slug}: {vid.video.name}")
        print(f"    URL: {vid.video.url if vid.video.name else 'N/A'}")
except:
    print("  PageVideo model may not exist or have different structure")
