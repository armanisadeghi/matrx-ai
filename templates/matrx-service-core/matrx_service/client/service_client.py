"""Outbound HTTP client for service-to-service calls.

Reads the current AppContext from the ContextVar and injects the standard
Matrx propagation headers so that downstream services reconstruct an
equivalent context via their own AuthMiddleware.

Propagated headers
------------------
Authorization       : Bearer <token>  (if user has a JWT or admin token)
X-Fingerprint-ID    : <fingerprint>   (if guest auth)
X-Request-ID        : <request_id>    (for distributed tracing)
X-Conversation-ID   : <conv_id>       (for conversation continuity)
X-User-ID           : <user_id>       (for quick identity lookup without JWT decode)
X-Internal-Agent    : "true"          (marks request as service-originated)

Usage
-----
    from matrx_service.client.service_client import ServiceClient

    # One-shot request (creates and closes the client):
    client = ServiceClient(base_url="http://matrx-ai:8000")
    response = await client.post("/api/ai/chat", json={"messages": [...]})

    # Reuse across a request lifetime:
    async with ServiceClient(base_url="http://matrx-ai:8000") as client:
        response = await client.post("/api/ai/chat", json={...})

    # Stream NDJSON response:
    async with ServiceClient(base_url="http://matrx-media:8001") as client:
        async for event in client.stream_ndjson("/api/process", json={...}):
            print(event)  # each event is a parsed dict

    # Convenience — resolve base URL from settings without hard-coding:
    client = ServiceClient.for_service("matrx_ai")   # reads MATRX_AI_URL from env
"""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from matrx_service.context.app_context import try_get_app_context

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = httpx.Timeout(connect=5.0, read=120.0, write=30.0, pool=5.0)


class ServiceClient:
    """Async HTTP client that propagates Matrx request context.

    Can be used as a context manager or as a plain instance (auto-managed).
    """

    def __init__(
        self,
        base_url: str,
        timeout: httpx.Timeout = DEFAULT_TIMEOUT,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._extra_headers = extra_headers or {}
        self._client: httpx.AsyncClient | None = None

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> ServiceClient:
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._build_context_headers(),
        )
        return self

    async def __aexit__(self, *_: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    # ------------------------------------------------------------------
    # Convenience constructor
    # ------------------------------------------------------------------

    @classmethod
    def for_service(cls, service_env_key: str, **kwargs: Any) -> ServiceClient:
        """Instantiate using a URL read from an environment variable.

        The env var name is derived from the key: "matrx_ai" → MATRX_AI_URL.

        Example:
            # .env: MATRX_AI_URL=http://matrx-ai:8000
            client = ServiceClient.for_service("matrx_ai")
        """
        import os

        env_var = f"{service_env_key.upper()}_URL"
        url = os.environ.get(env_var, "")
        if not url:
            raise ValueError(
                f"ServiceClient.for_service('{service_env_key}'): "
                f"env var {env_var!r} is not set."
            )
        return cls(base_url=url, **kwargs)

    # ------------------------------------------------------------------
    # Header builder
    # ------------------------------------------------------------------

    def _build_context_headers(self) -> dict[str, str]:
        """Read current AppContext and build propagation headers."""
        headers: dict[str, str] = {}

        ctx = try_get_app_context()
        if ctx is not None:
            if ctx.token:
                headers["Authorization"] = f"Bearer {ctx.token}"
            elif ctx.fingerprint_id:
                headers["X-Fingerprint-ID"] = ctx.fingerprint_id

            if ctx.request_id:
                headers["X-Request-ID"] = ctx.request_id
            if ctx.conversation_id:
                headers["X-Conversation-ID"] = ctx.conversation_id
            if ctx.user_id:
                headers["X-User-ID"] = ctx.user_id
            if ctx.is_internal_agent:
                headers["X-Internal-Agent"] = "true"

        headers.update(self._extra_headers)
        return headers

    # ------------------------------------------------------------------
    # Request helpers — work in both managed (async with) and one-shot mode
    # ------------------------------------------------------------------

    def _make_one_shot_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._build_context_headers(),
        )

    async def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """GET request. Raises httpx.HTTPStatusError for 4xx/5xx."""
        if self._client is not None:
            response = await self._client.get(path, **kwargs)
            response.raise_for_status()
            return response
        async with self._make_one_shot_client() as client:
            response = await client.get(path, **kwargs)
            response.raise_for_status()
            return response

    async def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """POST request. Raises httpx.HTTPStatusError for 4xx/5xx."""
        if self._client is not None:
            response = await self._client.post(path, **kwargs)
            response.raise_for_status()
            return response
        async with self._make_one_shot_client() as client:
            response = await client.post(path, **kwargs)
            response.raise_for_status()
            return response

    async def post_json(self, path: str, body: dict[str, Any], **kwargs: Any) -> Any:
        """POST with JSON body. Returns parsed response JSON."""
        response = await self.post(path, json=body, **kwargs)
        return response.json()

    async def stream_ndjson(
        self,
        path: str,
        method: str = "POST",
        **kwargs: Any,
    ) -> AsyncGenerator[dict[str, Any]]:
        """Consume an NDJSON streaming response line by line.

        Yields each parsed JSON object. Non-JSON lines are logged and skipped.
        Raises httpx.HTTPStatusError if the response status is 4xx/5xx.

        Example:
            async for event in client.stream_ndjson("/api/ai/chat", json={...}):
                if event.get("event") == "chunk":
                    print(event["data"]["text"], end="", flush=True)
                elif event.get("event") == "end":
                    break
        """
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            headers=self._build_context_headers(),
        ) as client:
            async with client.stream(method, path, **kwargs) as response:
                response.raise_for_status()
                async for raw_line in response.aiter_lines():
                    line = raw_line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning("ServiceClient: non-JSON line skipped: %r", line)
