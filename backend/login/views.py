from accounts.serializers import LoginDataSerializer, UserSerializer
from drf_spectacular.utils import extend_schema, inline_serializer
from login.authentication_backend import AuthBackend
from login.cookie import delete_auth_cookie, set_auth_cookie
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken


def get_tokens(user):
    """Get tokens for user"""

    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
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
        """Authenticate the user, set the access token
        as an HttpOnly cookie, and return a user info"""

        # authenticate user
        data = request.data

        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        login_data = serializer.validated_data

        user = AuthBackend.authenticate(self, request, username=login_data["username"], password=login_data["password"])

        if user is None:
            raise ValidationError({"Invalid": "Invalid username or password"}, code=status.HTTP_404_NOT_FOUND)

        token = get_tokens(user)

        # set cookie for response
        response = Response()
        set_auth_cookie(response, token["access"])

        # serialize the user to return it in response
        serializer = UserSerializer(user, many=False)
        response.data = {"Success": "Login successfully", "user": serializer.data}
        return response


class LogoutAPIView(UpdateAPIView):
    """Logout. Delete the access token cookie"""

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
        """Delete the access token cookie"""

        response = Response(status=status.HTTP_204_NO_CONTENT)
        delete_auth_cookie(response)
        return response

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
