import logging

from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication"""

    def authenticate(self, request):
        header = self.get_header(request)

        if header is None:
            # get token from cookies
            raw_token = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE"]) or None
            logger.debug(f"Got auth cookie: {raw_token}")
        else:
            # get token from header
            raw_token = self.get_raw_token(header)
            logger.debug(f"Got auth header: {raw_token}")

        if raw_token is None:
            logger.warning("No token found")
            return None

        validated_token = self.get_validated_token(raw_token)
        logger.debug(f"Got validated token: {validated_token}")

        user = self.get_user(validated_token)
        logger.debug(f"User {user} authenticated")

        return user, validated_token
