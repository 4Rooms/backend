import os
from urllib.parse import urlencode, urljoin

from django.core.mail import send_mail
from django.urls import reverse


def send_confirmation_email(email, token_id):
    """Send an email for email confirmation"""

    from_email = os.getenv("HOST_USER_EMAIL")
    # host = os.getenv("DJANGO_HOST")

    # url = urljoin(host, reverse("confirm-email"))
    ui_host = "http://localhost:5173/"
    url = ui_host + "confirm-email/" + "?" + urlencode({"token_id": token_id})
    message = f"Please confirm your email by going to the following link: {url}"

    send_mail(
        subject="Please confirm email",
        message=message,
        from_email=from_email,
        recipient_list=[email],
        fail_silently=True,
    )
