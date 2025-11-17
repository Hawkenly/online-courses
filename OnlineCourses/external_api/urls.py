from django.urls import path
from .views import WeatherFetchView, WeatherCachedView

urlpatterns = [
    path("weather/fetch/", WeatherFetchView.as_view(), name="weather-update"),
    path("weather/cached/", WeatherCachedView.as_view(), name="weather-cache"),
]
