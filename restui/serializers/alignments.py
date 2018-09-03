from restui.models.mappings import Alignment, AlignmentRun #, Mapping, MappingHistory, ReleaseMappingHistory

from rest_framework import serializers

class AlignmentRunSerializer(serializers.ModelSerializer):
    """
    Serialize an AlignmentRun instance
    """
    
    class Meta:
        model = AlignmentRun
        fields = '__all__'
        
class AlignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alignment
        fields = '__all__'
