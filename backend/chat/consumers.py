import logging
from typing import Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chat.models import Message, OnlineUser
from chat.serializers import MessageSerializer, WebsocketMessageSerializer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self._user = self.scope["user"]

        logger.debug(f"User {self._user} wants to connect to websocket")

        self._room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self._chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self._group_name = f"{self._room_name}-{self._chat_id}"
        logger.info(f"CONNECT: User {self._user}. Chat {self._chat_id}. Channel: {self.channel_name}")

        # await self.get_online_users()

        await self.accept()
        # Send Event connected_user
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "send_connected_user",
                "user": {
                    "id": self._user.id,
                    "username": self._user.username,
                    "avatar": await self.get_user_avatar(self._user),
                },
            },
        )
        # Add a user to a group of users in that chat
        await self.channel_layer.group_add(self._group_name, self.channel_name)
        # Add user as online user in DB
        await self.create_online_user()
        # Send yourself Event online_user_list
        await self.send_online_user_list()

    async def disconnect(self, code):
        logger.info(f"DISCONNECT: User {self._user}. Chat {self._chat_id}. Room {self._room_name}")

        # Delete user as online user from DB
        await self.delete_online_user()
        # Send Event disconnected_user
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "send_disconnected_user",
                "user": {
                    "id": self._user.id,
                    "username": self._user.username,
                    "avatar": await self.get_user_avatar(self._user),
                },
            },
        )
        await self.channel_layer.group_discard(self._group_name, self.channel_name)

    async def receive_json(self, content):
        logger.debug(f"MESSAGE: User: {self._user}. Chat {self._chat_id}. Room {self._room_name}")

        saved_message = await self._validate_and_save(content)
        if saved_message is None:
            return

        # Send message to group
        msg_json = await self._serialize_message(saved_message)
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "send_message",
                "message": msg_json,
            },
        )

    @database_sync_to_async
    def _serialize_message(self, message) -> dict:
        return WebsocketMessageSerializer(instance={"message": message, "event_type": "chat_message"}).data

    @database_sync_to_async
    def _validate_and_save(self, content) -> Optional[Message]:
        # Validate websocket message
        websocket_message = WebsocketMessageSerializer(data=content)
        if not websocket_message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Chat {self._chat_id}. {websocket_message.errors}")
            return None

        # Validate chat message
        message = MessageSerializer(data=websocket_message.data["message"], context={"user": self._user})
        if not message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Msg: {content}. Chat {self._chat_id}.")
            return None

        # save
        return message.save()

    async def send_message(self, event):
        logger.debug(f"Sending message to chat {self._chat_id} in room {self._room_name}")
        await self.send_json(event["message"])

    async def send_connected_user(self, event):
        logger.debug(f"Event connected_user. Sending user joined to chat {self._chat_id} in room {self._room_name}")

        connected_event = {
            "event_type": "connected_user",
            "user": event["user"],
        }
        await self.send_json(connected_event)

    async def send_disconnected_user(self, event):
        logger.debug(
            f"Event disconnected_user. Sending user joined to chat user {self._chat_id} in room {self._room_name}"
        )
        disconnected_event = {
            "event_type": "disconnected_user",
            "user": event["user"],
        }
        await self.send_json(disconnected_event)

    async def send_online_user_list(self):
        logger.debug(f"Event online_user_list. Sending online users in chat {self._chat_id} in room {self._room_name}")

        online_users_event = {
            "event_type": "online_user_list",
            "user_list": await self.get_online_users(),
        }
        await self.send_json(online_users_event)

    @database_sync_to_async
    def create_online_user(self):
        new, _ = OnlineUser.objects.get_or_create(user=self._user, chat_id=self._chat_id)

    @database_sync_to_async
    def delete_online_user(self):
        OnlineUser.objects.filter(user=self._user, chat_id=self._chat_id).delete()

    @database_sync_to_async
    def get_user_avatar(self, user):
        return user.profile.avatar.url

    @database_sync_to_async
    def get_online_users(self):
        """Return list of online users in that chat excluding yourself"""

        querySet = OnlineUser.objects.filter(chat_id=self._chat_id).exclude(user=self._user)
        online_users = []

        for online_user in querySet:
            online_users.append(
                {
                    "id": online_user.user.id,
                    "username": online_user.user.username,
                    "avatar": online_user.user.profile.avatar.url,
                }
            )
        return online_users
