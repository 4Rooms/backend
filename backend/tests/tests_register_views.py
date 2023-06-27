from accounts.models import EmailConfirmationToken
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class RegisterUserAPIViewsTests(APITestCase):
    def test_register_user_view_is_working(self):
        """Test user registration"""

        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")
        # print(response)
        self.assertEquals(response.status_code, 201)

        user = User.objects.filter(email=body["email"]).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.check_password(body["password"]))

    def test_register_user_view_no_double_email(self):
        """Test that it is not possible to register a user with a used email"""

        # create and post user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")

        # try to post user with a used email
        response = self.client.post(url, body, format="json")
        # print("response", response.json())
        self.assertEquals(response.status_code, 400)

    def test_email_confirmation_token_is_created(self):
        """Test that an email confirmation token is created during the registration process"""

        # create and post user
        url = reverse("register")
        body = {"email": "user1@gmail.com", "password": "user1user1user1"}
        response = self.client.post(url, body, format="json")
        user = User.objects.filter(email=body["email"]).first()

        # check that token is created
        token = EmailConfirmationToken.objects.filter(user=user).first()
        self.assertIsNotNone(token)
