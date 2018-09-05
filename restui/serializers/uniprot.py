from rest_framework import serializers

from restui.models.uniprot import UniprotEntry

class UniprotEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for UniprotEntry instances
    """

    class Meta:
        model = UniprotEntry
        fields = '__all__'
