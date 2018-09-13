from restui.models.annotations import UeMappingStatus, UeMappingComment, UeMappingLabel

from rest_framework import serializers

import pprint

###################################################################
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

class LabelSerializer(serializers.ModelSerializer):
    """
    mapping/:id/labels endpoint

    Serialize label associated to mapping
    """

    def create(self, validated_data):
        return UeMappingLabel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.time_stamp = validated_data.get('time_stamp', instance.time_stamp)
        instance.user_stamp = validated_data.get('user_stamp', instance.user_stamp)
        instance.label = validated_data.get('label', instance.label)
        instance.mapping = validated_data.get('mapping', instance.mapping)

#        instance.save()
#        return instance

    class Meta:
        model = UeMappingLabel
        fields = '__all__'

#
###################################################################
