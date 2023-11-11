import logging

from django.conf import settings
from django.http.request import split_domain_port
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def origin_from_host(host: str) -> str:
    """Return origin from host"""

    # split host into domain and port
    domain, _ = split_domain_port(host)

    if domain not in settings.ALLOWED_HOSTS:
        logger.error(f"Host {host} is not allowed")
        raise ValidationError("This host is not allowed")

    # find origin in CORS_ALLOWED_ORIGINS based on host
    for origin in settings.CORS_ALLOWED_ORIGINS:
        if host in origin:
            return origin

    raise ValidationError(f"Host {domain} is not allowed")


def get_ui_host(request: Request, always_frontend_ui=True) -> str:
    """Return UI host"""

    origin = None

    if origin is None:
        try:
            origin = request.headers.get("origin", None)
            logger.debug(f"Origin from headers: {origin}")
        except AttributeError:
            logger.error("AttributeError: request has no attribute 'headers'")
            raise ValidationError("Origin header is required")

    if origin is None:
        origin = origin_from_host(request.headers.get("Host", None))
        logger.debug(f"Origin from host: {origin}")

    logger.debug(f"Calculated origin: {origin}")

    if origin in settings.CORS_ALLOWED_ORIGINS:
        if always_frontend_ui:
            # for back.4rooms.pro and testback.4rooms.pro we want to return https://4rooms.pro
            if origin in ["https://back.4rooms.pro", "https://testback.4rooms.pro"]:
                return "https://4rooms.pro"

        logger.debug(f"Returning origin {origin}")
        return origin

    logger.error(f"Origin {origin} is not allowed")
    raise ValidationError("This origin is not allowed")
