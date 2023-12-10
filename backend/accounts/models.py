import os
from pathlib import Path
from uuid import uuid4

from accounts.user_manager import UserManager
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


class User(AbstractUser, PermissionsMixin):
    """Custom user model"""

    # username should be unique
    username = models.CharField(
        _("login"),
        max_length=20,
        validators=[
            UnicodeUsernameValidator,
        ],
        unique=True,
    )
    # email should be unique
    email = models.EmailField(
        _("email"),
        unique=True,
    )
    is_email_confirmed = models.BooleanField(default=False)
    # extra fields
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    # for default authentication
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        ordering = ["-date_joined"]
        app_label = "accounts"

    def __str__(self):
        return f"{self.username}"


class EmailConfirmationToken(models.Model):
    """Token for email confirmation"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class PasswordResetToken(models.Model):
    """Token for email confirmation"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


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

    ava_dir = Path("avatars") / "uploads"
    if not ava_dir.exists():
        ava_dir.mkdir(parents=True)

    name = instance.avatar.name
    slug = slugify(name)
    return ava_dir / f"{slug}-{filename}"


class Profile(models.Model):
    """User profile"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(default="default-user-avatar.jpg", upload_to=get_image_filename, null=True)

    def __str__(self):
        return self.user.username

    @property
    def filename(self):
        return os.path.basename(self.avatar.name)


class ChangedEmail(models.Model):
    """New email for changing"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        app_label = "accounts"
