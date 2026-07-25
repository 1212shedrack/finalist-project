import os
try:
    import dj_database_url
except ImportError:
    dj_database_url = None
from pathlib import Path
from django.utils.translation import gettext_lazy as _

# Suppress TensorFlow/oneDNN noise
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-amaranthus-detection-fallback-key-2025-'
    'change-in-production'
)

# On Render: set DEBUG=False via env var. Locally defaults to True.
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    '.onrender.com',
    os.environ.get('RENDER_EXTERNAL_HOSTNAME', ''),
]
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# ── CSRF trusted origins (required for POST forms on Render) ──────────────────
# Without this, every login/register/form POST gets a 403 CSRF error on Render.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '')
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
]
if _render_host:
    CSRF_TRUSTED_ORIGINS += [
        f'https://{_render_host}',
        f'http://{_render_host}',
    ]
CSRF_TRUSTED_ORIGINS.append('https://*.onrender.com')

# Application
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Serve staticfiles
    'whitenoise.runserver_nostatic',
    'django.contrib.staticfiles',
    'disease_app',
    'accounts',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # Must be right after SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
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

# ── Database ─────────────────────────────────────────────────────────────────
# Automatically uses PostgreSQL on Render (DATABASE_URL is set by the
# linked database service). Falls back to SQLite for local development.
if dj_database_url and os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
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
TFLITE_MODEL_PATH = BASE_DIR / 'model' / 'amaranthus_efficientnet_v5.tflite'
RECOMMENDATIONS_PATH = BASE_DIR / 'recommendations.json'

# Upload Settings
MAX_UPLOAD_SIZE = 10 * 1024 * 1024    # 10 MB
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/jpg']
AVATAR_MAX_SIZE = 5 * 1024 * 1024     # 5 MB

# Messages
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# ── Authentication ────────────────────────────────────────────────────────────
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/'

# Session: 2-week default; overridden to 0 (browser session) when remember_me is off
SESSION_COOKIE_AGE = 14 * 24 * 60 * 60   # 14 days
SESSION_SAVE_EVERY_REQUEST = True

# ── Email — Console backend (prints reset links to server log) ────────────────
# To switch to real email later, replace EMAIL_BACKEND and add SMTP settings.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'AmaranthusAI <noreply@amaranthusai.com>'

# ── Password validation ───────────────────────────────────────────────────────
# (Already configured above; kept for clarity)

# Security Headers (enforced when DEBUG=False)
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
