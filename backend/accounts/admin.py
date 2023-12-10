from accounts.models import (
    ChangedEmail,
    EmailConfirmationToken,
    PasswordResetToken,
    Profile,
    User,
)
from django.contrib import admin

admin.site.register(EmailConfirmationToken)
admin.site.register(PasswordResetToken)
admin.site.register(Profile)
admin.site.register(User)
admin.site.register(ChangedEmail)
