import time

from celery import shared_task

@shared_task(queue='long_tasks',
             name='long_running_query',
             )
def long_running_query():
    time.sleep(10)
    return "Hello from long_running_query!"