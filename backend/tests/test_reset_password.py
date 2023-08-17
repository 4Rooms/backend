import logging
import re

import pytest
from accounts.models import User
from django.core import mail
from django.test.client import Client
from django.urls import reverse

from .conftest import UserForTests


@pytest.mark.django_db
@pytest.mark.parametrize(
    "new_password, expected_error_type",
    [
        ("gxf1yAzl", None),  # valid password
        ("xf1yAzl", "validation_error"),  # too short
        ("", "validation_error"),  # blank
        ("password", "validation_error"),  # too common
        ("password123", "validation_error"),  # too common
    ],
)
def test_password_reset(client: Client, test_user: UserForTests, new_password, expected_error_type):
    """
    Test password reset

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user.email}, format="json")
    logging.debug(f"response: {response.json()}\n")

    assert response.status_code == 200

    email = mail.outbox[0]
    assert email.to[0] == test_user.email
    assert email.subject == "Password reset"
    logging.debug(f"Password reset email: \n{email.body}\n")

    # get token for password reset from email
    token = re.match(r".*http://.+/password-reset/\?token_id=(?P<token>.+)", email.body).groupdict()["token"]
    assert token is not None

    # reset password
    url = reverse("password_reset")
    body = {"token_id": token, "password": new_password}
    response = client.post(url, body, format="json")
    response_json = response.json()
    logging.debug(f"response: {response_json}\n")

    if expected_error_type is None:
        assert response.status_code == 200

        # check that password was changed
        user = User.objects.get(pk=test_user.django_user.pk)
        assert user.check_password(new_password)
    else:
        assert response.status_code == 400
        assert response_json["type"] == expected_error_type


@pytest.mark.django_db
@pytest.mark.parametrize(
    "token, expected_error_type, expected_message",
    [
        ("", "validation_error", "blank"),
        ("invalid_token", "validation_error", "Invalid token."),
        ("00000000-0000-0000-0000-000000000000", "validation_error", "Invalid token."),
    ],
)
def test_password_reset_with_invalid_token(
    client: Client, test_user: UserForTests, token: str, expected_error_type: str, expected_message: str
):
    """
    Test password reset with invalid token

    Args:
        client (fixture): django test client
        test_user (fixture): user with confirmed email (see conftest.py for details)
    """

    # The test client will return a 500 response as would be returned to a browser
    client.raise_request_exception = False

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user.email}, format="json")
    assert response.status_code == 200

    # reset password
    url = reverse("password_reset")
    body = {"token_id": token, "password": "new_password"}
    response = client.post(url, body, format="json")
    assert response.status_code == 400

    response_json = response.json()
    logging.debug(f"response: {response_json}\n")

    error_type = response_json["type"]
    assert error_type == expected_error_type


@pytest.mark.django_db
def test_password_reset_with_unconfirmed_email(client: Client, test_user_unconfirmed: UserForTests):
    """
    Test password reset with unconfirmed email

    Args:
        client (fixture): django test client
        test_user (fixture): user with unconfirmed email (see conftest.py for details)
    """

    # The test client will return a 500 response as would be returned to a browser
    client.raise_request_exception = False

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": test_user_unconfirmed.email}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json()["type"] == "validation_error"


@pytest.mark.django_db
def test_password_reset_with_nonexistent_email(client: Client):
    """
    Test password reset with nonexistent email

    Args:
        client (fixture): django test client
    """

    # The test client will return a 500 response as would be returned to a browser
    client.raise_request_exception = False

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": "nonexistent@email.com"}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json()["type"] == "validation_error"


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

    # The test client will return a 500 response as would be returned to a browser
    client.raise_request_exception = False

    # request password reset email
    url = reverse("request_password_reset")
    response = client.post(url, {"email": email}, format="json")

    # no emails should be sent
    assert mail.outbox == []

    assert response.status_code == 400
    assert response.json()["type"] == "validation_error"
