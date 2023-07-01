from django.contrib import admin

from .models import EmailConfirmationToken, Profile, User

# class CustomUserAdmin(UserAdmin):
#     """Define admin model for custom User model without username field.
#     Without this, the admin panel will look bad"""
#
#     fieldsets = (
#         (None, {"fields": ("username", "email", "password", "is_email_confirmed")}),
#         # (_("Personal info"), {"fields": ("first_name", "last_name")}),
#         (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
#         (_("Important dates"), {"fields": ("last_login", "date_joined")}),
#     )
#     add_fieldsets = (
#         (
#             None,
#             {
#                 "classes": ("wide",),
#                 "fields": ("username", "email", "password1", "password2"),
#             },
#         ),
#     )
#     list_display = ("username", "email", "first_name", "is_email_confirmed", "last_name", "is_staff")
#     search_fields = ("email",)
#     ordering = ("email",)


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


# admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(User)
admin.site.register(EmailConfirmationToken)
admin.site.register(Profile)
