import os
from urllib.parse import urlencode

from config.settings import UI_HOST
from django.core.mail import send_mail


def send_email_from_django(address, subject, message):
    """Send an email"""

    from_email = os.getenv("HOST_USER_EMAIL")
    send_mail(
        subject=subject,
        message=message,
        from_email=from_email,
        recipient_list=[address],
        fail_silently=True,
    )


def send_confirmation_email(email, token_id):
    """Send email with confirmation link"""

    url = UI_HOST + "confirm-email/" + "?" + urlencode({"token_id": token_id})
    message = f"Please confirm your email by going to the following link: {url}"
    send_email_from_django(email, subject="Please confirm email", message=message)


def send_password_reset_email(address, reset_password_token):
    """Send email with password reset link"""

    url = UI_HOST + "password-reset/" + "?" + urlencode({"token_id": reset_password_token})
    message = f"Password reset link: {url}"
    send_email_from_django(address, subject="Password reset", message=message)
