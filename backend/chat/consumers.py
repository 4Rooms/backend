import logging
from typing import Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chat.models import Message
from chat.serializer import MessageSerializer, WebsocketMessageSerializer

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

        # Add a user to a group of users in that chat
        await self.channel_layer.group_add(self._group_name, self.channel_name)

    async def disconnect(self, code):
        logger.info(f"DISCONNECT: User {self._user}. Chat {self._chat_id}. Room {self._room_name}")
        await self.channel_layer.group_discard(self._group_name, self.channel_name)

    async def receive_json(self, content):
        logger.debug(f"MESSAGE: User: {self._user}. Chat {self._chat_id}. Room {self._room_name}")

        saved_message = await self._validate_and_save(content)
        if saved_message is None:
            return

        # Send message to group
        msg_json = WebsocketMessageSerializer(instance={"message": saved_message, "type": "chat_message"}).data
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "send_message",
                "message": msg_json,
            },
        )

    @database_sync_to_async
    def _validate_and_save(self, content) -> Optional[Message]:
        # Validate websocket message
        websocket_message = WebsocketMessageSerializer(data=content)
        if not websocket_message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Msg: {content}. Chat {self._chat_id}.")
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
