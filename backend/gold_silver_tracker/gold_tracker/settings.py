import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-your-secret-key-change-this'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'corsheaders',
    'api.apps.ApiConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
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

CORS_ALLOW_ALL_ORIGINS = True

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': 3,
    }
}

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

GOLD_API_KEY = 'your-goldapi-key-here'
GOLD_API_BASE_URL = 'https://api.gold-api.com'
EXCHANGE_RATE_URL = 'https://api.exchangerate-api.com/v4/latest/USD'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'