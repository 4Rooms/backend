from urllib.parse import urlencode

import pytest
from accounts.models import EmailConfirmationToken, User
from django.core import mail
from django.test.client import Client
from django.urls import reverse


class UserForTests:
    def __init__(self, django_user: User, name: str, email: str, password: str):
        self.django_user = django_user
        self.username = name
        self.email = email
        self.password = password


@pytest.fixture
def test_user(client: Client, django_user_model):
    # create user
    url = reverse("register")
    body = {"username": "user1", "email": "user1@gmail.com", "password": "user1user1user1"}
    response = client.post(url, body, format="json")
    assert response.status_code == 201

    # Test that one message has been sent.
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    assert email.to == [body["email"]]
    assert email.subject == "Please confirm email"

    user = django_user_model.objects.filter(email=body["email"]).first()
    assert user is not None

    # get token for email confirmation
    token = EmailConfirmationToken.objects.filter(user=user).first()
    assert token is not None

    # get request for email confirm
    url = reverse("confirm-email")
    response = client.get(url + "?" + urlencode({"token_id": token.id}))
    assert response.status_code == 200

    mail.outbox.clear()
    return UserForTests(user, name=body["username"], email=body["email"], password=body["password"])
