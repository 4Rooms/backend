from typing import Optional

from chat.models.chat import Chat, SavedChat
from chat.models.chatLike import ChatLike
from files.utils import get_full_file_url
from rest_framework import serializers


class ChatSerializer(serializers.ModelSerializer):
    """Chat Serializer"""

    user = serializers.SerializerMethodField(source="get_user")
    img = serializers.SerializerMethodField(source="get_img")
    likes = serializers.SerializerMethodField(source="get_likes")

    class Meta:
        model = Chat
        fields = ["id", "title", "room", "img", "user", "description", "url", "timestamp", "likes"]
        read_only_fields = ["id", "user", "timestamp", "url", "room"]

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

    def get_img(self, obj) -> Optional[str]:
        """Return url of chat img"""

        if obj.img:
            return get_full_file_url(obj.img.url)

    @staticmethod
    def get_likes(obj) -> str:
        """Return number of likes"""

        return ChatLike.objects.filter(chat__pk=obj.pk).count()


class ChatSerializerForChatUpdate(ChatSerializer):
    """Chat Serializer for Update chat (Patch)"""

    class Meta:
        model = Chat
        fields = ["id", "title", "room", "img", "user", "description", "url", "timestamp", "likes"]
        read_only_fields = ["id", "user", "timestamp", "url", "title", "room", "likes"]
        extra_kwargs = {"description": {"required": False}, "img": {"required": False}}


class SavedChatSerializer(serializers.ModelSerializer):
    """Saved chat Serializer"""

    title = serializers.SerializerMethodField(source="get_title")
    room = serializers.SerializerMethodField(source="get_room")
    description = serializers.SerializerMethodField(source="get_description")
    chat_creator = serializers.SerializerMethodField(source="get_chat_creator")
    img = serializers.SerializerMethodField(source="get_img")
    url = serializers.SerializerMethodField(source="get_url")
    likes = serializers.SerializerMethodField(source="get_likes")

    class Meta:
        model = SavedChat
        fields = ["id", "user", "chat", "title", "room", "description", "chat_creator", "img", "url", "likes"]
        extra_kwargs = {"id": {"read_only": True}, "user": {"read_only": True}, "chat": {"read_only": True}}

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

    def get_img(self, obj) -> Optional[str]:
        """Return url of chat img"""

        if obj.chat:
            return get_full_file_url(obj.chat.img.url)

    @staticmethod
    def get_url(obj) -> Optional[str]:
        """Return url of chat (as WebSocket chat)"""

        if isinstance(obj, SavedChat):
            return obj.chat.url
        return None

    @staticmethod
    def get_likes(obj) -> str:
        """Return number of likes"""

        return ChatLike.objects.filter(chat__pk=obj.pk).count()
