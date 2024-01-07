import logging
from urllib.parse import urlencode

import pytest
from accounts.models import EmailConfirmationToken
from django.core import mail
from django.test.client import Client
from django.urls import reverse

logger = logging.getLogger(__name__)

very_long_email = "veryveryveryveryveryveryveryveryveryveryveryverylongemailaddress@a4rooms.pro"


@pytest.mark.parametrize(
    "username, email_addr, password, login_name, expected_status_code",
    [
        ("user1", "test@4rooms.pro", "user1user1user1", "user1", 200),
        ("user1", "test@4rooms.pro", "user1user1user1", "test@4rooms.pro", 200),
        ("user1", very_long_email, "user1user1user1", "user1", 200),
        ("user1", very_long_email, "user1user1user1", very_long_email, 200),
    ],
)
def test_login(
    client: Client,
    username: str,
    email_addr: str,
    password: str,
    login_name: str,
    expected_status_code: int,
    django_user_model,
):
    """Test login"""

    # create user
    url = reverse("register")
    body = {"username": username, "email": email_addr, "password": password}
    response = client.post(url, body, format="json", headers={"origin": "http://localhost:8000"})
    assert response.status_code == 201

    # Test that one message has been sent.
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    assert email.to == [email_addr]
    assert email.subject == "Please confirm email"

    user = django_user_model.objects.filter(email=email_addr).first()
    assert user is not None

    mail.outbox.clear()

    # get token for email confirmation
    token = EmailConfirmationToken.objects.filter(user=user).first()
    assert token is not None

    # get request for email confirm
    url = reverse("confirm-email")
    response = client.get(url + "?" + urlencode({"token_id": token.id}))
    assert response.status_code == 200

    mail.outbox.clear()

    # login
    url = reverse("login")
    body = {"username": login_name, "password": password}
    response = client.post(url, body, format="json", headers={"origin": "http://localhost:8000"})
    assert response.status_code == expected_status_code
