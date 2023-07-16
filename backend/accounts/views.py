from accounts.email_sending import send_confirmation_email
from accounts.models import EmailConfirmationToken, Profile, User
from accounts.serializers import (
    ChangePasswordSerializer,
    ProfileAvatarSerializer,
    UserSerializer,
)
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class RegisterUserView(APIView):
    """User registration with email and password"""

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # if email is already in use
        if User.objects.filter(email=request.data["email"]).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # if username is already in use
        if User.objects.filter(username=request.data["username"]).exists():
            return Response({"error": "Username already registered"}, status=status.HTTP_400_BAD_REQUEST)

        # validate password
        try:
            validate_password(password=request.data["password"], user=request.data)
        except ValidationError as errors:
            return Response({"password error": errors}, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        # create token for email confirmation
        token = EmailConfirmationToken.objects.create(user=user)
        # send link for email confirmation
        send_confirmation_email(email=user.email, token_id=token.pk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserView(APIView):
    """Return current authenticated user"""

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


class ConfirmEmailApiView(APIView):
    """When the user goes to the email confirmation link"""

    permission_classes = (AllowAny,)

    def get(self, request):
        token_id = request.GET.get("token_id", None)
        try:
            # We check whether there is such a token
            token = EmailConfirmationToken.objects.get(pk=token_id)
            user = token.user
            user.is_email_confirmed = True
            user.save()
            data = {"is_email_confirmed": True}
            return Response(data=data, status=status.HTTP_200_OK)
        except EmailConfirmationToken.DoesNotExist:
            # if token does not exist
            data = {"is_email_confirmed": False, "error": "Token is wrong"}
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarAPIView(RetrieveUpdateAPIView):
    """
    Get, Update user avatar
    """

    permission_classes = (IsAuthenticated,)
    queryset = Profile.objects.all()
    serializer_class = ProfileAvatarSerializer
    http_method_names = ["get", "put"]

    def get_object(self):
        return self.request.user.profile


class ChangePasswordView(UpdateAPIView):
    """
    Changing password endpoint.
    """

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)
    http_method_names = ["put"]

    def is_invalid_password(self, password, user):
        """
        Password validation. Returns False if the password has passed validation.
        Returns error/errors if the password has not passed the validation.
        """

        try:
            validate_password(password, user)
            return False
        except ValidationError as error:
            return error

    def update(self, request, *args, **kwargs):
        self.user = self.request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            # check old password
            if not self.user.check_password(serializer.data.get("old_password")):
                return Response({"old password error": ["Old password is wrong"]}, status=status.HTTP_400_BAD_REQUEST)

            # if password is invalid
            password_errors = self.is_invalid_password(password=request.data["new_password"], user=self.user)
            if password_errors:
                return Response({"new password error": password_errors}, status=status.HTTP_400_BAD_REQUEST)

            # set_password also hashes the password that the user will get
            self.user.set_password(serializer.data.get("new_password"))
            self.user.save()

            data = {"message": "Password updated successfully"}
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
