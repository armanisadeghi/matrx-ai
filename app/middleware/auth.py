from __future__ import annotations

import os
from typing import Optional

import jwt
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from context.app_context import AppContext, set_app_context, clear_app_context

SUPABASE_JWT_SECRET: Optional[str] = os.environ.get("SUPABASE_MATRIX_JWT_SECRET")
ADMIN_TOKEN: Optional[str] = os.environ.get("ADMIN_API_TOKEN")
ADMIN_USER_ID: Optional[str] = os.environ.get("ADMIN_USER_ID")


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        ctx = _build_context(request)

        # For router handlers — context_dep reads this
        request.state.context = ctx

        # For service / AI / tool code — get_app_context() reads this
        token = set_app_context(ctx)
        try:
            return await call_next(request)
        finally:
            clear_app_context(token)


def _build_context(request: Request) -> AppContext:
    from context.stream_emitter import StreamEmitter

    ctx = AppContext(
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        emitter=StreamEmitter(debug=False),
    )

    authorization: Optional[str] = request.headers.get("authorization")
    fingerprint_id: Optional[str] = request.headers.get("x-fingerprint-id")

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
    fingerprint_id: Optional[str],
    ctx: AppContext,
) -> Optional[AppContext]:
    try:
        scheme, token = authorization.split(None, 1)
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None

    if ADMIN_TOKEN and ADMIN_USER_ID and token == ADMIN_TOKEN:
        ctx.user_id = ADMIN_USER_ID
        ctx.auth_type = "token"
        ctx.is_authenticated = True
        ctx.is_admin = True
        ctx.email = "admin@system"
        ctx.token = token
        ctx.fingerprint_id = fingerprint_id
        return ctx

    if not SUPABASE_JWT_SECRET:
        return None

    try:
        decoded = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
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
