from typing import List, Union

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.openapi import AutoSchema


class CustomJWTAuthenticationExtension(OpenApiAuthenticationExtension):
    target_class = "login.authenticate.CustomJWTAuthentication"
    name = "JWTAuthentication"

    def get_security_definition(self, auto_schema: "AutoSchema") -> Union[dict, List[dict]]:
        return {
            "type": "http",
            "in": "header",
            "scheme": "Bearer",
            "name": "Authorization",
            "description": "JWT Authorization header using the Bearer scheme.",
        }
