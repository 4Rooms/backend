import logging

from django.conf import settings
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def get_ui_host(request: Request) -> str:
    """Return UI host"""

    try:
        origin = request.headers.get("origin")
    except AttributeError:
        logger.error("AttributeError: request has no attribute 'headers'")
        raise ValidationError("Origin header is required")

    if origin in settings.CORS_ALLOWED_ORIGINS:
        return origin

    logger.error(f"Origin {origin} is not allowed")
    raise ValidationError("This origin is not allowed")
