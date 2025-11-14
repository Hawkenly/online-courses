import time

from celery import shared_task

@shared_task(queue='long_tasks')
def long_running_query():
    time.sleep(10)
    return "Hello from long_running_query!"