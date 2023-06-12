"""
URL configuration for accounts.
"""

from django.urls import include, path, re_path
from rest_framework import routers

from .views import GroupViewSet, UserViewSet

router = routers.SimpleRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)
print(router.urls)

urlpatterns = [
    path("", include(router.urls)),

    # session authentication
    path("api-session-auth/", include("rest_framework.urls", namespace="rest_framework")),

    # Token authentication

    # http://127.0.0.1:8000/api-auth/users/
    path(r'api-auth/', include('djoser.urls')),

    # http://127.0.0.1:8000/auth/token/login/
    # http://127.0.0.1:8000/auth/token/logout/
    re_path(r'^auth/', include('djoser.urls.authtoken')),
]
