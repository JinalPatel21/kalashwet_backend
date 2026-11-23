import os

from kalashwet_backend.setting.function import *

ADMIN_PAGE_SIZE = get_int("ADMIN_PAGE_SIZE")
WEB_LINK = os.environ.get('WEB_LINK')


# --- Celery -------------------------------------------------------------------

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Kolkata'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


# Static token for read-only monitoring access (see setting/permissions.py).
LOGS_API_TOKEN = os.environ.get('LOGS_API_TOKEN', '')


# --- Error email alerts ------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

SERVER_EMAIL = os.environ.get('SERVER_EMAIL', EMAIL_HOST_USER or 'root@localhost')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', SERVER_EMAIL)
# Who receives the crash mails: comma-separated addresses in ADMIN_EMAILS.
ADMINS = [('admin', a.strip()) for a in os.environ.get('ADMIN_EMAILS', '').split(',') if a.strip()]
