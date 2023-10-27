from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from jwt import decode
from rest_framework.response import Response


def get_token_expire_time(access_token):
    """Get token expire time"""

    key = settings.SECRET_KEY
    algorithms = settings.SIMPLE_JWT["ALGORITHM"]
    decoded_access_token = decode(access_token, key, algorithms)
    token_exp_time = datetime.utcfromtimestamp(decoded_access_token["exp"])
    return token_exp_time


def get_hostname():
    domain_url = settings.DJANGO_HOST
    hostname = urlparse(domain_url).hostname
    if hostname not in settings.ALLOWED_HOSTS:
        hostname = None

    if hostname in ["back.4rooms.pro", "testback.4rooms.pro"]:
        hostname = "4rooms.pro"


def set_auth_cookie(response: Response, jwt_token):
    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=jwt_token,
        expires=get_token_expire_time(jwt_token),
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        domain=get_hostname(),
    )


def delete_auth_cookie(response: Response):
    response.delete_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        domain=get_hostname(),
    )
