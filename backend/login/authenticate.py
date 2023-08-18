import logging

from django.conf import settings
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication"""

    def authenticate(self, request):
        raw_token = self._get_raw_token(request)

        if raw_token is None:
            logger.warning("No token found")
            return None, None

        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        logger.debug(f"User {user} authenticated")

        return user, validated_token

    def _get_raw_token(self, request_data):
        """
        Returns the raw token string that was used to authenticate the request.
        """

        raw_token = None

        if isinstance(request_data, Request):
            # http request
            raw_token = request_data.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"], None)

            if raw_token is None:
                header = self.get_header(request_data)
                raw_token = self.get_raw_token(header if header is not None else "")
        else:
            # websocket
            raw_token = self._get_auth_cookie_from_headers(request_data["headers"])

        return raw_token

    def _get_auth_cookie_from_headers(self, headers):
        """Get auth cookie from headers"""
        try:
            for header in headers:
                if header[0] == b"cookie":
                    for cookie in map(bytes.decode, header[1].split(b";")):
                        if cookie.strip().startswith(settings.SIMPLE_JWT["AUTH_COOKIE"]):
                            return cookie.split("=")[1]
        except Exception:
            return None

        return None
