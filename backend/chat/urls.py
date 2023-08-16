from django.urls import path

from backend.chat.views import ChatAPIView, UpdateDeleteChatApiView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="create_chat"),
    path("chat/<int:pk>/", UpdateDeleteChatApiView.as_view(), name="update_delete_chat"),
    path("chat/<str:room_name>/", ChatAPIView.as_view(), name="get_post_chats"),
]
