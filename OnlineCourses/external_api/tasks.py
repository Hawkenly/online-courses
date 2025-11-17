import requests
from celery import shared_task
from django.core.cache import cache
from django.conf import settings

from external_api.dto import WeatherResponseDto

@shared_task(
    bind=True,
    queue="weather",
    name = "fetch_weather",
    max_retries = 3,
    default_retry_delay = 30,)
def fetch_weather_data(self, lat: float = None, lon: float = None):
    lat = lat if lat is not None else settings.WEATHER_LAT
    lon = lon if lon is not None else settings.WEATHER_LON

    if lat is None or lon is None:
        return None

    url = settings.WEATHER_API_URL
    if not url:
        return None

    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "wind_speed_10m", "wind_direction_10m"]
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
       raise self.retry(exc=exc)

    current = data.get("current")

    result_dto = WeatherResponseDto(
        temperature=float(current.get("temperature_2m")),
        windspeed=float(current.get("wind_speed_10m")),
        winddirection=float(current.get("wind_direction_10m")),
        time=str(current.get("time"))
    )

    cache.set(settings.WEATHER_CACHE_KEY, result_dto.__dict__, timeout=300)

    return result_dto.__dict__
