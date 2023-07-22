"""
Custom strategy to:

- set is_email_confirmed to True when creating a user
- redirect to a custom url after login and set a cookie with JWT token

It is necessary to set SOCIAL_AUTH_STRATEGY to point to this class in settings.py
"""


from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy


class AuthStrategy(DjangoStrategy):
    def create_user(self, *args, **kwargs):
        user = super().create_user(*args, **{**kwargs, **{"is_email_confirmed": True}})
        return user

    def redirect(self, url):
        response = HttpResponseRedirect(resolve_url(url))

        user = self.request.user
        response.set_cookie(
            key=settings.SIMPLE_JWT["AUTH_COOKIE"],
            value=RefreshToken.for_user(user).access_token,
            expires=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"],
            secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
            httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
            samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        )

        return response
