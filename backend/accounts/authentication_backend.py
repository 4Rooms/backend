from django.db.models import Q

from .models import User


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
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, request, username, password):
        """
        Overrides the authenticate method to allow users to login by email or username.
        """

        try:
            user = User.objects.get(Q(username=username) | Q(email=username))
            print(user)

        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user

        else:
            return None
