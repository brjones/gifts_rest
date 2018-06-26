from restui.models.annotations import UeMappingStatus, UeMappingComment

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

#
# TODO
#
# - include user_stamp when authentication system is in place
#
class CommentSerializer(serializers.ModelSerializer):
    """
    mapping/:id/comment endpoint

    Serialize comment associated to mapping
    """

    # this is probably not needed, the framework should check
    # the provided comment data is not blank
    def validate_comment(self, value):
        """
        Check the comment is non-empty
        """

        if not value.translate({ord(" "):None, ord("\t"):None}):
            raise serializer.ValidationError("Comment is empty")

        return value

    def create(self, validated_data):
        return UeMappingComment.objects.create(**validated_data)

    class Meta:
        model = UeMappingComment
        exclude = ('user_stamp',)
