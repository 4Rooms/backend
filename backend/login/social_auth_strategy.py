"""
Custom strategy to:

- set is_email_confirmed to True when creating a user
- redirect to a custom url after login and set a JWT token

It is necessary to set SOCIAL_AUTH_STRATEGY to point to this class in settings.py
"""


import logging
from urllib.parse import urljoin, urlparse

from config.utils import get_ui_host
from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy

logger = logging.getLogger(__name__)


class AuthStrategy(DjangoStrategy):
    def create_user(self, *args, **kwargs):
        """
        Create a user and set is_email_confirmed to True
        """
        user = super().create_user(*args, **{**kwargs, **{"is_email_confirmed": True}})
        logger.info(f"{user} Social auth: create_user")
        return user

    def redirect(self, url):
        """
        Redirect to a custom url after login and set a JWT token
        """

        logger.info(f"Google auth redirecting to {url}")

        if urlparse(url).hostname == "accounts.google.com":
            logger.info(f"This is a redirect to Google auth")
            return HttpResponseRedirect(url)

        redirect_url = resolve_url(url)
        if redirect_url == settings.LOGIN_REDIRECT_URL:
            logger.info(f"Redirecting url is LOGIN_REDIRECT_URL")
            redirect_url = urljoin(get_ui_host(self.request, always_frontend_ui=True), redirect_url)
            logger.info(f"Setting redirect_url to {redirect_url}")

        user = self.request.user
        token = RefreshToken.for_user(user).access_token

        redirect_url = urljoin(redirect_url, f"?token={token}")
        response = HttpResponseRedirect(redirect_url)

        logger.info(f"Redirecting to {redirect_url}")
        return response
