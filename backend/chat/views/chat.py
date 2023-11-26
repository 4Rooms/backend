import logging

from chat.models.chat import Chat, SavedChat
from chat.permissions import IsCreatorOrReadOnly, IsEmailConfirm
from chat.serializers.chat import (
    ChatSerializer,
    ChatSerializerForChatUpdate,
    SavedChatSerializer,
)
from config.settings import CHOICE_ROOM
from django.conf import settings
from django.db.models import Count
from drf_spectacular.utils import extend_schema, extend_schema_view
from files.services.default_avatars import DefaultAvatars
from files.services.images import resize_in_memory_uploaded_file
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class ChatGetAPIView(generics.GenericAPIView):
    """API to get chats"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["get"]

    @extend_schema(
        tags=["Chat"],
    )
    def get(self, request, room_name, sorting_name):
        """Get a chat list from a certain room sorted by a certain criterion (sorting_name)"""

        logger.info(f"Get chat, room_name: {room_name}, sorting_name: {sorting_name}")

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": {"detail": "wrong room"}}, status=status.HTTP_400_BAD_REQUEST
            )

        # if wrong sorting_name name
        if sorting_name not in ["new", "popular", "old"]:
            return Response(
                {"type": "client_error", "errors": {"detail": "wrong sorting_name"}}, status=status.HTTP_400_BAD_REQUEST
            )

        # get chats, serialize, and return list of chats by pagination
        # sorting_name = new
        if sorting_name == "new":
            self.queryset = Chat.objects.filter(room=room_name).order_by("-timestamp")
            serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
            page = self.paginate_queryset(serializer.data)
            return self.get_paginated_response(page)
        # sorting_name = old
        if sorting_name == "old":
            self.queryset = Chat.objects.filter(room=room_name).order_by("timestamp")
            serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
            page = self.paginate_queryset(serializer.data)
            return self.get_paginated_response(page)
        # sorting_name = popular
        if sorting_name == "popular":
            self.queryset = (
                Chat.objects.filter(room=room_name).annotate(likes_number=Count("chatlike")).order_by("-likes_number")
            )
            serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
            page = self.paginate_queryset(serializer.data)
            return self.get_paginated_response(page)


class ChatPostAPIView(generics.GenericAPIView):
    """API to post chat"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["post"]

    @extend_schema(
        tags=["Chat"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "img": {"type": "string", "format": "binary"},
                },
            }
        },
    )
    def post(self, request, room_name):
        """Create Chat"""

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data["room"] = room_name
        serializer = ChatSerializer(data=data)

        if serializer.is_valid():
            # Optional fields
            img = data.get("img", None)
            if img:
                if img.size > settings.MAX_FILE_SIZE:
                    raise ValidationError(f"File size must be less than {settings.MAX_FILE_SIZE} bytes")
                img = resize_in_memory_uploaded_file(img, 200)
            else:
                img = DefaultAvatars().get_random_chat_avatar().as_posix()
                logger.info(f"Post chat. No image provided. Using default avatar: {img}")

            description = serializer.validated_data.get("description", None)

            new_chat = Chat.objects.create(
                title=serializer.validated_data["title"],
                room=room_name,
                user=request.user,
                img=img,
                description=description,
            )
            serializer.update_url(obj=new_chat)

            return Response(
                {"chat": ChatSerializer(new_chat, context={"request": request}).data}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    delete=extend_schema(tags=["Chat"]),
)
class UpdateDeleteChatApiView(generics.RetrieveUpdateDestroyAPIView):
    """Update chat description/image or delete chat. Now delete chat is WSocket event"""

    permission_classes = (IsAuthenticated, IsCreatorOrReadOnly, IsEmailConfirm)
    queryset = Chat.objects.all()
    serializer_class = ChatSerializerForChatUpdate
    http_method_names = ["patch", "delete"]

    @extend_schema(
        tags=["Chat"],
        request={
            "multipart/form-data": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "img": {"type": "string", "format": "binary"},
                },
            }
        },
    )
    def patch(self, request, *args, **kwargs):
        """Update chat description/image"""

        logger.info(f"PATCH CHAT: Request data: {request.data}")
        serializer = ChatSerializerForChatUpdate(self.get_object(), data=request.data, context={"request": request})

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        logger.debug(f"Validated date: {serializer.validated_data}")
        chat_img = serializer.validated_data.get("img", None)

        if chat_img:
            logger.debug(f"Chat img: {chat_img}")
            serializer.validated_data["img"] = resize_in_memory_uploaded_file(chat_img, 200)

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class GetSavedChatApiView(generics.GenericAPIView):
    """Get saved chat(s) for the user"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = SavedChatSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get", "post"]

    @extend_schema(
        tags=["Chat"],
    )
    def get(self, request, room_name):
        """Get saved chats of users from request"""

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        # get saved chats, serialize, and return list of chats by pagination
        self.queryset = SavedChat.objects.filter(user=request.user, chat__room=room_name).order_by("-id")
        serializer = SavedChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class PostSavedChatApiView(generics.GenericAPIView):
    """Post saved chat for the user"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = SavedChatSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["post"]

    @extend_schema(
        tags=["Chat"],
        request={
            "application/json": {
                "properties": {
                    "chat_id": {"type": "integer"},
                },
            }
        },
    )
    def post(self, request):
        """Create a saved chat for the user from the request"""

        chat_id = request.data["chat_id"]
        chat = Chat.objects.get(pk=chat_id)
        saved_chat, _ = SavedChat.objects.get_or_create(user=request.user, chat=chat)
        return Response(
            {"saved_chat": SavedChatSerializer(saved_chat, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema_view(
    delete=extend_schema(tags=["Chat"]),
)
class DeleteSavedChatApiView(generics.RetrieveUpdateDestroyAPIView):
    """Delete saved chat as saved"""

    permission_classes = (IsAuthenticated, IsCreatorOrReadOnly, IsEmailConfirm)
    queryset = SavedChat.objects.all()
    serializer_class = SavedChatSerializer
    http_method_names = ["delete"]


@extend_schema_view(
    get=extend_schema(tags=["Chat"]),
)
class MyChatsApiView(generics.GenericAPIView):
    """Get a list of chats created by the user (my chats)"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = ChatSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get"]

    def get(self, request, room_name):
        """Get a list of chats created by the user (my chats)"""

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        # get chats, serialize, and return list of chats by pagination
        self.queryset = Chat.objects.filter(user=request.user, room=room_name).order_by("-timestamp")
        serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class ChatSearchGetAPIView(generics.GenericAPIView):
    """API to get chats with searched phrase in title"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["get"]

    @extend_schema(
        tags=["Chat"],
    )
    def get(self, request, room_name, phrase):
        """Get a chat list from a certain room with searched phrase in title"""

        logger.info(f"Chat search, room_name: {room_name}, sorting_name: {phrase}")

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        # get chats, serialize, and return list of chats by pagination
        self.queryset = Chat.objects.filter(room=room_name, title__contains=phrase).order_by("-timestamp")
        serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class SavedChatSearchGetAPIView(generics.GenericAPIView):
    """API to get saved chats with searched phrase in title"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["get"]

    @extend_schema(
        tags=["Chat"],
    )
    def get(self, request, room_name, phrase):
        """Get a saved chat list from a certain room with searched phrase in title"""

        logger.info(f"Chat search, room_name: {room_name}, sorting_name: {phrase}")

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        # get chats, serialize, and return list of chats by pagination
        self.queryset = SavedChat.objects.filter(chat__room=room_name, chat__title__contains=phrase).order_by("-id")
        serializer = SavedChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)


class MyChatSearchGetAPIView(generics.GenericAPIView):
    """API to get my chats with searched phrase in title"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["get"]

    @extend_schema(
        tags=["Chat"],
    )
    def get(self, request, room_name, phrase):
        """Get my chat list from a certain room with searched phrase in title"""

        logger.info(f"Chat search, room_name: {room_name}, sorting_name: {phrase}")

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response(
                {"type": "client_error", "errors": [{"detail": "wrong room"}]}, status=status.HTTP_400_BAD_REQUEST
            )

        # get chats, serialize, and return list of chats by pagination
        self.queryset = Chat.objects.filter(user=request.user, room=room_name, title__contains=phrase).order_by("-id")
        serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)
