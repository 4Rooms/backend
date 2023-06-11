"""
URL configuration for accounts.
"""

from django.urls import include, path
from rest_framework import routers

from .views import GroupViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)
router.register(r"groups", GroupViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # path("api/register/", RegisterAPI.as_view(), name="register"),
]
