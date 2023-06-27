from urllib.parse import urlencode

from accounts.models import EmailConfirmationToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class ConfirmEmailApiViewTests(APITestCase):
    def test_confirm_email_view_is_working(self):
        """Test that get-request makes is_confirm_email=True"""

        # create and post user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")
        user = User.objects.filter(email=body["email"]).first()

        # get token for email confirmation
        token = EmailConfirmationToken.objects.filter(user=user).first()

        # get request for email confirm
        url = reverse("confirm-email")
        response = self.client.get(url + "?" + urlencode({"token_id": token.id}))
        self.assertEquals(response.status_code, 200)

        # get token for get user info
        url = reverse("token_obtain_pair")
        response = self.client.post(url, data=body, format="json")
        token_obtain_pair = response.json()
        access_token = token_obtain_pair["access"]
        # print(access_token)

        # get user info to check is_email_confirm
        url = reverse("get_current_user")
        headers = {"Authorization": "Bearer " + access_token}
        response = self.client.get(url, headers=headers, format="json")
        print(response.json())
        is_email_confirmed = response.json()["is_email_confirmed"]
        self.assertTrue(is_email_confirmed)
