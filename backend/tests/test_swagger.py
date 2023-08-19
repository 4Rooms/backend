from django.test.client import Client
from django.urls import reverse

from .conftest import UserForTests


def test_swagger(client: Client, test_user: UserForTests):
    url = reverse("swagger-ui")

    response = client.get(url)
    assert response.status_code == 200

    url = "/api/schema/"
    response = client.get(url)
    assert response.status_code == 200
