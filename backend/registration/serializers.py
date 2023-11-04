from rest_framework import serializers


class EmailConfirmationResponseSerializer(serializers.Serializer):
    """
    Email confirmation response.
    """

    is_email_confirmed = serializers.BooleanField()


class ConfirmationEmailRequestSerializer(serializers.Serializer):
    """
    Email confirmation request.
    """

    email = serializers.EmailField()
