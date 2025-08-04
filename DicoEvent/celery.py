import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DicoEvent.settings')

app = Celery('DicoEvent')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'send-event-reminders': {
        'task': 'events.tasks.send_event_reminders',
        'schedule': crontab(minute='*/15'),  # Check every 15 minutes
    },
}

app.conf.timezone = 'UTC'

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')