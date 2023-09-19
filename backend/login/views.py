from accounts.serializers import UserSerializer
from drf_spectacular.utils import extend_schema
from login.authentication_backend import AuthBackend
from login.cookie import set_auth_cookie
from rest_framework import status
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
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        tags=["Account operations"],
    )
    def post(self, request, format=None):
        """Authenticate the user, set the access token
        as an HttpOnly cookie, and return a user info"""

        # authenticate user
        data = request.data
        username = data.get("username", None)
        password = data.get("password", None)
        user = AuthBackend.authenticate(self, request, username=username, password=password)

        if user is None:
            return Response({"Invalid": "Invalid username or password"}, status=status.HTTP_404_NOT_FOUND)

        token = get_tokens(user)

        # set cookie for response
        response = Response()
        set_auth_cookie(response, token["access"])

        # serialize the user to return it in response
        serializer = UserSerializer(user, many=False)
        response.data = {"Success": "Login successfully", "user": serializer.data}
        return response
