import pytest
from django.urls import reverse

from .conftest import UserForTests


# run test with different origins
@pytest.mark.parametrize(
    "origin",
    [
        ("http://localhost:8000"),
        ("http://localhost:5173"),
        ("https://4rooms.pro"),
        ("https://back.4rooms.pro"),
        ("https://testback.4rooms.pro"),
        # Forbidden origins
        ("http://localhost:8080"),
        ("https://5rooms.pro"),
    ],
)
def test_register_user_view_is_working(client, test_user: UserForTests, origin):
    """Test user registration"""
    # user is registered in conftest.py

    # login
    url = reverse("login")
    body = {"username": test_user.username, "password": test_user.password}
    response = client.post(url, body, format="json", headers={"origin": origin})

    assert response.status_code == 200


def test_register_user_view_no_double_email(client, test_user: UserForTests):
    """Test that it is not possible to register a user with a used email"""
    # user is registered in conftest.py

    # create and post user
    # try to post user with same email
    url = reverse("register")
    body = {"username": test_user.username, "email": test_user.email, "password": test_user.password}
    response = client.post(url, body, format="json", headers={"origin": "http://localhost:8000"})
    assert response.status_code == 400
