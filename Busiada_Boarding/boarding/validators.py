"""
File validators and compression utilities for media uploads.
"""
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image
import io
import os


# Size limits in bytes
SIZE_LIMITS = {
    'image': 5 * 1024 * 1024,  # 5 MB
    'video': 100 * 1024 * 1024,  # 100 MB
    'document': 50 * 1024 * 1024,  # 50 MB
    'logo': 2 * 1024 * 1024,  # 2 MB
    'profile': 5 * 1024 * 1024,  # 5 MB
}


def validate_image_file_size(file_obj, max_size_mb=5):
    """Validate image file size. Default 5MB."""
    max_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(
            f'Image file too large. Max size is {max_size_mb}MB. '
            f'Your file is {round(file_obj.size / 1024 / 1024, 2)}MB.'
        )


def validate_video_file_size(file_obj, max_size_mb=100):
    """Validate video file size. Default 100MB."""
    max_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(
            f'Video file too large. Max size is {max_size_mb}MB. '
            f'Your file is {round(file_obj.size / 1024 / 1024, 2)}MB.'
        )


def validate_document_file_size(file_obj, max_size_mb=50):
    """Validate document file size. Default 50MB."""
    max_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(
            f'Document file too large. Max size is {max_size_mb}MB. '
            f'Your file is {round(file_obj.size / 1024 / 1024, 2)}MB.'
        )


def validate_logo_file_size(file_obj, max_size_mb=2):
    """Validate logo file size. Default 2MB."""
    max_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_bytes:
        raise ValidationError(
            f'Logo file too large. Max size is {max_size_mb}MB. '
            f'Your file is {round(file_obj.size / 1024 / 1024, 2)}MB.'
        )


def compress_image(image_file, quality=85, max_width=2000, max_height=2000):
    """
    Compress an image file and return optimized ContentFile.
    
    Args:
        image_file: Django UploadedFile or File object
        quality: JPEG quality (1-100), default 85
        max_width: Max width in pixels, default 2000
        max_height: Max height in pixels, default 2000
    
    Returns:
        ContentFile: Compressed image file
    """
    try:
        # Open image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB for JPEG compression
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        # Resize if too large
        if img.width > max_width or img.height > max_height:
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        
        # Save compressed image
        output = io.BytesIO()
        format_map = {
            'JPEG': 'JPEG',
            'JPG': 'JPEG',
            'PNG': 'PNG',
            'GIF': 'GIF',
            'WEBP': 'WEBP',
        }
        
        img_format = format_map.get(img.format, 'JPEG')
        
        if img_format == 'JPEG':
            img.save(output, format='JPEG', quality=quality, optimize=True)
        else:
            img.save(output, format=img_format, optimize=True)
        
        output.seek(0)
        
        # Get original filename
        original_name = image_file.name if hasattr(image_file, 'name') else 'image.jpg'
        
        return ContentFile(output.getvalue(), name=original_name)
    
    except Exception as e:
        # If compression fails, return original file
        print(f'Image compression failed: {e}. Returning original file.')
        image_file.seek(0)
        return image_file


def get_file_size_display(file_obj):
    """Get human-readable file size."""
    if not file_obj or not hasattr(file_obj, 'size'):
        return 'Unknown'
    
    size_bytes = file_obj.size
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f'{size_bytes:.1f}{unit}'
        size_bytes /= 1024
    
    return f'{size_bytes:.1f}TB'


def get_upload_percentage(current_size, total_size):
    """Calculate upload percentage."""
    if total_size == 0:
        return 0
    return round((current_size / total_size) * 100, 1)
