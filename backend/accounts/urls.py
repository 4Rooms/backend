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
    # users, groups
    # http://127.0.0.1:8000/api/users/
    path("api/", include(router.urls)),

    # session authentication
    # path("api/session/auth/", include("rest_framework.urls", namespace="rest_framework")),

    # Token authentication
    # api/auth/users/
    path(r'api/auth/', include('djoser.urls')),

    # api/auth/token/  login, logout, users, user/<int:id>/
    re_path(r'^api/auth/', include('djoser.urls.authtoken')),
]
