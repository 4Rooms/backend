"""
Custom strategy to redirect to frontend with token

It is necessary to set SOCIAL_AUTH_STRATEGY to point to this class in settings.py
"""

from urllib.parse import urlencode

from rest_framework_simplejwt.tokens import RefreshToken
from social_django.strategy import DjangoStrategy


class AuthStrategy(DjangoStrategy):
    def get_setting(self, name):
        if name == "LOGIN_REDIRECT_URL":
            user = self.request.user
            if user.is_authenticated:
                refresh = RefreshToken.for_user(user)
                token = str(refresh)

            return super().get_setting(name) + "?" + urlencode({"refresh_token": token})
        else:
            return super().get_setting(name)

    def create_user(self, *args, **kwargs):
        user = super().create_user(*args, **{**kwargs, **{"is_email_confirmed": True}})
        return user
