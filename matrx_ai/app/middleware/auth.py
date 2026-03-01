from __future__ import annotations

import jwt
from matrx_utils import vcprint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.config import get_settings
from context.app_context import AppContext, clear_app_context, set_app_context


class AuthMiddleware:
    """Pure ASGI auth middleware.

    BaseHTTPMiddleware buffers the full response body and silently swallows
    exceptions raised inside streaming async generators. Pure ASGI middleware
    does neither — it passes scope/receive/send straight through.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)

        raw_auth: str | None = request.headers.get("authorization")
        redacted_auth: str | None = None
        if raw_auth:
            parts = raw_auth.split(None, 1)
            if len(parts) == 2:
                scheme, tok = parts
                redacted_auth = f"{scheme} {tok[:6]}…{tok[-4:]}" if len(tok) > 10 else f"{scheme} [redacted]"
            else:
                redacted_auth = "[redacted]"

        vcprint(
            {
                "method": request.method,
                "path": request.url.path,
                "query": str(request.url.query) or None,
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
                "authorization": redacted_auth,
                "fingerprint_id": request.headers.get("x-fingerprint-id"),
                "content_type": request.headers.get("content-type"),
                "content_length": request.headers.get("content-length"),
            },
            "[AuthMiddleware] __call__ Request Received",
            color="blue",
        )

        ctx = _build_context(request)

        # For router handlers — context_dep reads this
        request.state.context = ctx

        # For service / AI / tool code — get_app_context() reads this
        token = set_app_context(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            clear_app_context(token)


def _build_context(request: Request) -> AppContext:
    from context.stream_emitter import StreamEmitter

    ctx = AppContext(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        emitter=StreamEmitter(debug=False),
    )

    authorization: str | None = request.headers.get("authorization")
    fingerprint_id: str | None = request.headers.get("x-fingerprint-id")

    if authorization:
        enriched = _validate_token(authorization, fingerprint_id, ctx)
        if enriched is not None:
            return enriched

    if fingerprint_id:
        ctx.user_id = f"guest_{fingerprint_id}"
        ctx.auth_type = "fingerprint"
        ctx.fingerprint_id = fingerprint_id
        return ctx

    return ctx


def _validate_token(
    authorization: str,
    fingerprint_id: str | None,
    ctx: AppContext,
) -> AppContext | None:
    try:
        scheme, token = authorization.split(None, 1)
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None

    settings = get_settings()
    admin_token = settings.admin_api_token
    admin_user_id = settings.admin_user_id

    if admin_token and admin_user_id and token == admin_token:
        ctx.user_id = admin_user_id
        ctx.auth_type = "token"
        ctx.is_authenticated = True
        ctx.is_admin = True
        ctx.email = "admin@system"
        ctx.token = token
        ctx.fingerprint_id = fingerprint_id
        return ctx

    jwt_secret = settings.supabase_matrix_jwt_secret

    if not jwt_secret:
        return None

    try:
        decoded = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        ctx.user_id = decoded.get("sub", "")
        ctx.auth_type = "token"
        ctx.is_authenticated = True
        ctx.is_admin = False
        ctx.email = decoded.get("email")
        ctx.token = token
        ctx.fingerprint_id = fingerprint_id
        return ctx
    except jwt.InvalidTokenError:
        return None
