from chat.models.message import Message
from django.contrib.auth import get_user_model
from django.db import models


class Reaction(models.Model):
    """Reaction to the message"""

    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, on_delete=models.SET_NULL)
    reaction = models.CharField(max_length=1, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "chat"

    def __str__(self):
        return f"id: {self.pk}, msg: {self.message}, user: {self.user}, reaction: {self.reaction}"
