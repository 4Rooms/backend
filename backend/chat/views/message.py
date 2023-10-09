import logging

from chat.models.chat import Chat
from chat.models.message import Message
from chat.permissions import (
    IsCreatorOrReadOnly,
    IsEmailConfirm,
    IsNotDeleted,
    IsOnlyTextInRequestData,
)
from chat.serializers.message import MessageSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(tags=["Message"]),
)
class MessagesApiView(generics.ListAPIView):
    """Get messages from the certain chat"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = MessageSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        """Get messages from the certain chat"""

        chat_id = self.kwargs["chat_id"]
        return Chat.objects.get(pk=chat_id).message_set.all()


@extend_schema_view(
    patch=extend_schema(tags=["Message"]),
    delete=extend_schema(tags=["Message"]),
)
class UpdateDeleteMessageApiView(generics.RetrieveUpdateDestroyAPIView):
    """Update text of message and Soft delete of message"""

    permission_classes = (IsAuthenticated, IsOnlyTextInRequestData, IsCreatorOrReadOnly, IsEmailConfirm, IsNotDeleted)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    http_method_names = ["patch", "delete"]
