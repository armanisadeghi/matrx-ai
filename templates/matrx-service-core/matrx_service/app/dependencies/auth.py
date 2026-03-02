"""FastAPI route dependencies for auth gating.

Usage:
    from fastapi import APIRouter, Depends
    from matrx_service.app.dependencies.auth import (
        require_guest_or_above,
        require_authenticated,
        require_admin,
    )

    router = APIRouter()

    # Fingerprint or JWT
    @router.post("/endpoint", dependencies=[Depends(require_guest_or_above)])
    async def my_endpoint(): ...

    # JWT required
    @router.post("/secure", dependencies=[Depends(require_authenticated)])
    async def secure_endpoint(): ...

    # Admin only
    @router.post("/admin", dependencies=[Depends(require_admin)])
    async def admin_endpoint(): ...
"""

from __future__ import annotations

from fastapi import HTTPException, Request, status


async def require_guest_or_above(request: Request) -> None:
    """Allow fingerprint or token auth. Reject anonymous (no header at all)."""
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
    """Require a valid JWT. Rejects fingerprint and anonymous."""
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
    """Require a valid JWT AND admin flag (set by admin_api_token in config)."""
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
