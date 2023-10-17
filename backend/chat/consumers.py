import logging
from typing import Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chat.models.message import Message
from chat.models.onlineUser import OnlineUser
from chat.serializers.message import MessageSerializer, WebsocketMessageSerializer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self._user = self.scope["user"]

        logger.debug(f"User {self._user} wants to connect to websocket")

        self._room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self._chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self._group_name = f"{self._room_name}-{self._chat_id}"
        logger.info(f"CONNECT: User {self._user}. Chat {self._chat_id}. Channel: {self.channel_name}")

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
        logger.debug(f"Received Event. User: {self._user}. Chat {self._chat_id}. Room {self._room_name}")

        # delete msg event
        if content.get("event_type", None) == "message_was_deleted" and content.get("id", None):
            logger.debug(f"Message_was_deleted event. MESSAGE: {content}")
            await self.channel_layer.group_send(
                self._group_name,
                {
                    "type": "send_deleted_message",
                    "id": content["id"],
                    "event_type": content["event_type"],
                },
            )
            return

        # update msg event
        if (
            content.get("event_type", None) == "message_was_updated"
            and content.get("id", None)
            and content.get("new_text", None)
        ):
            logger.debug(f"Message_was_updated event. MESSAGE: {content}")

            # validate msg
            valid_message = await self._validate(
                {"event_type": "chat_message", "message": {"chat": self._chat_id, "text": content["new_text"]}}
            )

            if valid_message is None:
                logger.debug(f"Update msg. Invalid msg.")
                return

            await self.channel_layer.group_send(
                self._group_name,
                {
                    "type": "send_updated_message",
                    "id": content["id"],
                    "new_text": content["new_text"],
                    "event_type": content["event_type"],
                },
            )
            return

        # Validate received msg
        valid_message = await self._validate(content)
        if valid_message is None:
            logger.debug(f"Invalid received msg")
            return

        # Save msg to db
        saved_message = await self._save_message(valid_message)

        # Send message to group before sending to group
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
    def _validate(self, content) -> Optional[Message]:
        # Validate websocket message
        websocket_message = WebsocketMessageSerializer(data=content)
        if not websocket_message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Chat {self._chat_id}. {websocket_message.errors}")
            return None

        # Validate chat message
        message = MessageSerializer(data=websocket_message.data["message"], context={"user": self._user})
        if not message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Msg: {content}. Chat: {self._chat_id}.")
            return None

        # save
        return message

    @database_sync_to_async
    def _save_message(self, message):
        """Save MSG to DB"""
        return message.save()

    async def send_message(self, event):
        logger.debug(f"Chat_message. Sending message to chat: {self._chat_id} in room: {self._room_name}")
        await self.send_json(event["message"])

    async def send_connected_user(self, event):
        logger.debug(f"Event connected_user. Sending user joined to chat: {self._chat_id} in room: {self._room_name}")

        connected_event = {
            "event_type": "connected_user",
            "user": event["user"],
        }
        await self.send_json(connected_event)

    async def send_disconnected_user(self, event):
        logger.debug(
            f"Event disconnected_user. Sending user joined to chat: {self._chat_id} in room: {self._room_name}"
        )
        disconnected_event = {
            "event_type": "disconnected_user",
            "user": event["user"],
        }
        await self.send_json(disconnected_event)

    async def send_online_user_list(self):
        logger.debug(
            f"Event online_user_list. Sending online users in chat: {self._chat_id} in room: {self._room_name}"
        )

        online_users_event = {
            "event_type": "online_user_list",
            "user_list": await self.get_online_users(),
        }
        await self.send_json(online_users_event)

    async def send_deleted_message(self, event):
        logger.debug(
            f"Event message_was_deleted. Sending deleted MSG to chat: {self._chat_id} in room: {self._room_name}"
        )

        deleted_msg_event = {
            "event_type": event["event_type"],
            "id": event["id"],
        }

        if await self.delete_message(event["id"]):
            await self.send_json(deleted_msg_event)

    async def send_updated_message(self, event):
        logger.debug(
            f"Event message_was_updated. Sending deleted MSG to chat: {self._chat_id} in room: {self._room_name}"
        )

        updated_msg_event = {
            "event_type": event["event_type"],
            "id": event["id"],
            "new_text": event["new_text"],
        }

        if await self.update_message(event["id"], event["new_text"]):
            await self.send_json(updated_msg_event)

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

    @database_sync_to_async
    def get_message(self, id):
        msg = Message.objects.get(pk=id)
        if msg:
            return msg

    @database_sync_to_async
    def delete_message(self, id):
        """Return True and delete msg if the user from request is a message author.
        Return False, if the user from the request isn't a message author or msg is absent"""

        msg = Message.objects.get(pk=id)

        if not msg:
            logger.debug(f"Delete_message. The message with the specified ID is absent")
            return False

        # Is the user from the request isn't a message author
        if self._user.username != msg.user.username:
            logger.debug(f"Delete_message. The user from the request isn't a message author")
            return False

        msg.delete()
        logger.debug(
            f"Delete_message. The Msg: {msg.id} was deleted from chat: {self._chat_id} in room: {self._room_name}"
        )
        return True

    @database_sync_to_async
    def update_message(self, id, new_text):
        """Return True and update msg if the user from request is a message author.
        Return False, if the user from the request isn't a message author, msg is absent"""

        msg = Message.objects.get(pk=id)

        if not msg:
            logger.debug(f"Update_message. The message with the specified ID is absent")
            return False

        if msg.is_deleted:
            logger.debug(f"Update_message. A deleted message cannot be edited")
            return False

        # Is the user from the request isn't a message author
        if self._user.username != msg.user.username:
            logger.debug(f"Update_message. The user from the request isn't a message author")
            return False

        msg.text = new_text
        msg.save()
        logger.debug(f"Update_message. The Msg: {msg.id} was updated in chat: {self._chat_id}, room: {self._room_name}")
        return True
