import logging

from channels.db import database_sync_to_async
from chat.models.onlineUser import OnlineUser
from chat.views.chat import (
    ChatGetAPIView,
    ChatPostAPIView,
    ChatSearchGetAPIView,
    DeleteSavedChatApiView,
    GetSavedChatApiView,
    MyChatsApiView,
    MyChatSearchGetAPIView,
    PostSavedChatApiView,
    SavedChatSearchGetAPIView,
    UpdateDeleteChatApiView,
)
from chat.views.message import MessagesApiView, UpdateDeleteMessageApiView
from django.core.exceptions import SynchronousOnlyOperation
from django.db import connection
from django.urls import path

logger = logging.getLogger(__name__)

urlpatterns = [
    path("chat/saved_chats/get/<str:room_name>/", GetSavedChatApiView.as_view(), name="get_saved_chats"),
    path("chat/saved_chats/delete/<int:pk>/", DeleteSavedChatApiView.as_view(), name="delete_saved_chats"),
    path("chat/saved_chats/post/", PostSavedChatApiView.as_view(), name="post_saved_chats"),
    path("chat/my_chats/get/<str:room_name>/", MyChatsApiView.as_view(), name="my_chats"),
    path("chat/get/<str:room_name>/<str:sorting_name>/", ChatGetAPIView.as_view(), name="get_chats"),
    path("chat/post/<str:room_name>/", ChatPostAPIView.as_view(), name="post_chat"),
    path("chat/update/<int:pk>/", UpdateDeleteChatApiView.as_view(), name="update_delete_chat"),
    path("chat/messages/get/<int:chat_id>/", MessagesApiView.as_view(), name="get_messages"),
    # search
    path("chat/search/get/<str:room_name>/<str:phrase>/", ChatSearchGetAPIView.as_view(), name="get_searched_chats"),
    path(
        "chat/saved_chats/search/get/<str:room_name>/<str:phrase>/",
        SavedChatSearchGetAPIView.as_view(),
        name="get_searched_saved_chats",
    ),
    path(
        "chat/my_chats/search/get/<str:room_name>/<str:phrase>/",
        MyChatSearchGetAPIView.as_view(),
        name="get_searched_my_chats",
    ),
    # It is WS event
    path("chat/message/update_delete/<int:pk>/", UpdateDeleteMessageApiView.as_view(), name="update_delete_message"),
]


def delete_online_users():
    # checl if OnlineUsers table exists
    all_tables = connection.introspection.table_names()
    logger.info(f"Checking if OnlineUser table exists in DB: {all_tables}")
    if "chat_onlineuser" not in all_tables:
        logger.info("OnlineUser table does not exist - OK")
        return

    # delete online users if any
    count = OnlineUser.objects.all().count()
    if count > 0:
        logger.info(f"Found {count} online users - deleting all...")
        OnlineUser.objects.all().delete()
        logger.info("Deleted all online users")
    else:
        logger.info("No online users found - OK")


try:
    delete_online_users()
except SynchronousOnlyOperation:
    logger.info("Could not delete online users. Use async mode")
    database_sync_to_async(delete_online_users)()
