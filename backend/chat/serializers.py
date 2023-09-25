from chat.models import Chat, Message
from rest_framework import serializers


class ChatSerializer(serializers.ModelSerializer):
    """Chat Serializer"""

    user = serializers.SerializerMethodField(source="get_user")
    img = serializers.SerializerMethodField(source="get_img")

    class Meta:
        model = Chat
        fields = ["id", "title", "room", "img", "user", "description", "url", "timestamp"]
        extra_kwargs = {"id": {"read_only": True}, "user": {"read_only": True}}

    def update_url(self, obj, *args, **kwargs):
        """Update chat to save url with id"""

        obj.url = f"/chat/{obj.room}/{obj.pk}/"
        obj.save()
        return obj

    def get_user(self, obj) -> str:
        """Return username (instead id)"""

        if obj.user:
            return obj.user.username

    def get_img(self, obj) -> str:
        """Return absolute url of chat img"""

        request = self.context.get("request")
        return request.build_absolute_uri(obj.img.url)


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

    def get_user_name(self, obj) -> str:
        """Return username (instead id)"""

        if isinstance(obj, Message):
            return obj.user.username

        return None

    def get_user_avatar(self, obj) -> str:
        """Return URL to user avatar"""

        if isinstance(obj, Message):
            return obj.user.profile.avatar.url

        return None


class WebsocketMessageSerializer(serializers.Serializer):
    """Serializer for websocket messages"""

    message = MessageSerializer()
    type = serializers.CharField()
    event = serializers.CharField()

    class Meta:
        fields = "__all__"
