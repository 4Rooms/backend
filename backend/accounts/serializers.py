from rest_framework import serializers

from .models import Profile, User


class UserSerializer(serializers.ModelSerializer):
    """Custom User Model Serializer"""

    class Meta:
        model = User
        fields = ["username", "email", "password", "is_email_confirmed"]
        extra_kwargs = {"password": {"write_only": True}, "is_email_confirmed": {"read_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProfileAvatarSerializer(serializers.ModelSerializer):
    """
    Serializer class to serialize the avatar
    """

    class Meta:
        model = Profile
        fields = ("avatar",)


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    model = User

    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
