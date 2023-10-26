from chat.models.chat import Chat
from django.contrib.auth import get_user_model
from django.db import models


class ChatLike(models.Model):
    """Chat like model"""

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"id: {self.pk}, chat: {self.chat}, user: {self.user}"

    class Meta:
        app_label = "chat"
