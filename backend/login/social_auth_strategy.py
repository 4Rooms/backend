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
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import resolve_url
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy

logger = logging.getLogger(__name__)


class AuthStrategy(DjangoStrategy):
    def __init__(self, storage, request=None, tpl=None):
        logger.debug(f"AuthStrategy init. Request: {request}")
        self.request = request

        # check if "state" is a query param
        if request and request.GET.get("state"):
            self.session_key = request.GET.get("state")

        self.session_key = self.random_string(32)
        if request and not hasattr(request, "session"):
            setattr(request, "session", None)

        super().__init__(storage, tpl)

    def create_user(self, *args, **kwargs):
        """
        Create a user and set is_email_confirmed to True
        """
        logger.debug(f"AuthStrategy create_user. Args: {args}, kwargs: {kwargs}, request: {self.request}")
        user = super().create_user(*args, **{**kwargs, **{"is_email_confirmed": True}})
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

    def build_absolute_uri(self, path=None):
        """
        Build absolute uri for given path
        """
        url = urljoin(settings.DJANGO_HOST, path or "")
        logger.debug(f"AuthStrategy build_absolute_uri. Url: {url}")
        return url

    def session_set(self, name, value):
        cache_key = f"custom_session_{self.session_key}_{name}"
        cache.set(cache_key, value, self.get_setting("SESSION_COOKIE_AGE"))

    def session_get(self, name, default=None):
        cache_key = f"custom_session_{self.session_key}_{name}"
        return cache.get(cache_key, default)

    def session_pop(self, name):
        cache_key = f"custom_session_{self.session_key}_{name}"
        return cache.delete(cache_key)

    def session_flush(self):
        cache_keys = cache.keys(f"custom_session_{self.session_key}_*")
        for cache_key in cache_keys:
            cache.delete(cache_key)
