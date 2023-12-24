import logging
import re

import requests
from django.conf import settings
from emails.models import DomainInfo, EmailInfo
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)


class EmailVerify:
    def __init__(self, email: str):
        self._email = email

    def check(self):
        email_info = self._get_email_info()
        if email_info is not None:
            if email_info.is_disposable:
                logger.error(f"Email {self._email} is disposable")
                raise ValidationError("Disposable emails are not allowed")

            if email_info.is_spam:
                logger.error(f"Email {self._email} is spam")
                raise ValidationError("Spam emails are not allowed")

        domain_info = self._get_domain_info()
        if domain_info is not None:
            if domain_info.is_spam:
                logger.error(f"Email {self._email} is spam")
                raise ValidationError("Spam emails are not allowed")

            if domain_info.country_code in settings.FORBIDDEN_COUNTRIES:
                logger.error(f"Email {self._email} is from forbidden country {domain_info.country_code}")
                raise ValidationError("Domains from this country are not allowed")

        # check that email does not match any pattern from FORBIDDEN_EMAILS
        for pattern in settings.FORBIDDEN_EMAILS:
            if re.match(pattern, self._email):
                logger.error(f"Email {self._email} is forbidden by pattern {pattern}")
                raise ValidationError("This email is forbidden by the server")

        # check email in EMA API
        email_info_from_api = self._get_email_info_from_api()
        if email_info_from_api is not None:
            email_info_from_api.save()
            if email_info_from_api.is_disposable:
                logger.error(f"Email {self._email} is disposable")
                raise ValidationError("Disposable emails are not allowed")

            if email_info_from_api.is_spam:
                logger.error(f"Email {self._email} is spam")
                raise ValidationError("Spam emails are not allowed")

        # check domain in EMA API
        domain_info_from_api = self._get_domain_info_from_api()
        if domain_info_from_api is not None:
            domain_info_from_api.save()
            if domain_info_from_api.is_spam:
                logger.error(f"Email {self._email} is spam")
                raise ValidationError("Spam emails are not allowed")

            if domain_info_from_api.country_code in settings.FORBIDDEN_COUNTRIES:
                logger.error(f"Email {self._email} is from forbidden country {domain_info_from_api.country_code}")
                raise ValidationError("Domains from this country are not allowed")

    def _get_email_info(self):
        # check if email is in the database
        try:
            email_info = EmailInfo.objects.get(email=self._email)
        except EmailInfo.DoesNotExist:
            email_info = None
        return email_info

    def _get_domain_info(self):
        try:
            domain = self._email.split("@")[1]
            domain_info = DomainInfo.objects.get(domain=domain)
        except Exception:
            domain_info = None
        return domain_info

    def _get_domain_info_from_api(self):
        if settings.EMA_DOMAIN_URL is None:
            return None

        try:
            domain = self._email.split("@")[1]
            response = requests.get(f"{settings.EMA_DOMAIN_URL}{self._email}")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Domain info from API: {data}")
                info = DomainInfo(
                    domain=domain,
                    country_code=data["location"]["country"],
                    is_spam=False,
                )
                return info
            else:
                return None
        except Exception as ex:
            logger.error(f"Error while getting domain info from API: {ex}")
            return None

    def _get_email_info_from_api(self):
        if settings.EMA_URL is None:
            return None

        try:
            response = requests.get(f"{settings.EMA_URL}{self._email}")
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Email info from API: {data}")
                info = EmailInfo(
                    email=self._email,
                    is_disposable=data["disposableCheck"] == "true",
                    is_spam=False,
                    is_free=data["freeCheck"] == "true",
                )
                return info
            else:
                return None
        except Exception as ex:
            logger.error(f"Error while getting email info from API: {ex}")
            return None
