from django.contrib import admin

from .models import EmailConfirmationToken, Profile, User

admin.site.register(User)
admin.site.register(EmailConfirmationToken)
admin.site.register(Profile)
