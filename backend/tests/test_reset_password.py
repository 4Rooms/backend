import re

import pytest
from accounts.models import User
from django.core import mail
from django.test.client import Client
from django.urls import reverse

from .conftest import UserForTests


@pytest.mark.django_db
def test_password_reset(client: Client, test_user: UserForTests):
    """
    Test password reset

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user.email}, format="json")
    assert response.status_code == 200

    email = mail.outbox[0]
    assert email.to[0] == test_user.email
    assert email.subject == "Password reset"
    print(f"\n\nPassword reset email:\n```\n{email.body}\n```\n")

    # get token for password reset from email
    token = re.match(r".*http://.+/password-reset/\?token_id=(?P<token>.+)", email.body).groupdict()["token"]
    assert token is not None

    # reset password
    url = reverse("password_reset")
    body = {"token_id": token, "password": "new_password"}
    response = client.post(url, body, format="json")
    assert response.status_code == 200

    # check that password was changed
    user = User.objects.get(pk=test_user.django_user.pk)
    assert user.check_password("new_password")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "token, expected_message",
    [
        ("", {"token_id": ["This field may not be blank."]}),
        ("invalid_token", "Validation error: ['“invalid_token” is not a valid UUID.']"),
        ("00000000-0000-0000-0000-000000000000", "Token does not exist"),
    ],
)
def test_password_reset_with_invalid_token(client: Client, test_user: UserForTests, token: str, expected_message):
    """
    Test password reset with invalid token

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user.email}, format="json")
    assert response.status_code == 200

    # reset password
    url = reverse("password_reset")
    body = {"token_id": token, "password": "new_password"}
    response = client.post(url, body, format="json")
    assert response.status_code == 400
    assert response.json() == {"message": expected_message}


@pytest.mark.django_db
def test_password_reset_with_unconfirmed_email(client: Client, test_user_unconfirmed: UserForTests):
    """
    Test password reset with unconfirmed email

    Args:
        client (fixture): django test client
        test_user (fixture): user with unconfirmed email (see conftest.py for details)
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user_unconfirmed.email}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json() == {"message": "Email is not confirmed."}


@pytest.mark.django_db
def test_password_reset_with_nonexistent_email(client: Client):
    """
    Test password reset with nonexistent email

    Args:
        client (fixture): django test client
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": "nonexistent@email.com"}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json() == {"message": "Email does not exist."}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "email", ["", "invalid_email", "invalid_email@", "invalid_email@invalid_domain", "invalid_email@invalid_domain."]
)
def test_password_reset_with_invalid_email(client: Client, email: str):
    """
    Test password reset with invalid email

    Args:
        client (fixture): django test client
        email (str): invalid email
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": email}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json() == {"email error": ["Enter a valid email address."]}
