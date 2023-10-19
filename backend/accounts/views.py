import logging

from accounts.models import PasswordResetToken, Profile, User
from accounts.serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    UpdateUserDataSerializer,
    UserSerializer,
)
from chat.permissions import IsEmailConfirm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.accounts.services.email import send_password_reset_email
from backend.config.utils import get_ui_host
from backend.files.services.images import resize_in_memory_uploaded_file


class UserAPIView(APIView):
    """Return current authenticated user"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Account"],
    )
    def get(self, request):
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Account"],
        request=UpdateUserDataSerializer,
    )
    def put(self, request):
        """Update user email/username"""

        data = UpdateUserDataSerializer(data=request.data)
        if not data.is_valid():
            raise ValidationError(data.errors)

        new_email = data.validated_data["email"]
        new_username = data.validated_data["username"]
        user = User.objects.get(email=request.user.email)

        # if email is already in use
        registered_user = User.objects.filter(email=new_email)
        if registered_user.exists():
            # is it another user
            if user.id != registered_user[0].id:
                raise ValidationError("Email already exists.")

        # if username is already in use
        registered_user = User.objects.filter(username=new_username)
        if registered_user.exists():
            if user.id != registered_user[0].id:
                raise ValidationError("Username already registered.")

        user.email = new_email
        user.username = new_username
        user.save()
        return Response({"message": "Email, Username updated successfully"}, status=status.HTTP_200_OK)


@extend_schema_view(
    get=extend_schema(tags=["Account"]),
    put=extend_schema(tags=["Account"]),
)
class ProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ["get", "put"]

    @extend_schema(
        tags=["Account"],
    )
    def get_object(self):
        return self.request.user.profile

    @extend_schema(
        tags=["Account"],
        operation_id="upload_file",
        request={
            "multipart/form-data": {"type": "object", "properties": {"avatar": {"type": "string", "format": "binary"}}}
        },
    )
    def put(self, request, *args, **kwargs):
        """Update user avatar"""

        serializer = ProfileSerializer(self.get_object(), data=request.data, context={"request": request})

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        avatar = serializer.validated_data["avatar"]
        serializer.validated_data["avatar"] = resize_in_memory_uploaded_file(avatar, 200)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema_view(
    put=extend_schema(tags=["Account"]),
)
class ChangePasswordAPIView(UpdateAPIView):
    """
    Changing password endpoint.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated, IsEmailConfirm)
    http_method_names = ["put"]

    @extend_schema(
        tags=["Account"],
    )
    def update(self, request, *args, **kwargs):
        """Change password"""

        self.user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            logging.error(f"Update password. serializer.is_valid() -> false")
            raise ValidationError(serializer.errors)

        # check old password
        if not self.user.check_password(serializer.data.get("old_password")):
            logging.error(f"Update password. Invalid old password")
            raise ValidationError("Wrong old password")

        # validate password
        try:
            validate_password(request.data["new_password"], self.user)
        except DjangoValidationError as error:
            logging.error(f"Update password. Invalid new password")
            raise ValidationError(error.messages) from None

        # set_password also hashes the password that the user will get
        self.user.set_password(serializer.data.get("new_password"))
        self.user.save()

        data = {"message": "Password updated successfully"}
        return Response(data=data, status=status.HTTP_200_OK)


class RequestPasswordResetAPIView(APIView):
    """
    Request password reset.
    """

    permission_classes = ()
    serializer_class = EmailSerializer

    @extend_schema(
        tags=["Account"],
        responses=inline_serializer(
            name="RequestPasswordResetResponse",
            fields={
                "message": serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        serializer = RequestPasswordResetAPIView.serializer_class(data=request.data)

        if not serializer.is_valid():
            logging.warning(f"Password reset request with invalid email: {serializer.errors}")
            raise ValidationError(serializer.errors)

        email = serializer.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logging.warning(f"Password reset request for non-existent email: {email}")
            raise ValidationError("User with this email does not exist") from None

        # send reset password email if user exists and email is confirmed
        if user.is_email_confirmed:
            token = PasswordResetToken.objects.create(user=user)
            send_password_reset_email(address=email, reset_password_token=token.pk, ui_host=get_ui_host(request))
        else:
            logging.warning(f"Password reset request for unconfirmed email: {email}")
            raise ValidationError("Email is not confirmed.")

        msg = "If this email exists, a password reset email has been sent"
        return Response({"message": msg}, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """
    Reset password.
    """

    permission_classes = ()
    serializer_class = PasswordResetSerializer

    @extend_schema(
        tags=["Account"],
        responses=inline_serializer(
            name="PasswordResetResponse",
            fields={
                "message": serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        token_id = serializer.data.get("token_id")
        password = serializer.data.get("password")

        try:
            token = PasswordResetToken.objects.get(pk=token_id)
        except PasswordResetToken.DoesNotExist:
            logging.warning(f"Password reset with invalid token: {token_id}")
            raise ValidationError("Invalid token.") from None
        except DjangoValidationError as error:
            logging.error(f"Password reset with invalid token: {token_id}")
            raise ValidationError(error) from None

        user = token.user

        try:
            validate_password(password, user)
        except DjangoValidationError as error:
            logging.error(f"Password reset with invalid password.")
            raise ValidationError(error) from None

        # set_password also hashes the password that the user will get
        user.set_password(password)
        user.save()

        token.delete()

        data = {"message": "Password reset successfully"}
        return Response(data=data, status=status.HTTP_200_OK)
