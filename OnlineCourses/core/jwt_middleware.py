from urllib.parse import parse_qs
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        token = None

        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b'authorization', b'').decode("utf-8")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]

        if not token:
            qs = scope.get("query_string", b"").decode()
            params = parse_qs(qs)
            token = params.get("token", [None])[0]

        if token:
            try:
                access_token = AccessToken(token)  # validate & decode
                user_id = access_token.get("user_id")
                if user_id is not None:
                    user = await get_user(user_id)
                    scope["user"] = user
                else:
                    scope["user"] = AnonymousUser()
            except Exception:
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
