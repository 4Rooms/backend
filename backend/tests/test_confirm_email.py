import logging
import re
import uuid
from urllib.parse import urlparse

import pytest
from accounts.models import EmailConfirmationToken
from django.core import mail
from django.test.client import Client
from django.urls import reverse

from .conftest import UserForTests

logger = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "origin, expected_url, expected_cookie_domain",
    [
        ("http://localhost:8000", "http://localhost:8000/confirm-email/", ""),
        ("http://localhost:5173", "http://localhost:5173/confirm-email/", ""),
        ("https://4rooms.pro", "https://4rooms.pro/confirm-email/", "4rooms.pro"),
        ("https://back.4rooms.pro", "https://4rooms.pro/confirm-email/", "4rooms.pro"),
        ("https://testback.4rooms.pro", "https://4rooms.pro/confirm-email/", "4rooms.pro"),
    ],
)
def test_confirm_email_view_is_working(client: Client, django_user_model, origin, expected_url, expected_cookie_domain):
    """
    Test that get-request makes is_confirm_email=True

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    url = reverse("register")
    body = {"username": "user1", "email": "user1@gmail.com", "password": "user1user1user1"}
    response = client.post(url, body, format="json", headers={"origin": origin})
    assert response.status_code == 201

    # Test that one message has been sent.
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    mail.outbox.clear()
    assert email.to == [body["email"]]
    assert email.subject == "Please confirm email"
    link = re.match(r".*(?P<link>http[s]?://[^\s]+)", email.body).groupdict()["link"]
    assert link is not None
    parsed = urlparse(link)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == expected_url

    token = parsed.query.split("=")[1]
    assert token is not None

    user = django_user_model.objects.filter(email=body["email"]).first()
    assert user is not None

    # login user
    url = reverse("login")
    body = {"username": "user1", "password": "user1user1user1"}

    logger.debug(f"Login user: {body}")
    response = client.post(url, body, format="json", headers={"origin": origin})

    logger.debug(f"Login response: {response.json()}")
    assert response.status_code == 200

    # check cookie
    assert "access_token" in response.cookies
    cookie = response.cookies["access_token"]
    assert cookie["domain"] == expected_cookie_domain


@pytest.mark.django_db
@pytest.mark.parametrize(
    "origin, expected_url",
    [
        ("http://localhost:8000", "http://localhost:8000/confirm-email/"),
        ("http://localhost:5173", "http://localhost:5173/confirm-email/"),
        ("https://4rooms.pro", "https://4rooms.pro/confirm-email/"),
        ("https://back.4rooms.pro", "https://4rooms.pro/confirm-email/"),
        ("https://testback.4rooms.pro", "https://4rooms.pro/confirm-email/"),
        # Forbidden origins
        ("http://localhost:8080", None),
        ("https://5rooms.pro", None),
    ],
)
def test_resend_confirmation_email(
    client: Client, test_user_unconfirmed: UserForTests, django_user_model, origin, expected_url
):
    """
    Test that the resend confirmation email endpoint sends an email.

    Args:
        client (Client): Django test client.
        test_user_unconfirmed (UserForTests): Unconfirmed user object.
        django_user_model (Model): Django user model.
    """

    # Clear outbox before sending email
    mail.outbox.clear()

    # Send confirmation email
    url = reverse("send-confirmation-email")
    body = {"email": test_user_unconfirmed.email}
    response = client.post(url, body, format="json", headers={"origin": origin})

    if expected_url is None:
        assert response.status_code == 400
        return

    # Check response
    assert response.status_code == 200
    assert response.json()["is_email_confirmed"] is False
    assert response.json()["email"] == test_user_unconfirmed.email

    # Check that one message has been sent
    assert len(mail.outbox) == 1

    # Check email details
    email = mail.outbox[0]
    mail.outbox.clear()
    assert email.to == [body["email"]]
    assert email.subject == "Please confirm email"

    # get token for password reset from email
    link = re.match(r".*(?P<link>http[s]?://[^\s]+)", email.body).groupdict()["link"]
    assert link is not None
    parsed = urlparse(link)
    assert f"{parsed.scheme}://{parsed.netloc}{parsed.path}" == expected_url
    token = parsed.query.split("=")[1]
    assert token is not None

    # Check that user exists
    user = django_user_model.objects.filter(email=body["email"]).first()
    assert user is not None

    # Check that token exists
    existing_token = EmailConfirmationToken.objects.filter(user=user).first()
    assert existing_token is not None
    assert existing_token.id == uuid.UUID(token)


@pytest.mark.django_db
def test_resend_confirmation_email_not_existing_email(client: Client):
    """
    Test that the resend confirmation email endpoint sends an email.

    Args:
        client (Client): Django test client.
        test_user_unconfirmed (UserForTests): Unconfirmed user object.
    """

    # Clear outbox before sending email
    mail.outbox.clear()

    origin = "http://localhost:8000"
    url = reverse("send-confirmation-email")
    body = {"email": "test@example.com"}
    response = client.post(url, body, format="json", headers={"origin": origin})

    # Check response
    assert response.status_code == 400
    resp_json = response.json()
    assert resp_json["type"] == "validation_error"
    assert resp_json["errors"][0]["code"] == "invalid"
    assert resp_json["errors"][0]["detail"] == "User with this email does not exist"

    # Check that no message has been sent
    assert len(mail.outbox) == 0
