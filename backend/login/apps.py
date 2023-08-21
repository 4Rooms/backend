from django.apps import AppConfig


class LoginConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "login"

    def ready(self) -> None:
        # Import schema so OpenAPI extension can register itself
        from login.openapi_custom_auth_extension import (  # noqa
            CustomJWTAuthenticationExtension,
        )
