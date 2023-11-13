import logging

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
            header = self.get_header(request_data)
            raw_token = self.get_raw_token(header if header is not None else "")
        else:
            # websocket
            if isinstance(request_data, dict):
                headers = dict(request_data["headers"])
                if b"Authorization" in headers:
                    raw_token = self.get_raw_token(dict(request_data["headers"])[b"Authorization"])
                else:
                    if "query_string" in request_data:
                        token = request_data["query_string"].decode("utf-8").split("=")
                        if len(token) == 2:
                            if token[0] == "token":
                                raw_token = token[1]

        return raw_token
