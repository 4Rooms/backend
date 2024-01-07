import asyncio

import pytest
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from config.asgi import application
from django.test.client import Client
from django.urls import reverse

from .conftest import print_msgs


@pytest.mark.django_db(transaction=True, reset_sequences=True)
@pytest.mark.asyncio
async def test_saved_chats(client: Client, settings, chat_factory, user_factory, client_factory):
    # create user
    user1, t1 = await user_factory.create(username="u1", password="p", email="e1@4rooms.pro", is_email_confirmed=True)
    user2, t2 = await user_factory.create(username="u2", password="p", email="e2@4rooms.pro", is_email_confirmed=True)
    # create chat
    chat = await database_sync_to_async(chat_factory)(
        title="test chat", room="books", description="test description", user=user1
    )
    chat = await database_sync_to_async(chat_factory)(
        title="test chat1", room="books", description="test description", user=user1
    )
    chat = await database_sync_to_async(chat_factory)(
        title="test chat2", room="books", description="test description", user=user1
    )

    client1: WebsocketCommunicator = await client_factory.create(settings, application, chat, user1, t1)
    client2: WebsocketCommunicator = await client_factory.create(settings, application, chat, user2, t2)
    auth_header1 = {"Authorization": f"Bearer {t1}"}
    auth_header2 = {"Authorization": f"Bearer {t2}"}

    await asyncio.sleep(1)
    await print_msgs([client1])

    # like chat
    await client1.send_json_to(
        {
            "event_type": "chat_was_liked/unliked",
            "chat_id": chat.id,
        }
    )
    # await asyncio.sleep(1)
    await client2.send_json_to(
        {
            "event_type": "chat_was_liked/unliked",
            "chat_id": chat.id,
        }
    )
    await asyncio.sleep(1)
    await print_msgs([client1])

    # get chats
    url = reverse("get_chats", kwargs={"room_name": chat.room, "sorting_name": "new"})
    response = await database_sync_to_async(client.get)(url, headers=auth_header1)
    resp_data = response.json()
    print(resp_data)
    assert response.status_code == 200
    assert len(resp_data["results"]) == 3
    assert resp_data["results"][0]["id"] == chat.id
    assert resp_data["results"][0]["likes"] == 2

    # get saved chats
    url = reverse("get_saved_chats", kwargs={"room_name": chat.room})
    response = await database_sync_to_async(client.get)(url, headers=auth_header1)
    resp_data = response.json()
    print(resp_data)
    assert response.status_code == 200
    assert len(resp_data["results"]) == 0

    url = reverse("post_saved_chats")
    data = {"chat_id": chat.id}
    response = await database_sync_to_async(client.post)(url, data=data, headers=auth_header1)
    resp_data = response.json()
    print(resp_data)
    assert response.status_code == 201

    # get saved chats
    url = reverse("get_saved_chats", kwargs={"room_name": chat.room})
    response = await database_sync_to_async(client.get)(url, headers=auth_header1)
    resp_data = response.json()
    print(resp_data)
    assert response.status_code == 200
    assert len(resp_data["results"]) == 1
    assert resp_data["results"][0]["chat"] == chat.id
    assert resp_data["results"][0]["title"] == chat.title
    assert resp_data["results"][0]["description"] == chat.description
    assert resp_data["results"][0]["chat_creator"] == user1.username
    assert resp_data["results"][0]["likes"] == 2
    saved_chat_id = resp_data["results"][0]["id"]

    # delete saved chat
    url = reverse("delete_saved_chats", kwargs={"pk": saved_chat_id})
    response = await database_sync_to_async(client.delete)(url, headers=auth_header1)
    assert response.status_code == 204

    await client1.disconnect()
    await client2.disconnect()
