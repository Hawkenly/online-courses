from rest_framework import serializers

class WeatherRequestSerializer(serializers.Serializer):
    lat = serializers.FloatField(required=False)
    lon = serializers.FloatField(required=False)

class WeatherResponseSerializer(serializers.Serializer):
    temperature = serializers.FloatField()
    windspeed = serializers.FloatField()
    winddirection = serializers.FloatField()
    time = serializers.CharField()
