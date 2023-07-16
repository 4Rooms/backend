from django.urls import path
from login.views import LoginAPIView

urlpatterns = [
    path("login/", LoginAPIView.as_view(), name="login"),
]
