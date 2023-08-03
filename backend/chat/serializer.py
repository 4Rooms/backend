from chat.models import Chat
from rest_framework import serializers


class ChatSerializer(serializers.ModelSerializer):
    """Chat Serializer"""

    creator = serializers.SerializerMethodField(source="get_creator")
    img = serializers.SerializerMethodField(source="get_img")

    class Meta:
        model = Chat
        fields = ["id", "title", "room", "img", "creator", "description", "timestamp", "url"]
        extra_kwargs = {"id": {"read_only": True}, "creator": {"read_only": True}, "url": {"read_only": True}}

    def get_creator(self, obj):
        """Return creator username (instead id)"""

        return obj.creator.username

    def get_img(self, obj):
        """Return absolute url of chat img"""

        request = self.context.get("request")
        return request.build_absolute_uri(obj.img.url)
