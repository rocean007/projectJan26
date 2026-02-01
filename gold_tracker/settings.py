import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    "whitenoise.runserver_nostatic",
    'django.contrib.staticfiles',
    'corsheaders',
    'api',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'corsheaders.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'gold_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [],
        },
    },
]

WSGI_APPLICATION = 'gold_tracker.wsgi.application'

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Cache for 3 seconds
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 3,
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles", "static")

GOLD_API_KEY = 'your-goldapi-key-here'  # Change this
GOLD_API_BASE_URL = 'https://api.gold-api.com'
EXCHANGE_RATE_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'