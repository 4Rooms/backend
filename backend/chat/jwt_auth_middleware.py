from channels.db import database_sync_to_async
from login.authenticate import CustomJWTAuthentication


class JWTAuthMiddleware:
    """
    Custom middleware for django channels to authenticate users using JWT tokens
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        user, token = await self._authenticate(scope)
        scope["user"] = user
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def _authenticate(self, scope):
        auth = CustomJWTAuthentication()
        return auth.authenticate(scope)
