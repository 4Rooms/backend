import asyncio
import base64

import pytest
from channels.testing import WebsocketCommunicator
from chat.models.chat import Chat
from config.asgi import application
from django.test.client import Client

from .conftest import get_msgs, print_msgs


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.parametrize(
    "message, expected_error_message",
    [
        (
            {
                "event_type": "chat_message",
                "message": {
                    "chat": "",
                    "text": "",
                },
            },
            "message: text: This field may not be blank.\nchat: This field may not be null.",
        ),
        (
            {
                "event_type": "chat_message",
                "message": {
                    "chat": "",
                    "text": "text",
                },
            },
            "message: chat: This field may not be null.",
        ),
        (
            {
                "event_type": "chat_message",
                "message": {
                    "chat": None,
                    "text": "",
                },
            },
            "message: text: This field may not be blank.",
        ),
        (
            {
                "event_type": "chat_message",
            },
            "message: This field is required.",
        ),
        (
            {
                "event_type": "chat_message",
                "message": {
                    "chat": 8888,
                    "text": "text",
                },
            },
            'message: chat: Invalid pk "8888" - object does not exist.',
        ),
        (
            {
                "event_type": "chat_message",
                "message": {
                    "chat": None,
                    "text": "text",
                    "attachments": [
                        {
                            "name": "photo.png",
                            "content": f"data:image/png;base64,{base64.b64encode(b'a' *1024*1024*10)}",
                        }
                    ],
                },
            },
            "File 'photo.png' is too large: 11 MB. Must be less than 1 MB",
        ),
    ],
)
async def test_invalid_msgs(
    client: Client, settings, chat: Chat, user_factory, client_factory, message, expected_error_message
):
    #
    # create users
    #
    user1, t1 = await user_factory.create(username="u1", password="p", email="e1@4rooms.pro", is_email_confirmed=True)
    client1: WebsocketCommunicator = await client_factory.create(settings, application, chat, user1, t1)

    user2, t2 = await user_factory.create(username="u2", password="p", email="e2@4rooms.pro", is_email_confirmed=True)
    client2: WebsocketCommunicator = await client_factory.create(settings, application, chat, user2, t2)

    user3, t3 = await user_factory.create(username="u3", password="p", email="e3@4rooms.pro", is_email_confirmed=True)
    client3: WebsocketCommunicator = await client_factory.create(settings, application, chat, user3, t3)

    await asyncio.sleep(1)
    await print_msgs([client1, client2, client3])

    if "message" in message and message["message"]["chat"] is None:
        message["message"]["chat"] = chat.id
    await client2.send_json_to(message)

    await asyncio.sleep(1)

    c2_msgs = await get_msgs(client2)
    assert len(c2_msgs) == 1
    assert c2_msgs[0]["event_type"] == "error"
    assert c2_msgs[0]["error_message"] == expected_error_message

    c1_msgs = await get_msgs(client1)
    assert len(c1_msgs) == 0

    c3_msgs = await get_msgs(client3)
    assert len(c3_msgs) == 0

    await client2.disconnect()
    await client1.disconnect()
    await client3.disconnect()
