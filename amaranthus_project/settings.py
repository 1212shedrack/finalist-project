import os
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Suppress TensorFlow/oneDNN noise
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
# On Render: set SECRET_KEY env variable in the dashboard.
# Locally: falls back to the dev key (never use this in real production).
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-amaranthus-detection-fallback-key-2025-'
    'change-in-production'
)

# On Render set DEBUG=False (env var). Locally defaults to True.
DEBUG = os.environ.get('DEBUG', 'False') == 'False'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com',          # All Render subdomains
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),  # Exact Render hostname
]
# Remove empty strings that os.environ.get returns when var is not set
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# Application
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Serve staticfiles in dev too (consistent)
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'disease_app',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Must be right after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',   # i18n: after Session, before Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'amaranthus_project.urls'

# Templates
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
                'django.template.context_processors.i18n',
            ],
            'builtins': [
                # {% trans %} available everywhere
                'django.templatetags.i18n',
            ],
        },
    },
]

WSGI_APPLICATION = 'amaranthus_project.wsgi.application'

# Database
# SQLite for local dev and Render (ephemeral — history resets on redeploy).
# To use Render's free PostgreSQL, set DATABASE_URL env var and install dj-database-url.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

#  Internationalisation
LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LANGUAGES = [
    ('en', _('English')),
    ('sw', _('Swahili')),
    ('fr', _('Français')),
]

LOCALE_PATHS = [BASE_DIR / 'locale']

LANGUAGE_COOKIE_NAME = 'amaranthus_language'
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60

# Static Files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'          # collectstatic output dir
STATICFILES_DIRS = [BASE_DIR / 'static']        # source static dir

# WhiteNoise: compress + cache-bust static files automatically
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media Files
# Note: on Render these are ephemeral (lost on redeploy).
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default Primary Key

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ML Model
TFLITE_MODEL_PATH    = BASE_DIR / 'model' / 'amaranthus_efficientnet_v5.tflite'
RECOMMENDATIONS_PATH = BASE_DIR / 'recommendations.json'

# Upload Settings
MAX_UPLOAD_SIZE        = 10 * 1024 * 1024    # 10 MB
ALLOWED_IMAGE_TYPES  = ['image/jpeg', 'image/png', 'image/jpg']

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Security Headers (enforced when DEBUG=False)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
