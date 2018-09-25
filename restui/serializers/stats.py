from rest_framework import serializers

from restui.models.mappings import ReleaseStats

class ReleaseStatsSerializer(serializers.ModelSerializer):
    """
    Serializer for ReleaseStats instances
    """

    class Meta:
        model = ReleaseStats
        fields = '__all__'
