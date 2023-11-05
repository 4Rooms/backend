import asyncio

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from chat.models.chat import Chat
from chat.models.message import Message
from config.asgi import application

from .conftest import get_msgs, print_msgs


@database_sync_to_async
def get_messages_from_db():
    res = []
    for msg in Message.objects.all():
        res.append(msg.__dict__)
    return res


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
async def test_message_update(settings, chat: Chat, user_factory, client_factory):
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

    #
    # send message 1
    #
    await client2.send_json_to(
        {
            "event_type": "chat_message",
            "message": {
                "chat": chat.id,
                "text": "test message",
            },
        }
    )

    await asyncio.sleep(1)
    await print_msgs([client1, client2, client3])

    db_msgs = await get_messages_from_db()
    assert len(db_msgs) == 1
    assert db_msgs[0]["text"] == "test message"
    assert db_msgs[0]["user_id"] == user2.id

    #
    # send message 2
    #
    await client1.send_json_to(
        {
            "event_type": "chat_message",
            "message": {
                "chat": chat.id,
                "text": "Another message",
            },
        }
    )

    await asyncio.sleep(1)
    await print_msgs([client1, client2, client3])

    db_msgs = await get_messages_from_db()
    assert len(db_msgs) == 2
    assert db_msgs[1]["text"] == "Another message"
    assert db_msgs[1]["user_id"] == user1.id

    #
    # update message 1
    #
    await client2.send_json_to(
        {
            "event_type": "message_was_updated",
            "id": db_msgs[0]["id"],
            "new_text": "updated text",
        }
    )

    await asyncio.sleep(1)
    c1_msgs = await get_msgs(client1)
    assert len(c1_msgs) == 1
    assert c1_msgs[0]["event_type"] == "message_was_updated"
    assert c1_msgs[0]["id"] == db_msgs[0]["id"]

    c2_msgs = await get_msgs(client2)
    assert len(c2_msgs) == 1
    assert c2_msgs[0]["event_type"] == "message_was_updated"
    assert c2_msgs[0]["id"] == db_msgs[0]["id"]

    c3_msgs = await get_msgs(client3)
    assert len(c3_msgs) == 1
    assert c3_msgs[0]["event_type"] == "message_was_updated"
    assert c3_msgs[0]["id"] == db_msgs[0]["id"]

    await print_msgs([client1, client2, client3])

    db_msgs = await get_messages_from_db()
    assert len(db_msgs) == 2
    assert db_msgs[0]["text"] == "updated text"
    assert db_msgs[0]["user_id"] == user2.id
    assert db_msgs[1]["text"] == "Another message"
    assert db_msgs[1]["user_id"] == user1.id

    await client2.disconnect()
    await client1.disconnect()
    await client3.disconnect()
