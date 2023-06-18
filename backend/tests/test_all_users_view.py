from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPIViewsTests(APITestCase):
    def test_all_users_view_is_working(self):
        """Test that All Users View gets user list"""

        # create and post first user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")

        # create and post second user
        body = {"email": "user2@gmail.com", "password": "user2user2user2"}
        response = self.client.post(url, body, format="json")

        # get token for get user list request
        url = reverse("token_obtain_pair")
        response = self.client.post(url, data=body, format="json")
        access_token = response.json()["access"]
        # print("Acces token:", access_token)
        header = {"Authorization": f"Bearer {access_token}"}

        # get user list
        url = reverse("get_user_list")
        response = self.client.get(url, headers=header, format="json")
        # print("response", response.status_code, response.json())
        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.json()), 2)
        self.assertEquals(response.json()[0]["email"], "user1@gmail.com")
        self.assertEquals(response.json()[1]["id"], 2)

    def test_all_users_view_not_working_without_right_token(self):
        """Test that All Users View doesn't work without right token"""

        # create and post first user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")

        # bed token for get user list request
        access_token = "dh728dj"
        header = {"Authorization": f"Bearer {access_token}"}

        # get user list with bad token
        url = reverse("get_user_list")
        response = self.client.get(url, headers=header, format="json")
        # print("response", response.status_code, response.json())
        self.assertEquals(response.status_code, 401)

        # get user list without token
        response = self.client.get(url, format="json")
        # print("response", response.status_code, response.json())
        self.assertEquals(response.status_code, 401)
