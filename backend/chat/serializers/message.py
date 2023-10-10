from typing import Optional
from urllib.parse import urljoin

from chat.models.message import Message
from django.conf import settings
from rest_framework import serializers


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for websocket messages"""

    # override timestamp field to return timestamp in seconds
    timestamp = serializers.DateTimeField(format="%s", read_only=True)

    # Add user_name field to return username instead id
    user_name = serializers.SerializerMethodField(source="get_user_name")
    user_avatar = serializers.SerializerMethodField(source="get_user_avatar")

    class Meta:
        model = Message
        fields = "__all__"
        read_only_fields = ["id", "timestamp", "user"]

    def create(self, validated_data):
        """Save message with user"""

        user = self.context.get("user")
        validated_data["user"] = user
        return super().create(validated_data)

    @staticmethod
    def get_user_name(obj) -> Optional[str]:
        """Return username (instead id)"""

        if isinstance(obj, Message):
            return obj.user.username
        return None

    def get_user_avatar(self, obj) -> Optional[str]:
        """Return URL to user avatar"""

        if isinstance(obj, Message):
            return urljoin(settings.DJANGO_HOST, obj.user.profile.avatar.url)
        return None


class WebsocketMessageSerializer(serializers.Serializer):
    """Serializer for websocket messages"""

    message = MessageSerializer()
    event_type = serializers.CharField()

    class Meta:
        fields = "__all__"
