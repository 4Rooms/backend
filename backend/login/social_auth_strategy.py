"""
Custom strategy to:

- set is_email_confirmed to True when creating a user
- redirect to a custom url after login and set a cookie with JWT token

It is necessary to set SOCIAL_AUTH_STRATEGY to point to this class in settings.py
"""


from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from login.cookie import set_auth_cookie
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy


class AuthStrategy(DjangoStrategy):
    def create_user(self, *args, **kwargs):
        """
        Create a user and set is_email_confirmed to True
        """
        user = super().create_user(*args, **{**kwargs, **{"is_email_confirmed": True}})
        return user

    def redirect(self, url):
        """
        Redirect to a custom url after login and set a cookie with JWT token
        """
        response = HttpResponseRedirect(resolve_url(url))

        user = self.request.user
        token = RefreshToken.for_user(user).access_token
        set_auth_cookie(response, str(token))

        return response
