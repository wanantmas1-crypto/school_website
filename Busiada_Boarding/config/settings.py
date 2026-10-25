from pathlib import Path
import os
import sys
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-9x%0n_9^h9f_pz6r7g8h9'
)

# Cloudinary configuration
CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL')
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# Use provided Cloudinary credentials if environment variables are not explicitly set
CLOUDINARY_URL = CLOUDINARY_URL or 'cloudinary://623378971952863:Gx4on-vb1YMgiaEdu-ZbcGteQbg@lbppchjw'
CLOUDINARY_CLOUD_NAME = CLOUDINARY_CLOUD_NAME or 'lbppchjw'
CLOUDINARY_API_KEY = CLOUDINARY_API_KEY or '623378971952863'
CLOUDINARY_API_SECRET = CLOUDINARY_API_SECRET or 'Gx4on-vb1YMgiaEdu-ZbcGteQbg'

CLOUDINARY_STORAGE = {
    'CLOUD_NAME': CLOUDINARY_CLOUD_NAME,
    'API_KEY': CLOUDINARY_API_KEY,
    'API_SECRET': CLOUDINARY_API_SECRET,
    'SECURE': True,
}

try:
    import cloudinary
except ImportError:
    cloudinary = None

try:
    import cloudinary_storage
except ImportError:
    cloudinary_storage = None

if cloudinary:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
    )

# In test environments, prefer local filesystem storage so uploaded test fixtures are
# valid byte streams rather than being sent to Cloudinary and rejected as invalid files.
IN_TESTS = 'test' in sys.argv or 'pytest' in sys.argv[0]

STORAGES = {
    'default': {
        'BACKEND': ('django.core.files.storage.FileSystemStorage' if IN_TESTS else 'cloudinary_storage.storage.MediaCloudinaryStorage'),
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
    },
}

if cloudinary_storage and not IN_TESTS:
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

if not cloudinary:
    print('Cloudinary package not installed: ensure cloudinary is installed for media storage')
elif not cloudinary_storage:
    print('django-cloudinary-storage package not installed: ensure django-cloudinary-storage is installed for media storage')
else:
    print('Cloudinary storage enabled: using Cloudinary media storage')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Security settings for production deployment
if DEBUG:
    SECURE_HSTS_SECONDS = 0
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
else:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Cloudinary media storage
    'cloudinary',
    'cloudinary_storage',

    # Your App
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
        'DIRS': [BASE_DIR / 'templates'],   # ← This tells Django where your templates are
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


DATABASE_URL = os.environ.get('DATABASE_URL')
if not DEBUG and not DATABASE_URL:
    raise ImproperlyConfigured('DATABASE_URL must be configured for production deployments.')

# Use Render's managed PostgreSQL database when configured, and SQLite locally.
DATABASES = {
    'default': dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=600,
    )
}

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
    },
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
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
    "https://cdnjs.cloudflare.com",
    "https://cdn.jsdelivr.net",
    "https://fonts.googleapis.com",
    "https://use.fontawesome.com",
    "https://cdn.quilljs.com",
)

CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-inline'",
    "https://unpkg.com",
    "https://cdn.tailwindcss.com",
    "https://cdn.quilljs.com",
)

CSP_FONT_SRC = (
    "'self'",
    "https://cdnjs.cloudflare.com",
    "https://use.fontawesome.com",
    "https://cdn.jsdelivr.net",
    "https://fonts.gstatic.com",
    "data:",
)

# Internationalization
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Africa/Nairobi'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
SERVE_MEDIA_FILES = os.environ.get('DJANGO_SERVE_MEDIA', str(DEBUG)).lower() in ('1', 'true', 'yes', 'on')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
