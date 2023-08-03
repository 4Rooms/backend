from chat.models import Chat
from chat.serializer import ChatSerializer
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class CreateChatAPIView(APIView):
    """API to create chat"""

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = ChatSerializer
    http_method_names = ["post"]

    def post(self, request):
        serializer = ChatSerializer(data=request.data)

        if serializer.is_valid():
            # Optional fields
            img = None if not "img" in request.data else request.data["img"]
            description = None if not "description" in request.data else request.data["description"]

            new_chat = Chat.objects.create(
                title=request.data["title"],
                room=request.data["room"],
                creator=request.user,
                img=img,
                description=description,
            )
            return Response({"chat": ChatSerializer(new_chat, context={"request": request}).data})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
