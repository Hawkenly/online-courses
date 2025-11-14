import os
from datetime import timedelta

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineCourses.settings')

app = Celery('OnlineCourses')

app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

app.conf.beat_schedule = {
    'long_running_query_every_10_seconds' : {
        'task': 'long_running_query',
        'schedule': timedelta(seconds=10),
    }
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')