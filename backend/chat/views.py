import logging
from io import BytesIO

from chat.models import Chat, Message, SavedChat
from chat.permissions import (
    IsCreatorOrReadOnly,
    IsEmailConfirm,
    IsNotDeleted,
    IsOnlyTextInRequestData,
)
from chat.serializers import (
    ChatSerializer,
    ChatSerializerForChatUpdate,
    MessageSerializer,
    SavedChatSerializer,
)
from config.settings import CHOICE_ROOM
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.files.services.images import resize_image

logger = logging.getLogger(__name__)


class ChatAPIView(generics.GenericAPIView):
    """API to get/put chat"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["get", "post"]

    def get(self, request, room_name):
        """Get chat list from the certain room"""

        # if wrong room name
        if (room_name, room_name) not in CHOICE_ROOM:
            return Response({"Error": "wrong room"}, status=status.HTTP_400_BAD_REQUEST)

        # get chats, serialize, and return list of chats by pagination
        self.queryset = Chat.objects.filter(room=room_name)
        serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    def post(self, request, room_name):
        """Create Chat"""

        data = request.data.copy()
        data["room"] = room_name
        serializer = ChatSerializer(data=data)

        if serializer.is_valid():
            # Optional fields
            img = request.data.get("img", None)
            description = request.data.get("description", None)

            new_chat = Chat.objects.create(
                title=request.data["title"],
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


class UpdateDeleteChatApiView(generics.RetrieveUpdateDestroyAPIView):
    """Update chat description/image or delete chat"""

    permission_classes = (IsAuthenticated, IsCreatorOrReadOnly, IsEmailConfirm)
    queryset = Chat.objects.all()
    serializer_class = ChatSerializerForChatUpdate
    http_method_names = ["patch", "delete"]

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
            img = Image.open(chat_img)
            img_format = img.format

            if img.size != (200, 200):
                # Resize the image before saving it
                img = resize_image(img, 200)

                # Create a BytesIO object to store the resized image
                output = BytesIO()

                # Save the resized image to the BytesIO object in JPEG format
                img.save(output, format=img_format)

                # Move the cursor to the beginning of the BytesIO object
                output.seek(0)

                # Create a new InMemoryUploadedFile with the resized image
                resized_image = InMemoryUploadedFile(
                    output,
                    "ImageField",
                    f"{chat_img.name.split('.')[0]}.{img_format.lower()}",
                    f"image/{img_format.lower()}",
                    output.tell(),
                    None,
                )

                # Save the resized image
                serializer.validated_data["img"] = resized_image

        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class MessagesApiView(generics.ListAPIView):
    """Get messages from the certain chat"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = MessageSerializer
    http_method_names = ["get"]

    def get_queryset(self):
        """Get messages from the certain chat"""

        chat_id = self.kwargs["chat_id"]
        return Chat.objects.get(pk=chat_id).message_set.all()


class UpdateDeleteMessageApiView(generics.RetrieveUpdateDestroyAPIView):
    """Update text of message and Soft delete of message"""

    permission_classes = (IsAuthenticated, IsOnlyTextInRequestData, IsCreatorOrReadOnly, IsEmailConfirm, IsNotDeleted)
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    http_method_names = ["patch", "delete"]


class SavedChatApiView(generics.GenericAPIView):
    """Get/Post saved chat(s) for the user"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = SavedChatSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get", "post"]

    def get(self, request):
        """Get saved chats of users from request"""

        # get saved chats, serialize, and return list of chats by pagination
        self.queryset = SavedChat.objects.filter(user=request.user)
        serializer = SavedChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)

    def post(self, request):
        """Create a saved chat for the user from the request"""

        chat_id = request.data["chat_id"]
        chat = Chat.objects.get(pk=chat_id)
        saved_chat, _ = SavedChat.objects.get_or_create(user=request.user, chat=chat)
        return Response(
            {"saved_chat": SavedChatSerializer(saved_chat, context={"request": request}).data},
            status=status.HTTP_201_CREATED,
        )


class DeleteSavedChatApiView(generics.RetrieveUpdateDestroyAPIView):
    """Delete saved chat as saved"""

    permission_classes = (IsAuthenticated, IsCreatorOrReadOnly, IsEmailConfirm)
    queryset = SavedChat.objects.all()
    serializer_class = SavedChatSerializer
    http_method_names = ["delete"]


class MyChatsApiView(generics.GenericAPIView):
    """Get a list of chats created by the user (my chats)"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    serializer_class = ChatSerializer
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    http_method_names = ["get"]

    def get(self, request):
        """Get a list of chats created by the user (my chats)"""

        # get chats, serialize, and return list of chats by pagination
        self.queryset = Chat.objects.filter(user=request.user)
        serializer = ChatSerializer(self.queryset, context={"request": request}, many=True)
        page = self.paginate_queryset(serializer.data)
        return self.get_paginated_response(page)
