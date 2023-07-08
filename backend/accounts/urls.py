"""
URL configuration for accounts.
"""

from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    AllUsersView,
    ChangePasswordView,
    ConfirmEmailApiView,
    RegisterUserView,
    UserAvatarAPIView,
    UserView,
)

urlpatterns = [
    # user
    path("api/users/", AllUsersView.as_view(), name="get_user_list"),
    path("api/user/", UserView.as_view(), name="get_current_user"),
    path("api/user/change-password", ChangePasswordView.as_view(), name="change_password"),
    # profile
    path("api/profile/avatar/", UserAvatarAPIView.as_view(), name="user_avatar"),
    # register
    path("api/register/", RegisterUserView.as_view(), name="register"),
    path("oauth/", include("social_django.urls", namespace="social")),
    path("api/confirm-email/", ConfirmEmailApiView.as_view(), name="confirm-email"),
    # JWT authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
