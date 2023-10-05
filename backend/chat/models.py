from config.settings import CHOICE_ROOM
from django.contrib.auth import get_user_model
from django.db import models
from files.services.images import resize_image
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
            new_img = resize_image(new_img, 200)
            new_img.save(self.img.path)


class Message(models.Model):
    """Message table"""

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    text = models.TextField(max_length=1000, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"id: {self.pk}, chat: {self.chat}, user: {self.user}"

    def delete(self):
        """Soft delete: delete message text, is_deleted = True"""

        self.is_deleted = True
        self.text = "deleted"
        self.save()


class OnlineUser(models.Model):
    """The user who is currently in a certain chat"""

    user = models.ForeignKey(get_user_model(), related_name="group_user", on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, related_name="group_participant", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"user: {self.user}, chat: {self.chat}"


class SavedChat(models.Model):
    """Saved user's chat"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"id: {self.pk}, user: {self.user}, saved chat: {self.chat}"
