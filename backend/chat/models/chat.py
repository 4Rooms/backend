from config.settings import CHOICE_ROOM
from django.contrib.auth import get_user_model
from django.db import models


class Chat(models.Model):
    """Chat table"""

    title = models.CharField(max_length=50)
    room = models.CharField(choices=CHOICE_ROOM, max_length=50)
    img = models.ImageField(
        null=True,
        blank=True,
        upload_to="chat_img",
    )
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.CASCADE)
    description = models.TextField(max_length=200)
    url = models.CharField(max_length=50, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (
            "room",
            "title",
        )
        app_label = "chat"

    def __str__(self):
        return f"id: {self.pk}, title: {self.title}, room: {self.room}"


class SavedChat(models.Model):
    """Saved user's chat"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"id: {self.pk}, user: {self.user}, saved chat: {self.chat}"

    class Meta:
        app_label = "chat"
