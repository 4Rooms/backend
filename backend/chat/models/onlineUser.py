from chat.models.chat import Chat
from django.contrib.auth import get_user_model
from django.db import models


class OnlineUser(models.Model):
    """The user who is currently in a certain chat"""

    user = models.ForeignKey(get_user_model(), related_name="group_user", on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, related_name="group_participant", on_delete=models.CASCADE, null=True)

    class Meta:
        app_label = "chat"

    def __str__(self):
        return f"user: {self.user}, chat: {self.chat}"
