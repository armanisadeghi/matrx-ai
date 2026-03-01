import sys
import traceback

from fastapi import Request
from fastapi.responses import ORJSONResponse
from matrx_utils import vcprint


class MatrxException(Exception):
    def __init__(self, message: str, status_code: int = 500, detail: dict | None = None) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail or {}
        super().__init__(message)


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


async def matrx_exception_handler(request: Request, exc: MatrxException) -> ORJSONResponse:
    # Print directly to stderr — bypasses all logging infrastructure so this
    # is never silenced by uvicorn log config, log level filters, or handlers.
    print(
        f"\n[MatrxException] {request.method} {request.url.path}"
        f"\n  status={exc.status_code}  message={exc.message}"
        f"\n  detail={exc.detail}",
        file=sys.stderr,
        flush=True,
    )
    vcprint(
        {"status_code": exc.status_code, "message": exc.message, "detail": exc.detail, "path": str(request.url.path)},
        f"[Exception] {request.method} {request.url.path}",
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


async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse:
    tb = traceback.format_exc()
    # Print directly to stderr — bypasses all logging infrastructure.
    print(
        f"\n[UNHANDLED EXCEPTION] {request.method} {request.url.path}"
        f"\n  {type(exc).__name__}: {exc}"
        f"\n{tb}",
        file=sys.stderr,
        flush=True,
    )
    vcprint(
        tb,
        f"[Unhandled Exception] {request.method} {request.url.path} | {type(exc).__name__}: {exc}",
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
