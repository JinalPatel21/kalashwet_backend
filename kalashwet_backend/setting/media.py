import os
from pathlib import Path
from kalashwet_backend.setting.function import get_bool
from kalashwet_backend.settings import BASE_DIR

# These URLs are required even when files are served from object storage.
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
MEDIA_URL = os.environ.get('MEDIA_URL', '/media/')

if get_bool('USE_S3', False):

    DEFAULT_FILE_STORAGE = 'kalashwet_backend.storage_backends.PublicMediaStorage'
    STATICFILES_STORAGE = 'kalashwet_backend.storage_backends.StaticStorage'
    STORAGES = {
        'default': {'BACKEND': 'kalashwet_backend.storage_backends.PublicMediaStorage'},
        'staticfiles': {'BACKEND': 'kalashwet_backend.storage_backends.StaticStorage'},
    }

    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_REGION_NAME = os.environ.get('AWS_REGION_NAME')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_STATIC_LOCATION = os.environ.get('AWS_STATIC_LOCATION')
    AWS_MEDIA_LOCATION = os.environ.get('AWS_MEDIA_LOCATION')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    AWS_S3_ENDPOINT_URL = f'https://{AWS_REGION_NAME}.linodeobjects.com'

else:

    STATICFILES_DIRS = [Path(BASE_DIR / 'static')] if Path(BASE_DIR / 'static').is_dir() else []
    STATIC_ROOT = Path(BASE_DIR, 'static_cdn')
    MEDIA_ROOT = Path(BASE_DIR, 'media_cdn')
    STORAGES = {
        'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
        'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
    }
