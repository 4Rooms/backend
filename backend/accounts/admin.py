from accounts.models import EmailConfirmationToken, Profile, User
from django.contrib import admin

admin.site.register(User)
admin.site.register(EmailConfirmationToken)
admin.site.register(Profile)
