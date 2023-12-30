import logging

from accounts.models import User
from django.db.models import Q

logger = logging.getLogger(__name__)


class AuthBackend(object):
    """
    Custom authentication backend.
    Allows users to login by email or username.
    """

    supports_object_permissions = True
    supports_anonymous_user = False
    # supports_inactive_user = False

    def get_user(self, user_id):
        """
        Overrides the get_user method to allow users to login by email or username.
        """

        try:
            user = User.objects.get(pk=user_id)
            logger.debug(f"{user} AuthBackend get_user")
            return user
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username, password):
        """
        Overrides the authenticate method to allow users to login by email or username.
        """

        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            logger.debug(f"{user} AuthBackend authenticate")
        except User.DoesNotExist:
            logger.error(f"User {username} does not exist")
            return None

        if user.check_password(password):
            logger.debug(f"{user} AuthBackend authenticate: return user")
            return user

        return None
