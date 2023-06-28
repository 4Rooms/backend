from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import EmailConfirmationToken, Profile


class CustomUserAdmin(UserAdmin):
    """Define admin model for custom User model without username field.
    Without this, the admin panel will look bad"""

    fieldsets = (
        (None, {"fields": ("email", "password", "is_email_confirmed")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "first_name", "is_email_confirmed", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(EmailConfirmationToken)
admin.site.register(Profile)
