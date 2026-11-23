"""
Django settings for kalashwet_backend project.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import base64
from datetime import timedelta
from pathlib import Path
import dotenv
import os
from kalashwet_backend.setting.function import *


def get_env_path():
    from pathlib import Path
    CURRENT_DIR = Path(__file__).resolve().parent
    BASE_DIR = CURRENT_DIR.parent
    return Path(BASE_DIR, '.env')


dotenv.load_dotenv(str(get_env_path()))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# SECURITY WARNING: keep the secret key used in production secret!
# Stored base64-encoded in .env; decode it back to the real key here.
SECRET_KEY = base64.b64decode(os.environ['SECRET_KEY']).decode()

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = get_bool('DEBUG', False)
ALLOWED_HOSTS = [h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip()]
if DEBUG:
    for host in ['testserver', 'localhost', '127.0.0.1']:
        if host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)
CSRF_TRUSTED_ORIGINS = [o.strip() for o in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',') if o.strip()]

# Toggles DRF's BrowsableAPIRenderer.
IS_BROWSABLE = get_bool('IS_BROWSABLE', False)


# Application definition

INSTALLED_APPS = [
    'kalashwet_backend.apps.MongoAdminConfig',
    'kalashwet_backend.apps.MongoAuthConfig',
    'kalashwet_backend.apps.MongoContentTypesConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_mongodb_backend',
    'rest_framework',
    'django_filters',
    'kalashwet_backend.apps.MongoBeatConfig',

    # project apps
    'user',
    'pricing',
    'catalog',
    'orders',
    'payments',

    "debug_toolbar",
    'corsheaders',
    "django_mongodb_extensions",
]


CORS_ALLOWED_ORIGINS = [
    origin.strip() for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')
    if origin.strip()
]

CORS_ALLOW_ALL_ORIGINS = DEBUG and not CORS_ALLOWED_ORIGINS
CORS_ALLOW_CREDENTIALS = True


# panel, which captures the MongoDB commands this backend actually runs.
DEBUG_TOOLBAR_PANELS = [
    "debug_toolbar.panels.history.HistoryPanel",
    "debug_toolbar.panels.versions.VersionsPanel",
    "debug_toolbar.panels.timer.TimerPanel",
    "debug_toolbar.panels.settings.SettingsPanel",
    "debug_toolbar.panels.headers.HeadersPanel",
    "debug_toolbar.panels.request.RequestPanel",
    "django_mongodb_extensions.mql_panel.panel.MQLPanel",
    "debug_toolbar.panels.staticfiles.StaticFilesPanel",
    "debug_toolbar.panels.templates.TemplatesPanel",
    "debug_toolbar.panels.alerts.AlertsPanel",
    "debug_toolbar.panels.cache.CachePanel",
    "debug_toolbar.panels.signals.SignalsPanel",
    "debug_toolbar.panels.redirects.RedirectsPanel",
]

AUTH_USER_MODEL = 'user.User'


REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        ['rest_framework.renderers.JSONRenderer', 'rest_framework.renderers.BrowsableAPIRenderer']
        if IS_BROWSABLE else
        ['rest_framework.renderers.JSONRenderer']
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
    ],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': get_int('MAX_PAGE_SIZE', 20),

    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.ScopedRateThrottle'],
    'DEFAULT_THROTTLE_RATES': {
        'login': os.environ.get('THROTTLE_LOGIN', '10/min'),
    },
}


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'kalashwet_backend.middleware.HealthCheckMiddleware',
    # Enable once an app provides a RequestLog model (see setting/request_logger.py):
    # 'kalashwet_backend.setting.request_logger.RequestLogMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'kalashwet_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'kalashwet_backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

db_options = {}
if os.environ.get('MONGO_USER'):
    db_options['authSource'] = os.environ.get('MONGO_AUTH_SOURCE', os.environ['MONGO_DB_NAME'])

DATABASES = {
    'default': {
        'ENGINE': 'django_mongodb_backend',
        'HOST': os.environ['MONGO_HOST'],
        'PORT': int(os.environ['MONGO_PORT']),
        'NAME': os.environ['MONGO_DB_NAME'],
        'USER': os.environ.get('MONGO_USER', ''),
        'PASSWORD': os.environ.get('MONGO_PASSWORD', ''),
        'OPTIONS': db_options,
    }
}

DATABASE_ROUTERS = ['django_mongodb_backend.routers.MongoRouter']


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/6.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django_mongodb_backend.fields.ObjectIdAutoField'

MIGRATION_MODULES = {
    'admin': 'mongo_migrations.admin',
    'auth': 'mongo_migrations.auth',
    'contenttypes': 'mongo_migrations.contenttypes',
    'django_celery_beat': 'mongo_migrations.django_celery_beat',
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=7),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True
}


# TODO MEDIA SETTING
from .setting.media import *

# TODO VARIABLE SETTING
from .setting.variables import *

# TODO DEBUGTOOLBAR SETTING
from .setting.debugtoolbar import *


SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
