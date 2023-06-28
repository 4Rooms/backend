from rest_framework import serializers

from .models import CustomUser, Profile


class UserSerializer(serializers.ModelSerializer):
    """Custom User Model Serializer"""

    class Meta:
        model = CustomUser
        fields = ["id", "email", "password", "is_email_confirmed"]
        extra_kwargs = {"password": {"write_only": True}, "is_email_confirmed": {"read_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class ProfileSerializer(UserSerializer):
    """
    Serializer class to serialize the user Profile model
    """

    class Meta:
        model = Profile
        fields = ("nickname",)


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the avatar
    """

    class Meta:
        model = Profile
        fields = ("avatar",)
