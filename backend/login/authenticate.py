import logging

from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


def token_portion(token):
    if token is None:
        return None
    return f"{str(token[:25])}...{str(token[-25:])}"


class CustomJWTAuthentication(JWTAuthentication):
    """Custom JWT authentication"""

    def authenticate(self, request):
        raw_token = None
        try:
            raw_token = self._get_raw_token(request)

            if raw_token is None:
                logger.warning(
                    f"No token found. Request: {request.method} {request.get_full_path()} {request.query_params} {request.data}"
                )
                return None, None

            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.debug(f"{user} authenticated with token {token_portion(raw_token)}")
        except Exception as e:
            logger.error(f"Authentication failed for token {raw_token}: {e}")
            raise e

        return user, validated_token

    def _get_raw_token(self, request_data):
        """
        Returns the raw token string that was used to authenticate the request.
        """

        raw_token = None

        if isinstance(request_data, Request):
            header = self.get_header(request_data)
            raw_token = self.get_raw_token(header if header is not None else "")
            logger.debug(f"Raw token found in request: {token_portion(raw_token)}")
        else:
            # websocket
            if isinstance(request_data, dict):
                headers = dict(request_data["headers"])
                if b"Authorization" in headers:
                    raw_token = self.get_raw_token(dict(request_data["headers"])[b"Authorization"])
                    logger.debug(f"Raw token found in Authorization header: {token_portion(raw_token)}")
                else:
                    if "query_string" in request_data:
                        token = request_data["query_string"].decode("utf-8").split("=")
                        if len(token) == 2:
                            if token[0] == "token":
                                raw_token = token[1]
                                logger.debug(f"Raw token found in query string: {token_portion(raw_token)}")

        return raw_token
