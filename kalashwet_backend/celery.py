import os

from celery import Celery
from celery.schedules import crontab  # noqa: F401 - used once beat_schedule entries are added

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kalashwet_backend.settings')

app = Celery('kalashwet_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks, e.g.:
# 'some-task-daily': {
#     'task': 'app_name.tasks.some_task',
#     'schedule': crontab(hour=2, minute=0),
# },
app.conf.beat_schedule = {}
