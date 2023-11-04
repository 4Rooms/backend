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


@pytest.mark.django_db
def test_confirm_email_view_is_working(client: Client, test_user: UserForTests):
    """
    Test that get-request makes is_confirm_email=True

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    # login user
    url = reverse("login")
    body = {"username": test_user.username, "password": test_user.password}

    logger.debug(f"Login user: {body}")
    response = client.post(url, body, format="json", headers={"origin": "http://localhost:8000"})

    logger.debug(f"Login response: {response.json()}")
    assert response.status_code == 200

    # get user info to check is_email_confirmed
    url = reverse("user")
    response = client.get(url, format="json")
    print(response.json())
    assert response.json()["is_email_confirmed"] is True


@pytest.mark.django_db
def test_resend_confirmation_email(client: Client, test_user_unconfirmed: UserForTests, django_user_model):
    """
    Test that the resend confirmation email endpoint sends an email.

    Args:
        client (Client): Django test client.
        test_user_unconfirmed (UserForTests): Unconfirmed user object.
        django_user_model (Model): Django user model.
    """

    # Clear outbox before sending email
    mail.outbox.clear()

    origin = "http://localhost:8000"
    # Send confirmation email
    url = reverse("send-confirmation-email")
    body = {"email": test_user_unconfirmed.email}
    response = client.post(url, body, format="json", headers={"origin": origin})

    # Check response
    assert response.status_code == 200
    assert response.json()["is_email_confirmed"] is False
    assert response.json()["email"] == test_user_unconfirmed.email

    # Check that one message has been sent
    assert len(mail.outbox) == 1

    # Check email details
    email = mail.outbox[0]
    assert email.to == [body["email"]]
    assert email.subject == "Please confirm email"

    # get token for password reset from email
    link = re.match(r".*(?P<link>http[s]?://[^\s]+)", email.body).groupdict()["link"]
    assert link is not None
    parsed = urlparse(link)
    assert parsed.scheme == "http"
    assert parsed.netloc == "localhost:8000"
    assert parsed.path == "/confirm-email/"
    token = parsed.query.split("=")[1]
    assert token is not None

    # Check that user exists
    user = django_user_model.objects.filter(email=body["email"]).first()
    assert user is not None

    # Check that token exists
    existing_token = EmailConfirmationToken.objects.filter(user=user).first()
    assert existing_token is not None
    assert existing_token.id == uuid.UUID(token)

    # Clear outbox after test
    mail.outbox.clear()


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
