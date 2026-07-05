"""
Management command to fix image paths in the database.
Images uploaded were saved to boarding.utils.image_upload_to/ but database references site_pages/.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from boarding.models import PageImage, SitePage


class Command(BaseCommand):
    help = 'Fix image paths in the database to match actual file locations'

    def handle(self, *args, **options):
        media_root = settings.MEDIA_ROOT
        
        # Images that exist in the correct location
        correct_images = []
        # Images that need path fixing
        images_to_fix = []
        # Images that are missing (no file found)
        missing_images = []
        
        all_images = PageImage.objects.all()
        self.stdout.write(f"Checking {all_images.count()} images...")
        
        for img in all_images:
            current_path = os.path.join(media_root, img.image.name)
            
            # Check if image exists at current location
            if os.path.exists(current_path):
                correct_images.append(img)
                self.stdout.write(self.style.SUCCESS(f"✓ Exists: {img.image.name}"))
                continue
            
            # Check if image exists in boarding.utils.image_upload_to directory
            filename = os.path.basename(img.image.name)
            alt_path = os.path.join(media_root, 'boarding.utils.image_upload_to', filename)
            
            if os.path.exists(alt_path):
                images_to_fix.append((img, filename))
                self.stdout.write(self.style.WARNING(f"⚠ Found at alt location: {filename}"))
                continue
            
            # Image not found anywhere
            missing_images.append(img)
            self.stdout.write(self.style.ERROR(f"✗ Missing: {img.image.name}"))
        
        # Summary
        self.stdout.write("\n" + "="*60)
        self.stdout.write(f"Summary:")
        self.stdout.write(self.style.SUCCESS(f"  ✓ Correct location: {len(correct_images)}"))
        self.stdout.write(self.style.WARNING(f"  ⚠ Needs fixing: {len(images_to_fix)}"))
        self.stdout.write(self.style.ERROR(f"  ✗ Missing: {len(missing_images)}"))
        
        # Fix images that can be fixed
        if images_to_fix and self.confirm_fix():
            self.stdout.write("\nFixing image paths...")
            for img, filename in images_to_fix:
                # Update the image field to point to the correct location
                img.image.name = os.path.join('boarding.utils.image_upload_to', filename)
                img.save()
                self.stdout.write(self.style.SUCCESS(f"✓ Fixed: {filename}"))
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Fixed {len(images_to_fix)} images!"))
        
        # Remove missing images from database
        if missing_images and self.confirm_delete():
            self.stdout.write(f"\nRemoving {len(missing_images)} missing images from database...")
            for img in missing_images:
                page = img.page
                img.delete()
                self.stdout.write(self.style.ERROR(f"✗ Deleted: {img.image.name} from page '{page.slug}'"))
            
            self.stdout.write(self.style.SUCCESS(f"\n✓ Removed {len(missing_images)} orphaned records!"))

    def confirm_fix(self):
        """Ask user before fixing image paths"""
        response = input("\nDo you want to fix the image paths? (yes/no): ").lower().strip()
        return response in ('yes', 'y')

    def confirm_delete(self):
        """Ask user before deleting missing images"""
        response = input("\nDo you want to remove missing images from the database? (yes/no): ").lower().strip()
        return response in ('yes', 'y')
