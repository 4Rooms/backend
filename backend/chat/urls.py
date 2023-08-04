from django.urls import path

from backend.chat.views import ChatAPIView

urlpatterns = [
    path("chat/", ChatAPIView.as_view(), name="chat"),
]
