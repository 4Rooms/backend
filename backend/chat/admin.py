from chat.models.chat import Chat, SavedChat
from chat.models.message import Message
from chat.models.onlineUser import OnlineUser
from django.contrib import admin

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(OnlineUser)
admin.site.register(SavedChat)
