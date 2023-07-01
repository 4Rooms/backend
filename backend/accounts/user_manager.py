from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for Custom User model without username field."""

    def create_user(self, username, email, password=None, **extra_fields):
        """Create and save a User with the given username, email and password."""

        if not username:
            raise ValueError("Username must be set")

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given username, email and password."""

        user = self.create_user(username=username, email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save(using=self._db)
        return user
