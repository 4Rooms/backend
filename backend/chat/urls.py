from django.urls import path

from backend.chat.views import (
    ChatAPIView,
    MessagesApiView,
    UpdateDeleteChatApiView,
    UpdateMessageApiView,
)

urlpatterns = [
    path("chat/<int:pk>/", UpdateDeleteChatApiView.as_view(), name="update_delete_chat"),
    path("chat/<str:room_name>/", ChatAPIView.as_view(), name="get_post_chats"),
    path("chat/<int:chat_id>/messages/", MessagesApiView.as_view(), name="get_messages"),
    path("chat/message/<int:pk>/", UpdateMessageApiView.as_view(), name="update_messages"),
]
