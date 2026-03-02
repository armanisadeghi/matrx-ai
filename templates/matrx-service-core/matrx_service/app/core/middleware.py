"""Request context middleware — pure ASGI.

Attaches a unique request ID to every HTTP/WebSocket request and logs
method, path, status code, and elapsed time. Implemented as pure ASGI
(not BaseHTTPMiddleware) so streaming responses are never buffered and
exceptions inside async generators are never swallowed.

The request ID is stored in scope["state"].request_id and is also
emitted as the X-Request-ID response header (added by create_streaming_response).
"""

import logging
import time
import uuid
from typing import Any

from starlette.types import ASGIApp, Receive, Scope, Send

logger = logging.getLogger(__name__)


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        scope.setdefault("state", {})
        if hasattr(scope.get("state"), "__dict__"):
            scope["state"].request_id = request_id  # type: ignore[union-attr]
        else:
            scope["state"]["request_id"] = request_id  # type: ignore[index]

        start = time.perf_counter()
        status_code: int = 0

        async def send_with_capture(message: Any) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, send_with_capture)
        finally:
            if scope["type"] == "http":
                elapsed_ms = (time.perf_counter() - start) * 1000
                method = scope.get("method", "")
                path = scope.get("path", "")
                logger.info(
                    "%s %s %s %.2fms id=%s",
                    method,
                    path,
                    status_code,
                    elapsed_ms,
                    request_id,
                )
