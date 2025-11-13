from django.apps import AppConfig


class LongRunningQueryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'long_running_query'
