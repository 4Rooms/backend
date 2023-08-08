from django.urls import path

from backend.chat.views import ChatAPIView, UpdateChatApiView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="create_chat"),
    path("chat/<str:room_name>/", ChatAPIView.as_view(), name="get_chats"),
    path("chat/<str:room_name>/<int:pk>/", UpdateChatApiView.as_view(), name="update_chat"),
]
