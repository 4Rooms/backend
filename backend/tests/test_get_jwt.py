from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class TokenObtainPairAPIViewsTests(APITestCase):
    def test_token_obtain_pair_view_is_working(self):
        """Test that token obtain pair is getting"""

        # create and post first user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")

        # get token for get user list request
        url = reverse("token_obtain_pair")
        response = self.client.post(url, data=body, format="json")
        token_obtain_pair = response.json()

        # print(token_obtain_pair)
        # access_token = response.json()["access"]
        # refresh_token = response.json()["refresh"]
        # print("Access token:", access_token)
        # print("Refresh token:", access_token)

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(token_obtain_pair), 2)
        self.assertTrue(token_obtain_pair["refresh"], True)
        self.assertTrue(token_obtain_pair["access"], True)
