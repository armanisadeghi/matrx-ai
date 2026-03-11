"""Structured exception hierarchy and FastAPI exception handlers.

All exceptions that cross API boundaries should subclass MatrxException.
This guarantees a consistent error response shape across every service:

    {
        "error":  "<human-readable message>",
        "detail": { ... structured context ... },
        "path":   "/api/..."
    }

Every handler writes directly to sys.stderr before returning a response
so errors are never silenced by uvicorn log config or level filters.
"""

import sys
import traceback

from fastapi import HTTPException, Request
from fastapi.responses import ORJSONResponse

from matrx_ai.context._log import log


class MatrxException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: dict | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


class NotFoundError(MatrxException):
    def __init__(self, resource: str, resource_id: str) -> None:
        super().__init__(
            message=f"{resource} '{resource_id}' not found",
            status_code=404,
            detail={"resource": resource, "id": resource_id},
        )


class ProviderError(MatrxException):
    def __init__(self, provider: str, message: str, detail: dict | None = None) -> None:
        super().__init__(
            message=f"Provider '{provider}' error: {message}",
            status_code=502,
            detail={"provider": provider, **(detail or {})},
        )


class AgentNotFoundError(MatrxException):
    def __init__(self, agent_id: str) -> None:
        super().__init__(
            message=f"Agent '{agent_id}' not found",
            status_code=404,
            detail={"agent_id": agent_id},
        )


class ToolNotFoundError(MatrxException):
    def __init__(self, tool_name: str) -> None:
        super().__init__(
            message=f"Tool '{tool_name}' not found",
            status_code=404,
            detail={"tool_name": tool_name},
        )


class StreamingError(MatrxException):
    def __init__(self, message: str) -> None:
        super().__init__(message=f"Streaming error: {message}", status_code=500)


class AuthorizationError(MatrxException):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(message=message, status_code=401, detail={"error": "unauthorized"})


class ForbiddenError(MatrxException):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(message=message, status_code=403, detail={"error": "forbidden"})


# ---------------------------------------------------------------------------
# Exception handlers — register all three in main.py
# ---------------------------------------------------------------------------


async def matrx_exception_handler(request: Request, exc: MatrxException) -> ORJSONResponse:
    print(
        f"\n[MatrxException] {request.method} {request.url.path}"
        f"\n  status={exc.status_code}  message={exc.message}"
        f"\n  detail={exc.detail}",
        file=sys.stderr,
        flush=True,
    )
    log(
        {"status_code": exc.status_code, "message": exc.message,
         "detail": exc.detail, "path": str(request.url.path)},
        title=f"[Exception] {request.method} {request.url.path}",
        color="red",
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "detail": exc.detail,
            "path": str(request.url.path),
        },
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> ORJSONResponse:
    """Log every HTTPException to stderr so 401/403/404 are never silent."""
    detail = exc.detail
    print(
        f"\n[HTTPException] {request.method} {request.url.path}"
        f"\n  status={exc.status_code}  detail={detail}",
        file=sys.stderr,
        flush=True,
    )
    log(
        {"status_code": exc.status_code, "detail": detail, "path": str(request.url.path)},
        title=f"[HTTPException] {request.method} {request.url.path}",
        color="yellow",
    )
    return ORJSONResponse(
        status_code=exc.status_code,
        content={"error": detail, "path": str(request.url.path)},
        headers=dict(exc.headers) if exc.headers else {},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    tb = traceback.format_exc()
    print(
        f"\n[UNHANDLED EXCEPTION] {request.method} {request.url.path}"
        f"\n  {type(exc).__name__}: {exc}"
        f"\n{tb}",
        file=sys.stderr,
        flush=True,
    )
    log(
        tb,
        title=f"[Unhandled] {request.method} {request.url.path} | {type(exc).__name__}: {exc}",
        color="red",
    )
    return ORJSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": {"type": type(exc).__name__, "message": str(exc)},
            "path": str(request.url.path),
        },
    )
