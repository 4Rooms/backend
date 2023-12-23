import base64
import logging
from io import BytesIO
from typing import Optional

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from chat.models.chat import Chat
from chat.models.chatLike import ChatLike
from chat.models.message import Message
from chat.models.onlineUser import OnlineUser
from chat.models.reaction import Reaction
from chat.serializers.message import MessageSerializer, WebsocketMessageSerializer
from django.core.files.uploadedfile import InMemoryUploadedFile
from files.services.file_upload import FileUploadService
from files.utils import get_full_file_url

logger = logging.getLogger(__name__)


class WesocketException(Exception):
    def __init__(self, error_message, message_id=None):
        self.error_message = error_message
        self.message_id = message_id


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self._user = self.scope["user"]

        if self._user is None:
            logger.debug(f"User is None. Rejecting connection")
            await self.close()
            return

        self._username = await self.get_user_username(self._user)

        logger.debug(f"User {self._user} wants to connect to websocket")

        self._room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self._chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self._group_name = f"{self._room_name}-{self._chat_id}"
        logger.info(f"CONNECT: User {self._user}. Chat {self._chat_id}. Channel: {self.channel_name}")

        await self.accept()
        # Send Event connected_user
        logger.debug(f"Sending connected_user event to chat: {self._chat_id} in room: {self._room_name}")
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
        logger.debug(f"Adding user to group: {self._group_name}")
        await self.channel_layer.group_add(self._group_name, self.channel_name)
        # Add user as online user in DB
        logger.debug(f"Adding user as online user in DB")
        await self.create_online_user()
        # Send yourself Event online_user_list
        logger.debug(f"Sending online_user_list event to chat: {self._chat_id} in room: {self._room_name}")
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
        logger.debug(
            f"Received msg."
            + f" User '{self._user}'."
            + f" Chat '{self._chat_id}'."
            + f" Room '{self._room_name}'."
            + f" Event '{content.get('event_type', None)}'."
            + f" ChatID: '{content.get('message', {}).get('chat', None)}'."
            + f" Text: '{content.get('message', {}).get('text', '')[:200]}'."
            + f" Attachments: '{len(content.get('message', {}).get('attachments', []))}'."
        )

        try:
            await self.process_received_content(content)
        except Exception as e:
            logger.error(f"Error while processing received content: {e}")
            data = {
                "event_type": "error",
                "error_message": f"Error in websocket processor: {e}",
                "details": {"user_id": self._user.id, "user_name": self._user.username, "chat_id": self._chat_id},
            }

            if isinstance(e, WesocketException):
                data["error_message"] = e.error_message
                if e.message_id is not None:
                    data["details"]["message_id"] = e.message_id

            await self.send_json(data)

    async def process_received_content(self, content):
        """Process received content"""

        # delete msg event
        if content.get("event_type", None) == "message_was_deleted" and content.get("id", None):
            logger.debug(f"Message_was_deleted event. Content: {content}")

            await self.delete_message(content["id"])
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
            logger.debug(f"Message_was_updated event. Content: {content}")

            # validate msg
            valid_message = await self._validate(
                {"event_type": "chat_message", "message": {"chat": self._chat_id, "text": content["new_text"]}}
            )

            await self.update_message(content["id"], content["new_text"])
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

        # delete chat event
        if content.get("event_type", None) == "chat_was_deleted":
            logger.debug(f"Chat_was_deleted event. Content: {content}")
            await self.delete_chat()
            await self.channel_layer.group_send(
                self._group_name,
                {
                    "type": "send_deleted_chat",
                    "event_type": content["event_type"],
                },
            )
            return

        # chat was liked event
        if content.get("event_type", None) == "chat_was_liked/unliked":
            logger.debug(f"chat_was_liked/unliked event. Content: {content}")

            event_type = await self.like_chat(self._user)
            await self.channel_layer.group_send(
                self._group_name,
                {
                    "type": "send_liked_chat",
                    "username": self._user.username,
                    "event_type": event_type,
                },
            )
            return

        # message reaction event
        if (
            content.get("event_type", None) == "message_reaction"
            and content.get("id", None)
            and content.get("reaction", None)
        ):
            logger.debug(f"message_reaction event. Content: {content}")

            event_type = await self.message_reaction(content["id"], content["reaction"], self._user)
            await self.channel_layer.group_send(
                self._group_name,
                {
                    "type": "send_message_reaction",
                    "id": content["id"],
                    "reaction": content["reaction"],
                    "username": self._user.username,
                    "event_type": event_type,
                },
            )
            return

        # Validate received msg
        valid_message = await self._validate(content)

        # Save valid msg to db
        saved_message = await self._save_message(valid_message, content.get("message", {}).get("attachments", []))

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
    def _validate(self, content) -> Optional[Message]:
        """Validate websocket message and chat message"""

        # Validate websocket message
        websocket_message = WebsocketMessageSerializer(data=content)
        if not websocket_message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Chat {self._chat_id}. {websocket_message.errors}")
            raise WesocketException("Invalid Websocket message: " + str(websocket_message.errors))

        # Validate chat message
        message = MessageSerializer(data=websocket_message.data["message"], context={"user": self._user})
        if not message.is_valid():
            logger.error(f"INVALID MESSAGE: User: {self._user}. Msg: {content}. Chat: {self._chat_id}.")
            raise WesocketException("Invalid message: " + str(message.errors))

        return message

    @database_sync_to_async
    def _save_message(self, message, attachments):
        """Save MSG to DB"""

        # save attachments
        files = []
        for attachment in attachments:
            logger.info(f"Processing attachment with name: '{attachment.get('name', None)}'")
            logger.debug(f" - Content sample: {attachment.get('content', None)[:64]}")

            if "name" not in attachment:
                raise WesocketException("Attachment name is required")

            if "content" not in attachment:
                raise WesocketException("Attachment content is required")

            file_name = attachment["name"]
            # each attachment is a dict with keys: name, content
            # 'attachments': [{'name': '2023-08-13_23-49.png', 'content': 'data:image/png;base64,iVBO...'}]
            try:
                _, data = attachment["content"].split(",", 1)
            except Exception:
                raise WesocketException("Attachment content is invalid")

            logger.debug(f" - Content length before decoding: {len(data)}")

            file_content = base64.b64decode(data)
            logger.debug(f" - Content length after decoding: {len(file_content)}")

            try:
                file_type = attachment["content"].split(";")[0].split("/")[1]
            except Exception:
                raise WesocketException("Attachment content is invalid")

            logger.debug(f" - File type: {file_type}")

            in_memory_file = InMemoryUploadedFile(
                file=BytesIO(file_content),
                field_name=None,
                name=file_name,
                content_type=file_type,
                size=len(file_content),
                charset=None,
            )

            service = FileUploadService(user=self._user, file_obj=in_memory_file)
            file = service.create()
            files.append(file)

        message.validated_data["attachments"] = files
        # save message
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
        event_type = event["event_type"]
        logger.debug(f"Send '{event_type}' to {self._user.username}, chat: {self._chat_id} in room: {self._room_name}")

        deleted_msg_event = {
            "event_type": event["event_type"],
            "id": event["id"],
        }

        await self.send_json(deleted_msg_event)

    async def send_updated_message(self, event):
        event_type = event["event_type"]
        logger.debug(f"Send '{event_type}' to {self._username}, chat: {self._chat_id}, room: {self._room_name}")

        updated_msg_event = {
            "event_type": event["event_type"],
            "id": event["id"],
            "new_text": event["new_text"],
        }

        await self.send_json(updated_msg_event)

    async def send_deleted_chat(self, event):
        event_type = event["event_type"]
        logger.debug(f"Send '{event_type}' to {self._username}, chat: {self._chat_id}, room: {self._room_name}")

        deleted_chat_event = {
            "event_type": event_type,
            "id": self._chat_id,
        }

        await self.send_json(deleted_chat_event)

    async def send_liked_chat(self, event):
        logger.debug(f"Event chat_was_liked. Sending liked Chat: {self._chat_id} by user: {event['username']}")
        liked_chat_event = {"event_type": event["event_type"], "id": self._chat_id, "user": event["username"]}
        await self.send_json(liked_chat_event)

    # send_message_reaction
    async def send_message_reaction(self, event):
        logger.debug(f"Sending msg reaction to chat: {self._chat_id} in room: {self._room_name}")

        msg_reaction_event = {
            "event_type": event["event_type"],
            "id": event["id"],
            "reaction": event["reaction"],
            "user": event["username"],
        }

        await self.send_json(msg_reaction_event)

    @database_sync_to_async
    def create_online_user(self):
        new, _ = OnlineUser.objects.get_or_create(user=self._user, chat_id=self._chat_id)

    @database_sync_to_async
    def delete_online_user(self):
        OnlineUser.objects.filter(user=self._user, chat_id=self._chat_id).delete()

    @database_sync_to_async
    def get_user_avatar(self, user):
        return get_full_file_url(user.profile.avatar.url)

    @database_sync_to_async
    def get_user_username(self, user):
        return user.username

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
                    "avatar": get_full_file_url(online_user.user.profile.avatar.url),
                }
            )
        return online_users

    @database_sync_to_async
    def get_message(self, id):
        msg = Message.objects.filter(pk=id).first()
        if msg:
            return msg

    @database_sync_to_async
    def delete_message(self, id):
        """Return True and delete msg if the user from request is a message author.
        Return False, if the user from the request isn't a message author or msg is absent"""

        msg = Message.objects.filter(pk=id).first()

        if not msg:
            logger.debug(f"Delete_message. The message with the specified ID is absent")
            raise WesocketException("Message with the specified ID was not found", id)

        # Is the user from the request isn't a message author
        if self._user.username != msg.user.username:
            logger.debug(f"Delete_message. The user from the request isn't a message author")
            raise WesocketException("You are not the author of this message", id)

        msg.delete()
        logger.debug(
            f"Delete_message. The Msg: {msg.id} was deleted from chat: {self._chat_id} in room: {self._room_name}"
        )
        return True

    @database_sync_to_async
    def update_message(self, id, new_text):
        """Return True and update msg if the user from request is a message author.
        Return False, if the user from the request isn't a message author, msg is absent"""

        msg = Message.objects.filter(pk=id).first()

        if not msg:
            logger.debug(f"Update_message. The message with the specified ID is absent")
            raise WesocketException("Message with the specified ID was not found", id)

        if msg.is_deleted:
            logger.debug(f"Update_message. A deleted message cannot be edited")
            raise WesocketException("A deleted message cannot be edited because it is deleted", id)

        # Is the user from the request isn't a message author
        if self._user.username != msg.user.username:
            logger.debug(f"Update_message. The user from the request isn't a message author")
            raise WesocketException("You are not the author of this message", id)

        msg.text = new_text
        msg.save()
        logger.debug(f"Update_message. The Msg: {msg.id} was updated in chat: {self._chat_id}, room: {self._room_name}")
        return True

    @database_sync_to_async
    def delete_chat(self):
        """Return True and delete chat if the user from request is a chat author.
        Return False, if the user from the request isn't a chat author"""

        chat = Chat.objects.get(pk=self._chat_id)

        # Is the user from the request isn't a chat author
        if self._user.username != chat.user.username:
            logger.debug(f"Delete_chat. The user from the request isn't a chat author")
            raise WesocketException("You are not the author of this chat")

        chat.delete()
        logger.debug(f"Delete_chat. The Chat: {self._chat_id} was deleted in room: {self._room_name}")
        return True

    # like_chat
    @database_sync_to_async
    def like_chat(self, user):
        """Return 'chat_was_liked' and save like in DB.
        Return 'chat_was_unliked' and del like if this user already liked this chat."""

        chat_like = ChatLike.objects.filter(user=user, chat_id=self._chat_id).first()
        logger.debug(f"Like_chat. The Chat: {self._chat_id} was liked in room: {self._room_name}")

        if not chat_like:
            new, _ = ChatLike.objects.get_or_create(user=user, chat_id=self._chat_id)
            logger.debug(f"Like_chat. The Chat: {self._chat_id} was liked in room: {self._room_name}")
            return "chat_was_liked"
        else:
            # If this user already liked this chat -> del this like
            chat_like.delete()
            logger.debug(f"Like_chat. The Chat: {self._chat_id} was unliked in room: {self._room_name}")
            return "chat_was_unliked"

    @database_sync_to_async
    def message_reaction(self, id, reaction, user):
        """Return 'message_reaction_was_posted' and save reaction in DB.
        Return 'message_reaction_was_deleted' and del reaction if this user already reacted this msg."""

        msg_reaction = Reaction.objects.filter(user=user, message_id=id).first()

        if not msg_reaction:
            new, _ = Reaction.objects.get_or_create(user=user, message_id=id, reaction=reaction)
            logger.debug(f"Message_reaction. The user: {user} msg: {id}, reaction: {reaction} was posted")
            return "message_reaction_was_posted"
        else:
            msg_reaction.delete()
            logger.debug(f"Message_reaction. The user: {user} msg: {id}, reaction: {reaction} was deleted")
            return "message_reaction_was_deleted"
