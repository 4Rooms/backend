"""
URL configuration for accounts.
"""

from django.urls import path

from backend.accounts.views import ChangePasswordAPIView, ProfileAPIView, UserAPIView

urlpatterns = [
    # user
    path("user/", UserAPIView.as_view(), name="user"),
    path("user/change-password", ChangePasswordAPIView.as_view(), name="change_password"),
    # profile
    path("profile/", ProfileAPIView.as_view(), name="profile"),
]
