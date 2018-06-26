from restui.models.annotations import UeMappingStatus

from rest_framework import serializers

#
# TODO: include user_stamp when authentication system is in place
#
class StatusSerializer(serializers.ModelSerializer):
    """
    mapping/:id/status endpoint

    Serialize status associated to mapping
    """
    def create(self, validated_data):
        return UeMappingStatus.objects.create(**validated_data)
    
    class Meta:
        model = UeMappingStatus
        exclude = ('user_stamp',)
