"""
URL configuration for accounts.
"""

from django.urls import path

from backend.accounts.views import ChangePasswordView, ProfileAPIView, UserView

urlpatterns = [
    # user
    path("api/user/", UserView.as_view(), name="user"),
    path("api/user/change-password", ChangePasswordView.as_view(), name="change_password"),
    # profile
    path("api/profile/", ProfileAPIView.as_view(), name="profile"),
]
