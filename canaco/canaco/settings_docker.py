"""Docker settings for the Canaco stack (PostgreSQL)."""
import os
from pathlib import Path

from .settings import *  # noqa: F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'canaco'),
        'USER': os.getenv('DB_USER', 'canaco'),
        'PASSWORD': os.getenv('DB_PASSWORD', ''),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

STATIC_ROOT = Path(os.getenv('DJANGO_STATIC_ROOT', BASE_DIR / 'staticfiles'))
MEDIA_ROOT = Path(os.getenv('DJANGO_MEDIA_ROOT', BASE_DIR / 'media'))