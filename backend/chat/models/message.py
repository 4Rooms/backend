from chat.models.chat import Chat
from django.contrib.auth import get_user_model
from django.db import models


class Message(models.Model):
    """Message table"""

    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    text = models.TextField(max_length=792, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        app_label = "chat"

    def __str__(self):
        return f"id: {self.pk}, text: {self.text}, user: {self.user}"

    def delete(self):
        """Soft delete: delete message text, is_deleted = True"""

        self.is_deleted = True
        self.text = "deleted"
        self.save()
