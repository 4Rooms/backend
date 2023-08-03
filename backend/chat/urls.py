from django.urls import path

from backend.chat.views import CreateChatAPIView

urlpatterns = [
    path("create-chat/", CreateChatAPIView.as_view(), name="create_chat"),
]
