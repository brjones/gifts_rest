from restui.models.annotations import UeMappingStatus, UeMappingComment, UeMappingLabel, CvUeStatus, UeUnmappedEntryLabel

from rest_framework import serializers

import pprint

class StatusSerializer(serializers.ModelSerializer):
    """
    mapping/:id/status endpoint

    Serialize status associated to mapping
    """

    def create(self, validated_data):
        return UeMappingStatus.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.time_stamp = validated_data.get('time_stamp', instance.time_stamp)
        instance.user_stamp = validated_data.get('user_stamp', instance.user_stamp)
        instance.status = validated_data.get('status', instance.status)
        instance.mapping = validated_data.get('mapping', instance.mapping)

        instance.save()
        return instance

    class Meta:
        model = UeMappingStatus
        fields = '__all__'

class CvUeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = CvUeStatus
        fields = '__all__'

class StatusHistorySerializer(serializers.Serializer):
    """
    Serialize a status history record
    """
    status = serializers.CharField()
    time_stamp = serializers.DateTimeField()
    user = serializers.CharField()

class CommentSerializer(serializers.ModelSerializer):
    """
    mapping/:id/comments endpoint

    Serialize comment associated to mapping
    """

    # this is probably not needed, the framework should already
    # check the provided comment data is not blank
    def validate_comment(self, value):
        """
        Check the comment is non-empty
        """

        if not value.translate({ord(" "):None, ord("\t"):None}):
            raise serializers.ValidationError("Comment is empty")

        return value

    def create(self, validated_data):
        return UeMappingComment.objects.create(**validated_data)

    class Meta:
        model = UeMappingComment
        fields = '__all__'

class MappingLabelSerializer(serializers.ModelSerializer):
    """
    mapping/:id/labels endpoint

    Serialize label associated to mapping
    """

    def create(self, validated_data):
        return UeMappingLabel.objects.create(**validated_data)

    class Meta:
        model = UeMappingLabel
        fields = '__all__'

class UnmappedEntryLabelSerializer(serializers.ModelSerializer):
    """
    unmapped/<int:mapping_view_id>/labels/<label_id>/ endpoint

    Serialize label associated to unmapped entry
    """

    def create(self, validated_data):
        return UeUnmappedEntryLabel.objects.create(**validated_data)

    class Meta:
        model = UeUnmappedEntryLabel
        fields = '__all__'


class LabelSerializer(serializers.Serializer):
    """
    Serializer for an individual label
    """

    label = serializers.CharField()
    id = serializers.IntegerField()
    status = serializers.BooleanField()


class LabelsSerializer(serializers.Serializer):
    """
    For nested serialization of user label for a mapping in call to (mapping|unmapped)/<id>/labels endpoint.
    """

    labels = LabelSerializer(many=True)
