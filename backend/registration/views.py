from accounts.models import EmailConfirmationToken, User
from accounts.serializers import UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from backend.registration.email_sending import send_confirmation_email


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
