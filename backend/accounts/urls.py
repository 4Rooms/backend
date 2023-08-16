"""
URL configuration for accounts.
"""

from django.urls import path

from backend.accounts.views import (
    ChangePasswordAPIView,
    PasswordResetAPIView,
    ProfileAPIView,
    RequestPasswordResetAPIView,
    UserAPIView,
)

urlpatterns = [
    # user
    path("user/", UserAPIView.as_view(), name="user"),
    path("user/change-password", ChangePasswordAPIView.as_view(), name="change_password"),
    path("user/password/request-reset", RequestPasswordResetAPIView.as_view(), name="request_password_reset"),
    path("user/password/reset", PasswordResetAPIView.as_view(), name="password_reset"),
    # profile
    path("profile/", ProfileAPIView.as_view(), name="profile"),
]
