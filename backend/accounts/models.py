import os
from uuid import uuid4

from accounts.user_manager import UserManager
from django.conf import settings
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from PIL import Image


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


class EmailConfirmationToken(models.Model):
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

    name = instance.avatar.name
    slug = slugify(name)
    return f"avatars/{slug}-{filename}"


class Profile(models.Model):
    """User profile"""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(default="default-user-avatar.jpg", upload_to=get_image_filename, null=True)

    def __str__(self):
        return self.user.email

    def save(self, *args, **kwargs):
        """Override the save method of the model"""

        super().save(*args, **kwargs)

        if self.avatar.name == "default-user-avatar.jpg":
            return

        # open image
        img = Image.open(self.avatar.path)
        # resize image
        if img.size != (200, 200):
            img = self.resize_image(img, 200)
            img.save(self.avatar.path)

    @property
    def filename(self):
        return os.path.basename(self.image.name)

    @staticmethod
    def resize_image(image: Image, length: int) -> Image:
        """
        Resize an image to a square length x length. Return the resized image. It also crops
        part of the image; length: Width and height of the output image.
         Resizing strategy :
         1) resize the smallest side to the desired dimension (e.g. 200)
         2) crop the other side so as to make it fit with the same length as the smallest side (e.g. 200)
        """

        # If the height is bigger than width.
        if image.size[0] < image.size[1]:
            # this makes the width fit the LENGTH in pixels while conserving the ration.
            resized_image = image.resize((length, int(image.size[1] * (length / image.size[0]))))
            # amount of pixels to lose in total on the height of the image.
            required_loss = resized_image.size[1] - length
            # crop the height of the image so as to keep 300 pixels the center part.
            resized_image = resized_image.crop(
                box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2)
            )
            # we now have a length x length pixels image.

            return resized_image

        # If the width is bigger than the height.
        else:
            # this makes the height fit the LENGTH in pixels while conserving the ration.
            resized_image = image.resize((int(image.size[0] * (length / image.size[1])), length))
            # amount of pixels to lose in total on the width of the image.
            required_loss = resized_image.size[0] - length
            # crop the width of the image so as to keep 300 pixels of the center part.
            resized_image = resized_image.crop(
                box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length)
            )
            # we now have a length x length pixels image.

            return resized_image
