from config.settings import CHOICE_ROOM
from django.contrib.auth import get_user_model
from django.db import models
from PIL import Image


class Chat(models.Model):
    """Chat table"""

    title = models.CharField(max_length=70)
    room = models.CharField(choices=CHOICE_ROOM, max_length=50)
    img = models.ImageField(
        null=True,
        blank=True,
        default="default-user-avatar.jpg",
        upload_to="chat_img",
    )
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True, max_length=400)
    url = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "room",
            "title",
        )

    def __str__(self):
        return f"id: {self.pk}, title: {self.title}, room: {self.room}"

    def save(self, *args, **kwargs):
        """Redefined the save method to resize img"""

        # Save default chat img
        if not self.img:
            self.img = "default-user-avatar.jpg"

        # Save chat to DB
        super().save(*args, **kwargs)

        # Not resize the img if it is the default img
        if self.img.name == "default-user-avatar.jpg":
            return

        # Resize uploading by user img
        new_img = Image.open(self.img.path)
        if new_img.size != (200, 200):
            new_img = self.resize_image(new_img, 200)
            new_img.save(self.img.path)

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


class Message(models.Model):
    """Message table"""

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    text = models.TextField(max_length=1000)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"id: {self.pk}, chat: {self.chat}, user: {self.user}"
