import logging

from accounts.models import PasswordResetToken, Profile, User
from accounts.serializers import (
    ChangePasswordSerializer,
    EmailSerializer,
    PasswordResetSerializer,
    ProfileSerializer,
    UserSerializer,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.accounts.services.email import send_password_reset_email


class UserAPIView(APIView):
    """Return current authenticated user"""

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Account operations"],
    )
    def get(self, request):
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=["Account operations"],
    )
    def put(self, request):
        """Update user email/username"""

        user = User.objects.get(email=request.user.email)
        new_email = request.data["email"]
        new_username = request.data["username"]

        # if email is already in use
        if User.objects.filter(email=new_email).exists():
            another_user = User.objects.get(email=new_email)
            # is it another user
            if user.id != another_user.id:
                return Response({"email error": "That email already exists"}, status=status.HTTP_400_BAD_REQUEST)

        # if username is already in use
        if User.objects.filter(username=new_username).exists():
            another_user = User.objects.get(username=new_username)
            if user.id != another_user.id:
                return Response(
                    {"username error": "That username already registered"}, status=status.HTTP_400_BAD_REQUEST
                )

        # validate email
        try:
            validate_email(new_email)
        except ValidationError as error:
            return Response({"email error": error}, status=status.HTTP_400_BAD_REQUEST)

        user.email = new_email
        user.username = new_username
        user.save()
        return Response({"message": "Email, Username updated successfully"}, status=status.HTTP_200_OK)


class ProfileAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """

    permission_classes = (IsAuthenticated,)
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    http_method_names = ["get", "put"]

    @extend_schema(
        tags=["Account operations"],
    )
    def get_object(self):
        return self.request.user.profile


@extend_schema_view(
    put=extend_schema(tags=["Account operations"]),
)
class ChangePasswordAPIView(UpdateAPIView):
    """
    Changing password endpoint.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    http_method_names = ["put"]

    @extend_schema(
        tags=["Account operations"],
    )
    def update(self, request, *args, **kwargs):
        """Change password"""

        self.user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not self.user.check_password(serializer.data.get("old_password")):
                return Response({"old password error": ["Old password is wrong"]}, status=status.HTTP_400_BAD_REQUEST)

            # validate password
            try:
                validate_password(request.data["new_password"], self.user)
            except ValidationError as errors:
                return Response({"new password error": errors}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.user.set_password(serializer.data.get("new_password"))
            self.user.save()

            data = {"message": "Password updated successfully"}
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetAPIView(APIView):
    """
    Request password reset.
    """

    permission_classes = ()
    serializer_class = EmailSerializer

    @extend_schema(
        tags=["Account operations"],
    )
    def post(self, request):
        email = request.data.get("email", "")

        # check if email is valid
        try:
            validate_email(email)
        except ValidationError as error:
            return Response({"email error": error}, status=status.HTTP_400_BAD_REQUEST)

        # send reset password email if user exists and email is confirmed
        try:
            user = User.objects.get(email=email)

            if user.is_email_confirmed:
                token = PasswordResetToken.objects.create(user=user)
                send_password_reset_email(address=email, reset_password_token=token.pk)
            else:
                logging.warning(f"Password reset request for unconfirmed email: {email}")
                msg = "Email is not confirmed."
                return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            logging.error(f"Password reset request for nonexistent user with email: {email}")
            msg = "Email does not exist."
            return Response({"message": msg}, status=status.HTTP_400_BAD_REQUEST)

        msg = "If this email exists, a password reset email has been sent"
        return Response({"message": msg}, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """
    Reset password.
    """

    permission_classes = ()
    serializer_class = PasswordResetSerializer

    @extend_schema(
        tags=["Account operations"],
    )
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            token_id = serializer.data.get("token_id")
            password = serializer.data.get("password")

            try:
                token = PasswordResetToken.objects.get(pk=token_id)
                user = token.user

                # validate password
                try:
                    validate_password(password, user)
                except ValidationError as errors:
                    return Response({"new password error": errors}, status=status.HTTP_400_BAD_REQUEST)

                # set_password also hashes the password that the user will get
                user.set_password(password)
                user.save()

                token.delete()

                data = {"message": "Password reset successfully"}
                return Response(data=data, status=status.HTTP_200_OK)
            except PasswordResetToken.DoesNotExist:
                return Response({"message": "Token does not exist"}, status=status.HTTP_400_BAD_REQUEST)
            except ValidationError as ex:
                return Response({"message": f"Validation error: {ex}"}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
