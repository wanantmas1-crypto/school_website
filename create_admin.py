import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('DJANGO_ADMIN_USERNAME')
email = os.environ.get('DJANGO_ADMIN_EMAIL', '')
password = os.environ.get('DJANGO_ADMIN_PASSWORD')

if not username or not password:
    print('DJANGO_ADMIN_USERNAME or DJANGO_ADMIN_PASSWORD not set; skipping admin creation')
else:
    if User.objects.filter(username=username).exists():
        print(f'Admin user "{username}" already exists')
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Created admin user "{username}"')
