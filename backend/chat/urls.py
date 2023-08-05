from django.urls import path
from backend.chat.views import ChatAPIView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="create_chat"),
    path("chat/<str:room_name>/", ChatAPIView.as_view(), name="get_chats"),
]
