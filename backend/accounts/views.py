import logging
import math

from accounts.models import (
    ChangedEmail,
    EmailConfirmationToken,
    PasswordResetToken,
    Profile,
    User,
)
from accounts.serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    UpdateUserDataSerializer,
    UserSerializer,
)
from accounts.services.email import send_confirmation_email
from chat.permissions import IsEmailConfirm
from config.utils import get_ui_host
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import extend_schema, extend_schema_view, inline_serializer
from emails.services.email_verify import EmailVerify
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

logger = logging.getLogger(__name__)


class UserAPIView(APIView):
    """Return current authenticated user"""

    permission_classes = (IsAuthenticated, IsEmailConfirm)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Account"],
    )
    def get(self, request):
        logger.debug(f"{request.user} requested user data")
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Account"],
        request=UpdateUserDataSerializer,
    )
    def put(self, request):
        """Update user email/username"""

        logger.debug(f"{request.user} requested user data update, data: {request.data}")
        data = UpdateUserDataSerializer(data=request.data)
        if not data.is_valid():
            raise ValidationError(data.errors)

        new_email = data.validated_data.get("email", None)
        if new_email:
            # if email is already in use
            registered_user = User.objects.filter(email=new_email)
            if registered_user.exists():
                # is it another user
                if request.user.id != registered_user[0].id:
                    raise ValidationError("Email already exists.")

            # check if email is allowed
            email_verifier = EmailVerify(data.validated_data["email"])
            email_verifier.check()

            # save new email in ChangedEmail DB
            # if ChangedEmail object exists with old email we change old email to new
            new_email_obj = ChangedEmail.objects.filter(user=request.user).first()
            if new_email_obj:
                new_email_obj.email = new_email
                new_email_obj.save()
            else:
                new_email_obj, _ = ChangedEmail.objects.get_or_create(user=request.user, email=new_email)

            # get token for email confirmation
            token, _ = EmailConfirmationToken.objects.get_or_create(user=request.user)
            # send on new email confirmation letter with link
            send_confirmation_email(address=new_email, token_id=token.pk, ui_host=get_ui_host(request))

        new_username = data.validated_data.get("username", None)
        if new_username:
            registered_user = User.objects.filter(username=new_username)
            if registered_user.exists():
                if request.user.id != registered_user[0].id:
                    raise ValidationError("Username already registered.")

            request.user.username = new_username
            request.user.save()

        if not new_email and not new_username:
            raise ValidationError("No data to update.")

        logger.info(f"{request.user} user data updated successfully")
        return Response({"message": "User updated successfully"}, status=status.HTTP_200_OK)


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
        logger.debug(f"{self.request.user} requested profile data")
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

        logger.debug(f"{request.user} requested profile data update, data: {request.data}")
        serializer = ProfileSerializer(self.get_object(), data=request.data, context={"request": request})

        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        avatar = serializer.validated_data["avatar"]
        if avatar.size > settings.MAX_FILE_SIZE:
            msg = (
                f"Avatar file is too large: {math.ceil(avatar.size / 1024 / 1024)} MB."
                + f" Must be less than {settings.MAX_FILE_SIZE / 1024 / 1024} MB"
            )
            raise ValidationError(msg)

        serializer.validated_data["avatar"] = resize_in_memory_uploaded_file(avatar, 200)
        serializer.save()

        logger.info(f"{request.user} profile data updated successfully")
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

        logger.debug(f"{request.user} requested password change")
        self.user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if not serializer.is_valid():
            logging.error(f"{request.user} Update password. Invalid data: {serializer.errors}")
            raise ValidationError(serializer.errors)

        # check old password
        if not self.user.check_password(serializer.data.get("old_password")):
            logging.error(f"{request.user} Update password. Invalid old password")
            raise ValidationError("Wrong old password")

        # validate password
        try:
            validate_password(request.data["new_password"], self.user)
        except DjangoValidationError as error:
            logging.error(f"{request.user} Update password. Invalid new password")
            raise ValidationError(error.messages) from None

        # set_password also hashes the password that the user will get
        self.user.set_password(serializer.data.get("new_password"))
        self.user.save()

        data = {"message": "Password updated successfully"}
        logger.info(f"{request.user} Update password. Success")
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
        logger.debug(f"{request.user} Password reset request: {request.data}")
        serializer = RequestPasswordResetAPIView.serializer_class(data=request.data)

        if not serializer.is_valid():
            logging.warning(f"{request.user} Password reset request with invalid email: {serializer.errors}")
            raise ValidationError(serializer.errors)

        email = serializer.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logging.error(f"{request.user} Password reset request for non-existent email: {email}")
            raise ValidationError("User with this email does not exist") from None

        # send reset password email if user exists and email is confirmed
        if user.is_email_confirmed:
            token = PasswordResetToken.objects.create(user=user)
            send_password_reset_email(address=email, reset_password_token=token.pk, ui_host=get_ui_host(request))
        else:
            logging.warning(f"{request.user} Password reset request for unconfirmed email: {email}")
            raise ValidationError(f"Email is not confirmed.")

        msg = "If this email exists, a password reset email has been sent"
        logger.info(f"{request.user} Password reset request. Success")
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
        logger.debug(f"{request.user} Password reset: {request.data}")
        serializer = PasswordResetSerializer(data=request.data)

        if not serializer.is_valid():
            logging.warning(f"{request.user} Password reset with invalid data: {serializer.errors}")
            raise ValidationError(serializer.errors)

        token_id = serializer.data.get("token_id")
        password = serializer.data.get("password")

        try:
            token = PasswordResetToken.objects.get(pk=token_id)
        except PasswordResetToken.DoesNotExist:
            logging.warning(f"{request.user} Password reset with invalid token: {token_id}")
            raise ValidationError("Invalid token.") from None
        except DjangoValidationError as error:
            logging.error(f"{request.user} Password reset with invalid token: {token_id}")
            raise ValidationError(error) from None

        user = token.user

        try:
            validate_password(password, user)
        except DjangoValidationError as error:
            logging.error(f"{user} Password reset with invalid password.")
            raise ValidationError(error) from None

        # set_password also hashes the password that the user will get
        user.set_password(password)
        user.save()
        logger.info(f"{user} Password reset. Success")

        token.delete()
        logger.info(f"{user} Password reset token deleted")

        data = {"message": "Password reset successfully"}
        return Response(data=data, status=status.HTTP_200_OK)
