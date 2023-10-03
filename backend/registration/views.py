import logging

from accounts.models import EmailConfirmationToken, User
from accounts.serializers import UserSerializer
from accounts.services.email import send_confirmation_email
from config.utils import get_ui_host
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from drf_spectacular.utils import OpenApiParameter, extend_schema
from registration.serializers import EmailConfirmationResponseSerializer
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

logger = logging.getLogger(__name__)


class RegisterUserView(APIView):
    """User registration with email and password"""

    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = (AllowAny,)
    serializer_class = UserSerializer

    @extend_schema(
        tags=["Account operations"],
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            raise ValidationError(serializer.errors)

        # if email is already in use
        if User.objects.filter(email=request.data["email"]).exists():
            raise ValidationError("Email already exists")

        # if username is already in use
        if User.objects.filter(username=request.data["username"]).exists():
            raise ValidationError("Username already registered")

        # validate password
        try:
            validate_password(password=request.data["password"], user=request.data)
        except DjangoValidationError as error:
            raise ValidationError(error.messages) from None

        user = serializer.save()
        # create token for email confirmation
        token = EmailConfirmationToken.objects.create(user=user)
        # send link for email confirmation
        send_confirmation_email(address=user.email, token_id=token.pk, ui_host=get_ui_host(request))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConfirmEmailApiView(APIView):
    """When the user goes to the email confirmation link"""

    permission_classes = (AllowAny,)
    serializer_class = EmailConfirmationResponseSerializer

    @extend_schema(
        tags=["Account operations"],
        parameters=[
            OpenApiParameter(
                name="token_id", location=OpenApiParameter.QUERY, description="TokenId", required=True, type=str
            ),
        ],
    )
    def get(self, request):
        token_id = request.GET.get("token_id", None)
        try:
            # We check whether there is such a token
            token = EmailConfirmationToken.objects.get(pk=token_id)
            user = token.user
            user.is_email_confirmed = True
            user.save()

            resp_serializer = ConfirmEmailApiView.serializer_class(instance={"is_email_confirmed": True})
            return Response(data=resp_serializer.data, status=status.HTTP_200_OK)
        except EmailConfirmationToken.DoesNotExist as ex:
            logger.error(ex)
            raise ValidationError("Wrong email confirmation token.") from None
        except DjangoValidationError as ex:
            logger.error(ex)
            raise ValidationError(ex.message) from None
