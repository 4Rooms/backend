from django.urls import reverse

from .conftest import UserForTests


def test_register_user_view_is_working(client, test_user: UserForTests):
    """Test user registration"""
    # user is registered in conftest.py

    # login
    url = reverse("login")
    body = {"username": test_user.username, "password": test_user.password}
    response = client.post(url, body, format="json")
    assert response.status_code == 200


def test_register_user_view_no_double_email(client, test_user: UserForTests):
    """Test that it is not possible to register a user with a used email"""
    # user is registered in conftest.py

    # create and post user
    # try to post user with same email
    url = reverse("register")
    body = {"username": test_user.username, "email": test_user.email, "password": test_user.password}
    response = client.post(url, body, format="json")
    assert response.status_code == 400
