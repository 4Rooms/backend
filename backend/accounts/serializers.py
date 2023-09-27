from accounts.models import Profile, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """Custom User Model Serializer"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "is_email_confirmed"]
        extra_kwargs = {"password": {"write_only": True}, "is_email_confirmed": {"read_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ProfileSerializer(serializers.ModelSerializer):
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


class ChangePasswordResponseSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """

    message = serializers.CharField(required=True)


class EmailSerializer(serializers.Serializer):
    """
    Serializer for email.
    """

    model = User

    email = serializers.EmailField(required=True)


class PasswordResetSerializer(serializers.Serializer):
    """
    Serializer for password reset.
    """

    model = User

    password = serializers.CharField(required=True)
    token_id = serializers.CharField(required=True)


class LoginDataSerializer(serializers.Serializer):
    """
    Login data
    """

    model = User

    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=128)
