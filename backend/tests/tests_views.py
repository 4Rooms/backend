from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class UserAPIViewsTests(APITestCase):
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
