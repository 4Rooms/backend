from urllib.parse import urlencode

from accounts.models import EmailConfirmationToken
from django.contrib.auth import get_user_model
from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class ConfirmEmailApiViewTests(APITestCase):
    def test_confirm_email_view_is_working(self):
        """Test that get-request makes is_confirm_email=True"""

        # create and post user
        url = reverse("register")
        body = {"username": "user1", "email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")

        # Test that one message has been sent.
        self.assertEqual(len(mail.outbox), 1)

        email = mail.outbox[0]
        self.assertEqual(email.to, [body["email"]])
        self.assertEqual(email.subject, "Please confirm email")

        user = User.objects.filter(email=body["email"]).first()

        # get token for email confirmation
        token = EmailConfirmationToken.objects.filter(user=user).first()

        # get request for email confirm
        url = reverse("confirm-email")
        response = self.client.get(url + "?" + urlencode({"token_id": token.id}))
        self.assertEquals(response.status_code, 200)

        # login user
        url = reverse("login")
        body = {"username": "user1", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")
        self.assertEquals(response.status_code, 200)

        # get user info to check is_email_confirmed
        url = reverse("user")
        response = self.client.get(url, format="json")
        print(response.json())
        is_email_confirmed = response.json()["is_email_confirmed"]
        self.assertTrue(is_email_confirmed)
