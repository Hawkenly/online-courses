from rest_framework import serializers

class LongQuerySerializer(serializers.Serializer):
    result = serializers.CharField()