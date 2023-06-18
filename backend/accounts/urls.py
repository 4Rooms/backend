"""
URL configuration for accounts.
"""

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import AllUsersView, RegisterUserView, UserView

urlpatterns = [
    path("api/users/", AllUsersView.as_view(), name="get_user_list"),
    path("api/user/", UserView.as_view(), name="get_current_user"),
    path("api/register/", RegisterUserView.as_view(), name="register"),
    # JWT authentication
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # session authentication
    # path("api/session/auth/", include("rest_framework.urls", namespace="rest_framework")),
]
