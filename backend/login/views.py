import logging

from accounts.serializers import LoginDataSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from login.authentication_backend import AuthBackend
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


def get_tokens(user):
    """Get tokens for user"""

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    logger.info(f"{user} got tokens {access_token[:25]}...{access_token[-25:]}")
    return {
        "refresh": str(refresh),
        "access": access_token,
    }


class LoginAPIView(APIView):
    """Login. Authenticate user and return a user info"""

    authentication_classes = []
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    serializer_class = LoginDataSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Account"],
    )
    def post(self, request, format=None):
        """Authenticate the user, set the access token and return a user info"""

        logger.debug(f"Login request.")

        # authenticate user
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        login_data = serializer.validated_data

        user = AuthBackend.authenticate(self, request, username=login_data["username"], password=login_data["password"])

        if user is None:
            raise ValidationError({"Invalid": "Invalid username or password"}, code=status.HTTP_404_NOT_FOUND)

        tokens = get_tokens(user)

        response = Response()

        # serialize the user to return it in response
        serializer = UserSerializer(user, many=False)
        response.data = {"user": serializer.data, "token": tokens["access"]}
        return response


class LogoutAPIView(UpdateAPIView):
    """Logout"""

    authentication_classes = []
    http_method_names = ["put"]
    permission_classes = (AllowAny,)
    serializer_class = serializers.Serializer

    @extend_schema(
        tags=["Account"],
        request=inline_serializer(
            name="LogoutRequest",
            fields={},
        ),
        responses={
            204: inline_serializer(
                name="LogoutResponse",
                fields={},
            )
        },
        parameters=[],
        methods=["PUT"],
        description="Logout Request",
    )
    def put(self, request):
        """Delete the access token"""
        raise NotImplementedError("Logout is not implemented")

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
