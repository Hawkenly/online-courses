from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache
from django.conf import settings
from rest_framework import status

from .dto import WeatherRequestDto, WeatherResponseDto
from .serializers import WeatherRequestSerializer, WeatherResponseSerializer
from .tasks import fetch_weather_data

class WeatherFetchView(APIView):

    @extend_schema(
        summary="Запустить задачу получения погоды",
        tags=["Weather"],
        parameters=[
            OpenApiParameter("lat", type=float, required=False, description="Широта"),
            OpenApiParameter("lon", type=float, required=False, description="Долгота"),
        ],
        request=WeatherRequestSerializer,
        responses={202: None}
    )
    def get(self, request):
        serializer = WeatherRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        dto = WeatherRequestDto(**serializer.validated_data)

        fetch_weather_data.delay(dto.lat, dto.lon)
        return Response({"message": "Weather task started"}, status=status.HTTP_202_ACCEPTED)


class WeatherCachedView(APIView):


    @extend_schema(
        summary="Получить закешированную погоду",
        tags=["Weather"],
        responses={200: WeatherResponseSerializer, 404: None}
    )
    def get(self, request):
        data = cache.get(settings.WEATHER_CACHE_KEY)
        if not data:
            return Response({"error": "Cache empty"}, status=status.HTTP_404_NOT_FOUND)

        dto = WeatherResponseDto(**data)
        serializer = WeatherResponseSerializer(dto.__dict__)
        return Response(serializer.data)
