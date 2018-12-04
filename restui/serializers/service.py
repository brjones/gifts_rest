from rest_framework import serializers

class StatusSerializer(serializers.Serializer):
    """
    Status serializer
    """
    ping = serializers.IntegerField()
