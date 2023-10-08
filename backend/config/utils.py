import logging

from django.conf import settings
from django.http.request import split_domain_port
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def _origin_from_host(host: str) -> str:
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


def get_ui_host(request: Request, always_frontend_ui=True) -> str:
    """Return UI host"""

    try:
        origin = request.headers.get("origin", None)
    except AttributeError:
        logger.error("AttributeError: request has no attribute 'headers'")
        raise ValidationError("Origin header is required")

    if origin is None:
        origin = _origin_from_host(request.headers.get("Host", None))

    if origin in settings.CORS_ALLOWED_ORIGINS:
        if always_frontend_ui:
            # for back.4rooms.pro and testback.4rooms.pro we want to return https://4rooms.pro
            if origin in ["https://back.4rooms.pro", "https://testback.4rooms.pro"]:
                return "https://4rooms.pro"

        return origin

    logger.error(f"Origin {origin} is not allowed")
    raise ValidationError("This origin is not allowed")
