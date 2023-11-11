import logging
from datetime import datetime
from urllib.parse import urlparse

from config.utils import get_ui_host, origin_from_host
from django.conf import settings
from jwt import decode
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def get_token_expire_time(access_token):
    """Get token expire time"""

    key = settings.SECRET_KEY
    algorithms = settings.SIMPLE_JWT["ALGORITHM"]
    decoded_access_token = decode(access_token, key, algorithms)
    token_exp_time = datetime.utcfromtimestamp(decoded_access_token["exp"])
    return token_exp_time


def get_hostname(request):
    ui_host = get_ui_host(request, always_frontend_ui=True)
    hostname = urlparse(ui_host).hostname
    logger.info(f"Host for cookie: {hostname}")
    return hostname


def set_auth_cookie(request, response: Response, jwt_token, url=None):
    """
    Set auth cookie
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie
    """
    logger.info(f"Setting cookie. User: {request.user.username}, url: {url}")

    cookie_host = urlparse(origin_from_host(urlparse(url).hostname)).hostname if url else get_hostname(request)
    secure = False if cookie_host == "localhost" else settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"]
    samesite = settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"] if secure else None

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=jwt_token,
        expires=get_token_expire_time(jwt_token),
        secure=secure,
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=samesite,
        domain=cookie_host if cookie_host != "localhost" else None,
    )

    logger.info(f"Set cookie. User: {request.user.username}, host: {cookie_host}, secure: {secure}")


def delete_auth_cookie(request, response: Response):
    response.delete_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        domain=get_hostname(request),
    )
