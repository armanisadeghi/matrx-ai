from __future__ import annotations

from fastapi import HTTPException, Request, status


async def require_guest_or_above(request: Request) -> None:
    ctx = request.state.context
    if ctx.auth_type == "anonymous":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "auth_required",
                "message": "Authentication or X-Fingerprint-ID header required",
            },
        )


async def require_authenticated(request: Request) -> None:
    ctx = request.state.context
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "token_required",
                "message": "Valid authentication token required",
            },
        )


async def require_admin(request: Request) -> None:
    ctx = request.state.context
    if not ctx.is_authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "token_required",
                "message": "Valid authentication token required",
            },
        )
    if not ctx.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "admin_required",
                "message": "Admin access required",
            },
        )
