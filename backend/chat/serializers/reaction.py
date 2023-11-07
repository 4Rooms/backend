from typing import Optional

from chat.models.reaction import Reaction
from rest_framework import serializers


class ReactionSerializer(serializers.ModelSerializer):
    """Serializer for message reaction"""

    user_name = serializers.SerializerMethodField(source="get_user_name")

    class Meta:
        model = Reaction
        fields = "__all__"
        read_only_fields = ["id", "message", "user", "reaction", "timestamp",]

    @staticmethod
    def get_user_name(obj) -> Optional[str]:
        """Return username (instead user)"""

        if isinstance(obj, Reaction):
            return obj.user.username
        return None
