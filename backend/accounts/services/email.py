import logging
import os
from urllib.parse import urlencode, urljoin

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_email_from_django(address, subject, message):
    """Send an email"""

    from_email = os.getenv("HOST_USER_EMAIL")
    res = send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[address],
        fail_silently=True,
    )
    logger.debug(f"Email sent to {address}. Result: {res}")
    return res


def send_confirmation_email(address: str, token_id: str, ui_host: str) -> int:
    """Send email with confirmation link"""

    url = urljoin(ui_host, "confirm-email/") + "?" + urlencode({"token_id": token_id})
    message = f"Please confirm your email by going to the following link: {url}"
    logging.debug(f"Sending confirmation email to {address}. Url: {url}")
    return send_email_from_django(address, subject="Please confirm email", message=message)


def send_password_reset_email(address: str, reset_password_token: str, ui_host: str):
    """Send email with password reset link"""

    url = urljoin(ui_host, "password-reset/") + "?" + urlencode({"token_id": reset_password_token})
    message = f"Password reset link: {url}"
    logging.debug(f"Sending password reset email to {address}. Url: {url}")
    return send_email_from_django(address, subject="Password reset", message=message)
