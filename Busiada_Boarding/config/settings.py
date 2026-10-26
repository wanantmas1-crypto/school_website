from pathlib import Path
import os
import sys
from urllib.parse import parse_qsl, unquote, urlparse

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ImproperlyConfigured(
            'DJANGO_SECRET_KEY must be set when DEBUG is disabled.'
        )
    SECRET_KEY = 'local-development-only-insecure-key'

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
cloudinary_environment_parts = (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)
has_cloudinary_environment_parts = any(cloudinary_environment_parts)
cloudinary_url_options = {}
if CLOUDINARY_URL:
    parsed_cloudinary_url = urlparse(CLOUDINARY_URL)
    if (
        parsed_cloudinary_url.scheme != 'cloudinary'
        or not parsed_cloudinary_url.hostname
        or not parsed_cloudinary_url.username
        or not parsed_cloudinary_url.password
    ):
        raise ImproperlyConfigured(
            'CLOUDINARY_URL must use the cloudinary://key:secret@cloud_name format.'
        )
    CLOUDINARY_CLOUD_NAME = parsed_cloudinary_url.hostname
    CLOUDINARY_API_KEY = unquote(parsed_cloudinary_url.username)
    CLOUDINARY_API_SECRET = unquote(parsed_cloudinary_url.password)
    cloudinary_url_options = dict(parse_qsl(parsed_cloudinary_url.query))

cloudinary_parts = (
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
)
has_cloudinary_credentials = bool(CLOUDINARY_URL) or all(cloudinary_parts)

if CLOUDINARY_URL and has_cloudinary_environment_parts:
    raise ImproperlyConfigured(
        'Configure Cloudinary with CLOUDINARY_URL or the three individual '
        'CLOUDINARY_* variables, not both.'
    )
if has_cloudinary_environment_parts and not all(cloudinary_parts):
    raise ImproperlyConfigured(
        'Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and '
        'CLOUDINARY_API_SECRET together.'
    )
if not DEBUG and not has_cloudinary_credentials:
    raise ImproperlyConfigured(
        'Production media storage requires CLOUDINARY_URL or all three '
        'CLOUDINARY_* variables.'
    )

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY': CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
    'SECURE': True,
}
if CLOUDINARY_URL and parsed_cloudinary_url.path.strip('/'):
    CLOUDINARY_STORAGE['PRIVATE_CDN'] = True
    CLOUDINARY_STORAGE['SECURE_DISTRIBUTION'] = (
        parsed_cloudinary_url.path.strip('/')
    )

import cloudinary
if has_cloudinary_credentials:
    cloudinary_config = dict(cloudinary_url_options)
    cloudinary_config.update(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True,
    )
    cloudinary.config(**cloudinary_config)

IN_TESTS = 'test' in sys.argv or 'pytest' in sys.argv[0]
MEDIA_STORAGE_BACKEND = (
    'cloudinary_storage.storage.MediaCloudinaryStorage'
    if has_cloudinary_credentials and not IN_TESTS
    else 'django.core.files.storage.FileSystemStorage'
)
STORAGES = {
    'default': {'BACKEND': MEDIA_STORAGE_BACKEND},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

database_url = os.environ.get('DATABASE_URL')
require_database_url = os.environ.get(
    'DJANGO_REQUIRE_DATABASE_URL', 'False'
).lower() in ('1', 'true', 'yes')
if database_url:
    DATABASES = {
        'default': dj_database_url.parse(
            database_url,
            conn_max_age=600,
            ssl_require=True,
        )
    }
elif not require_database_url:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    raise ImproperlyConfigured(
        'DATABASE_URL must be set when DJANGO_REQUIRE_DATABASE_URL is enabled.'
    )
if (
    require_database_url
    and DATABASES['default']['ENGINE'] != 'django.db.backends.postgresql'
):
    raise ImproperlyConfigured(
        'DATABASE_URL must use PostgreSQL when DJANGO_REQUIRE_DATABASE_URL is enabled.'
    )
DATABASES['default']['CONN_HEALTH_CHECKS'] = True

render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
configured_hosts = os.environ.get('DJANGO_ALLOWED_HOSTS')
if not configured_hosts:
    configured_hosts = render_hostname or 'localhost,127.0.0.1'
if not DEBUG and not os.environ.get('DJANGO_ALLOWED_HOSTS') and not render_hostname:
    raise ImproperlyConfigured(
        'Set DJANGO_ALLOWED_HOSTS to the assigned production hostname.'
    )
ALLOWED_HOSTS = [
    host.strip()
    for host in configured_hosts.split(',')
    if host.strip()
]
if not DEBUG and (not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS):
    raise ImproperlyConfigured(
        'Set DJANGO_ALLOWED_HOSTS to exact production hostnames; '
        'wildcards are not allowed.'
    )

CSRF_TRUSTED_ORIGINS = [
    origin.strip().rstrip('/')
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
if not CSRF_TRUSTED_ORIGINS and render_hostname:
    CSRF_TRUSTED_ORIGINS = [f'https://{render_hostname}']
if not DEBUG and not CSRF_TRUSTED_ORIGINS:
    raise ImproperlyConfigured(
        'Set CSRF_TRUSTED_ORIGINS to the production HTTPS origin.'
    )
if not DEBUG and any(
    urlparse(origin).scheme != 'https' for origin in CSRF_TRUSTED_ORIGINS
):
    raise ImproperlyConfigured(
        'CSRF_TRUSTED_ORIGINS must contain HTTPS origins in production.'
    )

SECURE_SSL_REDIRECT = os.environ.get(
    'DJANGO_SECURE_SSL_REDIRECT', 'False'
).lower() in ('1', 'true', 'yes')
if os.environ.get('DJANGO_TRUST_X_FORWARDED_PROTO', 'False').lower() in (
    '1',
    'true',
    'yes',
):
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '0'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    SECURE_HSTS_SECONDS > 0
    and os.environ.get(
        'DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False'
    ).lower() in ('1', 'true', 'yes')
)
SECURE_HSTS_PRELOAD = (
    SECURE_HSTS_SECONDS > 0
    and os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', 'False').lower()
    in ('1', 'true', 'yes')
)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary',
    'cloudinary_storage',
    'boarding',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'boarding.middleware.SecurityHeadersMiddleware',
    'boarding.middleware.IpRateLimitMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'boarding.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'config.urls': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation.'
            'UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    'https://cdnjs.cloudflare.com',
    'https://cdn.jsdelivr.net',
    'https://fonts.googleapis.com',
    'https://use.fontawesome.com',
    'https://cdn.quilljs.com',
)

CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    'https://unpkg.com',
    'https://cdn.tailwindcss.com',
    'https://cdn.quilljs.com',
    'https://cdn.jsdelivr.net',
)

CSP_FONT_SRC = (
    "'self'",
    'https://cdnjs.cloudflare.com',
    'https://use.fontawesome.com',
    'https://fonts.gstatic.com',
    'data:',
)

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SERVE_MEDIA_FILES = (
    os.environ.get('DJANGO_SERVE_MEDIA', str(DEBUG)).lower()
    in ('1', 'true', 'yes', 'on')
)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
