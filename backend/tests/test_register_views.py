import pytest
from django.urls import reverse

from .conftest import UserForTests


# run test with different origins
@pytest.mark.parametrize(
    "origin, expected_cookie_domain",
    [
        ("http://localhost:8000", "localhost"),
        ("http://localhost:5173", "localhost"),
        ("https://4rooms.pro", "4rooms.pro"),
        ("https://back.4rooms.pro", "4rooms.pro"),
        ("https://testback.4rooms.pro", "4rooms.pro"),
        # Forbidden origins
        ("http://localhost:8080", None),
        ("https://5rooms.pro", None),
    ],
)
def test_register_user_view_is_working(client, test_user: UserForTests, origin, expected_cookie_domain):
    """Test user registration"""
    # user is registered in conftest.py

    # login
    url = reverse("login")
    body = {"username": test_user.username, "password": test_user.password}
    response = client.post(url, body, format="json", headers={"origin": origin})

    if expected_cookie_domain is None:
        assert response.status_code == 400
        return

    assert response.status_code == 200

    # check cookie
    assert "access_token" in response.cookies
    cookie = response.cookies["access_token"]
    assert cookie["domain"] == expected_cookie_domain


def test_register_user_view_no_double_email(client, test_user: UserForTests):
    """Test that it is not possible to register a user with a used email"""
    # user is registered in conftest.py

    # create and post user
    # try to post user with same email
    url = reverse("register")
    body = {"username": test_user.username, "email": test_user.email, "password": test_user.password}
    response = client.post(url, body, format="json", headers={"origin": "http://localhost:8000"})
    assert response.status_code == 400
