from django.urls import path

from backend.registration.views import ConfirmEmailApiView, RegisterUserView

urlpatterns = [
    path("register/", RegisterUserView.as_view(), name="register"),
    path("confirm-email/", ConfirmEmailApiView.as_view(), name="confirm-email"),
]
