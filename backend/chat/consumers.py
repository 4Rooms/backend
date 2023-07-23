import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self._user = self.scope["user"]
        self._room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self._chat_name = self.scope["url_route"]["kwargs"]["chat_name"]
        self._group_name = f"{self._room_name}-{self._chat_name}"
        logger.info(
            f"User {self._user} connected to chat {self._chat_name} in room {self._room_name}. Channel: {self.channel_name}"
        )

        await self.accept()

        # Add a user to a group of users in that chat
        await self.channel_layer.group_add(self._group_name, self.channel_name)

    async def disconnect(self, code):
        logger.info(f"User {self._user} disconnected from chat {self._chat_name} in room {self._room_name}")
        await self.channel_layer.group_discard(self._group_name, self.channel_name)

    async def receive_json(self, content):
        logger.debug(f"User {self._user} sent message {content} to chat {self._chat_name} in room {self._room_name}")
        await self.channel_layer.group_send(
            self._group_name,
            {
                "type": "send_message",
                "message": content,
            },
        )

    async def send_message(self, event):
        logger.debug(f"Sending message {event['message']} to chat {self._chat_name} in room {self._room_name}")
        await self.send_json(event["message"])
