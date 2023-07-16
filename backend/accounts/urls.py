"""
URL configuration for accounts.
"""

from django.urls import include, path

from backend.accounts.views import (
    ChangePasswordView,
    ConfirmEmailApiView,
    RegisterUserView,
    UserAvatarAPIView,
    UserView,
)

urlpatterns = [
    # user
    path("api/user/", UserView.as_view(), name="current_user"),
    path("api/user/change-password", ChangePasswordView.as_view(), name="change_password"),
    # profile
    path("api/profile/avatar/", UserAvatarAPIView.as_view(), name="user_avatar"),
    # register
    path("api/register/", RegisterUserView.as_view(), name="register"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("api/confirm-email/", ConfirmEmailApiView.as_view(), name="confirm-email"),
]
