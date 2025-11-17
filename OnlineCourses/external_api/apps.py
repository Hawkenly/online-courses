from django.apps import AppConfig

class ExternalApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'external_api'

    def ready(self):
        from external_api.tasks import fetch_weather_data
        fetch_weather_data.delay()
