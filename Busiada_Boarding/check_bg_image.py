#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from boarding.models import SitePage
from boarding.utils import safe_file_url

page = SitePage.objects.filter(slug='home').first()
if page:
    print(f'Home page found: {page.title}')
    print(f'Background image field: {page.background_image}')
    print(f'Background image name: {page.background_image.name if page.background_image else "None"}')
    print(f'Background image URL: {safe_file_url(page.background_image)}')
else:
    print('No home page found')
