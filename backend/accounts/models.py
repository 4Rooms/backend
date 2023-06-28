import os
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Define a model manager for Custom User model without username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""

        if not email:
            raise ValueError("The given email must be set")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, PermissionsMixin):
    """Custom user model"""

    # we don't need username
    username = None
    # email should be unique
    email = models.EmailField(_("email address"), unique=True)
    is_email_confirmed = models.BooleanField(default=False)

    # for default authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


class EmailConfirmationToken(models.Model):
    """Token for email confirmation"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


def get_image_filename(instance, filename):
    """
    Function for upload_to arg in avatar field of profile.
    This will be called to obtain the upload path, including the filename.
    This callable must accept two arguments and return a Unix-style path (with
    forward slashes) to be passed along to the storage system.
    The two arguments are:
        - instance: an instance of the model where the FileField is defined.
          More specifically, this is the particular instance where the current file is being attached.
        - filename: The filename that was originally given to the file.
          This may be taken into account when determining the final destination path.
    """
    name = instance.avatar.name
    slug = slugify(name)
    return f"avatars/{slug}-{filename}"


class Profile(models.Model):
    """User profile"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=get_image_filename, blank=True)
    nickname = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return self.user.email

    @property
    def filename(self):
        return os.path.basename(self.image.name)
