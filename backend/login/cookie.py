from datetime import datetime
from urllib.parse import urlparse

from django.conf import settings
from jwt import decode


def get_token_expire_time(access_token):
    """Get token expire time"""

    key = settings.SECRET_KEY
    algorithms = settings.SIMPLE_JWT["ALGORITHM"]
    decoded_access_token = decode(access_token, key, algorithms)
    token_exp_time = datetime.utcfromtimestamp(decoded_access_token["exp"])
    return token_exp_time


def set_auth_cookie(response, jwt_token):
    # set domain based on DJANGO_HOST
    domain_url = settings.DJANGO_HOST
    hostname = urlparse(domain_url).hostname
    if hostname not in settings.ALLOWED_HOSTS:
        hostname = None

    response.set_cookie(
        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
        value=jwt_token,
        expires=get_token_expire_time(jwt_token),
        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
        domain=hostname,
    )
