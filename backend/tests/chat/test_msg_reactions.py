import asyncio

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from chat.models.chat import Chat
from chat.models.message import Message
from config.asgi import application
from django.test.client import Client

from .conftest import get_msgs, print_msgs, wait_for_message


@database_sync_to_async
def get_message_reactions(id):
    res = []
    msg = Message.objects.get(id=id)
    for reaction in msg.reaction_set.all():
        res.append(reaction.__dict__)
    return res


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
async def test_message_reaction(client: Client, settings, chat: Chat, user_factory, client_factory):
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
    # send message
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

    message_available = await wait_for_message(client1)
    assert message_available
    c1_msgs = await get_msgs(client1)
    assert len(c1_msgs) == 1
    msg_id = c1_msgs[0]["message"]["id"]

    await print_msgs([client1, client2, client3])

    #
    # add reaction
    #
    reaction_msg_data = {
        "event_type": "message_reaction",
        "id": msg_id,
        "reaction": "😀",
    }
    await client1.send_json_to(reaction_msg_data)

    message_available = await wait_for_message(client1)
    assert message_available
    c1_msgs = await get_msgs(client1)
    assert len(c1_msgs) == 1
    assert c1_msgs[0]["event_type"] == "message_reaction_was_posted"
    assert c1_msgs[0]["reaction"] == "😀"
    assert c1_msgs[0]["user"] == user1.username

    message_available = await wait_for_message(client2)
    assert message_available
    c2_msgs = await get_msgs(client2)
    assert len(c2_msgs) == 1
    assert c2_msgs[0]["event_type"] == "message_reaction_was_posted"
    assert c2_msgs[0]["reaction"] == "😀"
    assert c2_msgs[0]["user"] == user1.username

    message_available = await wait_for_message(client3)
    assert message_available
    c3_msgs = await get_msgs(client3)
    assert len(c3_msgs) == 1
    assert c3_msgs[0]["event_type"] == "message_reaction_was_posted"
    assert c3_msgs[0]["reaction"] == "😀"
    assert c3_msgs[0]["user"] == user1.username

    reactions = await get_message_reactions(msg_id)
    for reaction in reactions:
        print(reaction)
    assert len(reactions) == 1
    assert reactions[0]["reaction"] == "😀"
    assert reactions[0]["user_id"] == user1.id
    assert reactions[0]["message_id"] == msg_id

    #
    # remove reaction
    #
    await client1.send_json_to(reaction_msg_data)

    message_available = await wait_for_message(client1)
    assert message_available
    c1_msgs = await get_msgs(client1)
    assert len(c1_msgs) == 1
    assert c1_msgs[0]["event_type"] == "message_reaction_was_deleted"
    assert c1_msgs[0]["reaction"] == "😀"
    assert c1_msgs[0]["user"] == user1.username

    message_available = await wait_for_message(client2)
    assert message_available
    c2_msgs = await get_msgs(client2)
    assert len(c2_msgs) == 1
    assert c2_msgs[0]["event_type"] == "message_reaction_was_deleted"
    assert c2_msgs[0]["reaction"] == "😀"
    assert c2_msgs[0]["user"] == user1.username

    message_available = await wait_for_message(client3)
    assert message_available
    c3_msgs = await get_msgs(client3)
    assert len(c3_msgs) == 1
    assert c3_msgs[0]["event_type"] == "message_reaction_was_deleted"
    assert c3_msgs[0]["reaction"] == "😀"
    assert c3_msgs[0]["user"] == user1.username

    reactions = await get_message_reactions(msg_id)
    for reaction in reactions:
        print(reaction)
    assert len(reactions) == 0

    # read remaining messages
    await print_msgs([client1, client2, client3])

    await client2.disconnect()
    await client1.disconnect()
    await client3.disconnect()
