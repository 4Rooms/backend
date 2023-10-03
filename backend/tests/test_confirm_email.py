import logging

from django.test.client import Client
from django.urls import reverse

from .conftest import UserForTests

logger = logging.getLogger(__name__)


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
