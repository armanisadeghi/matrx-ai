"""Auth middleware — pure ASGI, no BaseHTTPMiddleware.

BaseHTTPMiddleware buffers the full response body and silently swallows
exceptions raised inside streaming async generators. Pure ASGI middleware
does neither: it passes scope/receive/send straight through to the route
handler without buffering anything.

Auth resolution order per request
----------------------------------
1. Bearer JWT   → decode with Supabase secret → authenticated user
2. Admin token  → static token match          → admin user
3. Fingerprint  → X-Fingerprint-ID header     → guest user
4. None of the above                           → anonymous

Sets both:
  - request.state.context  → consumed by FastAPI Depends(context_dep)
  - ContextVar             → consumed by get_app_context() anywhere in the stack
"""

from __future__ import annotations

import sys

import jwt
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from matrx_service.app.config import get_settings
from matrx_service.context._log import log
from matrx_service.context.app_context import AppContext, clear_app_context, set_app_context


class AuthMiddleware:
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
                redacted_auth = (
                    f"{scheme} {tok[:6]}…{tok[-4:]}" if len(tok) > 10 else f"{scheme} [redacted]"
                )
            else:
                redacted_auth = "[redacted]"

        log(
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
            title="[AuthMiddleware] Request",
            color="blue",
        )

        ctx = _build_context(request)

        request.state.context = ctx

        token = set_app_context(ctx)
        try:
            await self.app(scope, receive, send)
        finally:
            clear_app_context(token)


def _build_context(request: Request) -> AppContext:
    from matrx_service.context.stream_emitter import StreamEmitter

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
            log(f"[AuthMiddleware] Non-bearer scheme rejected: {scheme!r}", color="yellow")
            return None
    except ValueError:
        log("[AuthMiddleware] Malformed authorization header", color="yellow")
        return None

    settings = get_settings()
    admin_token = settings.admin_api_token
    admin_user_id = settings.admin_user_id

    if admin_token and admin_user_id and token == admin_token:
        log(f"[AuthMiddleware] Admin token accepted: user={admin_user_id}", color="green")
        ctx.user_id = admin_user_id
        ctx.auth_type = "token"
        ctx.is_authenticated = True
        ctx.is_admin = True
        ctx.email = "admin@system"
        ctx.token = token
        ctx.fingerprint_id = fingerprint_id
        return ctx

    jwt_secret = settings.supabase_jwt_secret

    if not jwt_secret:
        print(
            "[AuthMiddleware] WARNING: SUPABASE_JWT_SECRET not set — "
            "JWT tokens cannot be validated.",
            file=sys.stderr,
            flush=True,
        )
        log("[AuthMiddleware] JWT secret missing — cannot validate token", color="red")
        return None

    try:
        decoded = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        user_id = decoded.get("sub", "")
        log(f"[AuthMiddleware] JWT accepted: user={user_id}", color="green")
        ctx.user_id = user_id
        ctx.auth_type = "token"
        ctx.is_authenticated = True
        ctx.is_admin = False
        ctx.email = decoded.get("email")
        ctx.token = token
        ctx.fingerprint_id = fingerprint_id
        return ctx
    except jwt.InvalidTokenError as e:
        print(
            f"[AuthMiddleware] JWT validation FAILED: {type(e).__name__}: {e}",
            file=sys.stderr,
            flush=True,
        )
        log(f"[AuthMiddleware] JWT rejected: {type(e).__name__}: {e}", color="red")
        return None
