import json
from typing import Tuple

import pytest
from accounts.models import User
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from chat.models.chat import Chat
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


async def wait_for_message(client: WebsocketCommunicator, timeout=5):
    nothing = await client.receive_nothing(timeout=timeout)
    return not nothing


async def print_msgs(clients):
    print("\n\n")
    for idx, client in enumerate(clients):
        while not client.output_queue.empty():
            data = await client.receive_json_from()
            print(f"client {idx} received: {json.dumps(data, indent=2)}\n")
    print("\n\n")


async def get_msgs(client: WebsocketCommunicator):
    res = []
    while not client.output_queue.empty():
        data = await client.receive_json_from()
        res.append(data)
        print(f"client received: {json.dumps(data, indent=2)}\n")
    return res


@database_sync_to_async
def create_user(**kwargs) -> Tuple[User, str]:
    user = get_user_model().objects.create_user(**kwargs)
    token = str(RefreshToken.for_user(user).access_token)
    return user, token


@pytest.fixture
def user_factory():
    class _factory:
        async def create(**kwargs) -> Tuple[User, str]:
            return await create_user(**kwargs)

    return _factory


@pytest.fixture
def chat_factory():
    def _factory(**kwargs):
        return Chat.objects.create(**kwargs)

    return _factory


@pytest.fixture
def chat(chat_factory):
    return chat_factory(title="test chat", room="books", description="test description")


@pytest.fixture
def client_factory():
    class _factory:
        async def create(settings, application, chat, user, access_token) -> WebsocketCommunicator:
            client = WebsocketCommunicator(
                application,
                f"/ws/chat/{chat.room}/{chat.id}/",
                headers=[
                    (b"origin", b"http://localhost:8000"),
                    (b"cookie", f"{settings.SIMPLE_JWT['AUTH_COOKIE']}={access_token}".encode()),
                ],
            )
            client.scope["user"] = user
            connected, subprotocol = await client.connect(timeout=20)
            print(f"connected: {connected}, subprotocol: {subprotocol}")
            assert connected
            return client

    return _factory
