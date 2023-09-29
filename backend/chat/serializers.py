from chat.models import Chat, Message, SavedChat
from rest_framework import serializers
from typing import Optional


class ChatSerializer(serializers.ModelSerializer):
    """Chat Serializer"""

    user = serializers.SerializerMethodField(source="get_user")
    img = serializers.SerializerMethodField(source="get_img")

    class Meta:
        model = Chat
        fields = ["id", "title", "room", "img", "user", "description", "url", "timestamp"]
        extra_kwargs = {"id": {"read_only": True}, "user": {"read_only": True}}

    @staticmethod
    def update_url(obj, *args, **kwargs):
        """Update chat to save url with id"""

        obj.url = f"/chat/{obj.room}/{obj.pk}/"
        obj.save()
        return obj

    @staticmethod
    def get_user(obj) -> str:
        """Return username (instead id)"""

        if obj.user:
            return obj.user.username

    @staticmethod
    def get_img(obj) -> str:
        """Return url of chat img"""

        if obj.user:
            return obj.img.url


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
        read_only_fields = ["timestamp", "user"]

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

    @staticmethod
    def get_user_avatar(obj) -> Optional[str]:
        """Return URL to user avatar"""

        if isinstance(obj, Message):
            return obj.user.profile.avatar.url
        return None


class WebsocketMessageSerializer(serializers.Serializer):
    """Serializer for websocket messages"""

    message = MessageSerializer()
    event_type = serializers.CharField()

    class Meta:
        fields = "__all__"


class SavedChatSerializer(serializers.ModelSerializer):
    """Saved chat Serializer"""

    title = serializers.SerializerMethodField(source="get_title")
    room = serializers.SerializerMethodField(source="get_room")
    description = serializers.SerializerMethodField(source="get_description")
    chat_creator = serializers.SerializerMethodField(source="get_chat_creator")
    img = serializers.SerializerMethodField(source="get_img")
    url = serializers.SerializerMethodField(source="get_url")

    class Meta:
        model = SavedChat
        fields = ["user", "chat", "title", "room", "description", "chat_creator", "img", "url"]
        extra_kwargs = {"user": {"read_only": True}}

    @staticmethod
    def get_title(obj) -> Optional[str]:
        """Return chat title"""

        if isinstance(obj, SavedChat):
            return obj.chat.title
        return None

    @staticmethod
    def get_room(obj) -> Optional[str]:
        """Return chat room"""

        if isinstance(obj, SavedChat):
            return obj.chat.room
        return None

    @staticmethod
    def get_description(obj) -> Optional[str]:
        """Return chat description"""

        if isinstance(obj, SavedChat):
            return obj.chat.description
        return None

    @staticmethod
    def get_chat_creator(obj) -> Optional[str]:
        """Return chat creator"""

        if isinstance(obj, SavedChat):
            return obj.chat.user.username
        return None

    @staticmethod
    def get_img(obj) -> Optional[str]:
        """Return url of chat avatar"""

        if isinstance(obj, SavedChat):
            return obj.chat.img.url
        return None

    @staticmethod
    def get_url(obj) -> Optional[str]:
        """Return url of chat (as WebSocket chat)"""

        if isinstance(obj, SavedChat):
            return obj.chat.url
        return None
