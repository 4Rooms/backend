import html

from accounts.models import Profile, User
from rest_framework import serializers

from .validators.common import WhitespaceValidator


class UserNameField(serializers.CharField):
    """
    Set validators for username field
    """

    def __init__(self, *args, **kwargs):
        # set default values
        kwargs["min_length"] = kwargs.get("min_length", 1)
        kwargs["max_length"] = kwargs.get("max_length", 20)
        kwargs["trim_whitespace"] = kwargs.get("trim_whitespace", False)

        validators = kwargs.get("validators", [])
        validators.append(WhitespaceValidator())
        kwargs["validators"] = validators

        super().__init__(*args, **kwargs)

    def to_internal_value(self, data):
        # escape html
        data = html.escape(data)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Custom User Model Serializer"""

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "is_email_confirmed"]
        extra_kwargs = {
            "id": {"read_only": True},
            "password": {"write_only": True},
            "is_email_confirmed": {"read_only": True},
        }

    username = UserNameField(required=True)

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

    username = UserNameField(required=True)
    password = serializers.CharField(required=True, max_length=128)


class UpdateUserDataSerializer(serializers.Serializer):
    """
    User data
    """

    model = User

    username = UserNameField(required=True)
    email = serializers.EmailField(required=True)
