from chat.models.chat import Chat, SavedChat
from chat.models.chatLike import ChatLike
from chat.models.message import Message
from chat.models.onlineUser import OnlineUser
from chat.models.reaction import Reaction
from django.contrib import admin

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(OnlineUser)
admin.site.register(SavedChat)
admin.site.register(ChatLike)
admin.site.register(Reaction)
