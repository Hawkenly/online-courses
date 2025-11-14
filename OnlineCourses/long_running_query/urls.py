from django.urls import path
from .views import LongQueryView

app_name = 'long_running_query'

urlpatterns = [
    path('long_task/', LongQueryView.as_view(), name='long_query'),
]