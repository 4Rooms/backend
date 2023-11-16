from chat.views.chat import (
    ChatGetAPIView,
    ChatPostAPIView,
    DeleteSavedChatApiView,
    GetSavedChatApiView,
    MyChatsApiView,
    PostSavedChatApiView,
    UpdateDeleteChatApiView,
)
from chat.views.message import MessagesApiView, UpdateDeleteMessageApiView
from django.urls import path

urlpatterns = [
    path("chat/saved_chats/get/<str:room_name>/", GetSavedChatApiView.as_view(), name="get_saved_chats"),
    path("chat/saved_chats/delete/<int:pk>/", DeleteSavedChatApiView.as_view(), name="delete_saved_chats"),
    path("chat/saved_chats/post/", PostSavedChatApiView.as_view(), name="post_saved_chats"),
    path("chat/my_chats/get/<str:room_name>/", MyChatsApiView.as_view(), name="my_chats"),
    path("chat/get/<str:room_name>/<str:sorting_name>/", ChatGetAPIView.as_view(), name="get_chats"),
    path("chat/post/<str:room_name>/", ChatPostAPIView.as_view(), name="post_chat"),
    path("chat/update/<int:pk>/", UpdateDeleteChatApiView.as_view(), name="update_delete_chat"),
    path("chat/messages/get/<int:chat_id>/", MessagesApiView.as_view(), name="get_messages"),
    # It is WS event
    path("chat/message/update_delete/<int:pk>/", UpdateDeleteMessageApiView.as_view(), name="update_delete_message"),
]
