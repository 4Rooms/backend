"""
Custom strategy to:

- set is_email_confirmed to True when creating a user
- redirect to a custom url after login and set a cookie with JWT token

It is necessary to set SOCIAL_AUTH_STRATEGY to point to this class in settings.py
"""


import logging
from urllib.parse import urljoin

from config.utils import get_ui_host
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from login.cookie import set_auth_cookie
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy

logger = logging.getLogger(__name__)


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

        redirect_url = resolve_url(url)
        response = HttpResponseRedirect(redirect_url)

        if redirect_url == settings.LOGIN_REDIRECT_URL:
            redirect_url = urljoin(get_ui_host(self.request), redirect_url)

        user = self.request.user
        token = RefreshToken.for_user(user).access_token
        set_auth_cookie(response, str(token))

        logger.info(f"Redirecting to {redirect_url}")
        return response
