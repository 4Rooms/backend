from accounts.models import Profile, User
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
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


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
