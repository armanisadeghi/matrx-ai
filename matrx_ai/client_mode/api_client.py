"""
HTTP client for fetching public and authenticated data from the AIDream server.

Used exclusively in client mode (desktop app). All server URLs are read from
environment variables — never hard-coded. The canonical var is:

    AIDREAM_SERVER_URL_LIVE=https://server.app.matrxserver.com

To enumerate all configured targets (e.g. for a debug UI), iterate over any
environment variable matching the AIDREAM_SERVER_URL_* prefix.

Available endpoints (see api-endpoints.md):
    Public (no auth):
        GET /api/ai-models
        GET /api/ai-tools
        GET /api/ai-tools/app/{source_app}
        GET /api/content-blocks
        GET /api/prompts/builtins

    Authenticated (Authorization: Bearer <jwt>):
        GET /api/prompts
        GET /api/prompts/all
        GET /api/cx/conversations
        GET /api/cx/conversations/{conversation_id}
"""

from __future__ import annotations

import os
from typing import Any

import httpx
from matrx_utils import vcprint

_SERVER_URL_ENV = "AIDREAM_SERVER_URL_LIVE"


def _get_server_url() -> str:
    url = os.environ.get(_SERVER_URL_ENV, "").rstrip("/")
    if not url:
        raise RuntimeError(
            f"Environment variable {_SERVER_URL_ENV!r} is not set. "
            "Client mode requires a server URL to fetch models, tools, and other data."
        )
    return url


def get_all_server_urls() -> dict[str, str]:
    """Return all AIDREAM_SERVER_URL_* environment variables as {suffix: url}.

    Useful for debug tooling that needs to enumerate all configured targets.
    e.g. {"LIVE": "https://server.app.matrxserver.com", "LOCAL": "http://localhost:8000"}
    """
    prefix = "AIDREAM_SERVER_URL_"
    return {
        key[len(prefix):]: val
        for key, val in os.environ.items()
        if key.startswith(prefix) and val
    }


class ApiClient:
    """
    Thin async HTTP client for the AIDream REST API.

    All methods raise httpx.HTTPStatusError for non-2xx responses.
    All methods raise RuntimeError if AIDREAM_SERVER_URL_LIVE is not set.

    This client is instantiated once by the client_mode module and reused
    across the lifetime of the application.
    """

    def __init__(self, base_url: str | None = None) -> None:
        self._base_url = (base_url or _get_server_url()).rstrip("/")

    @property
    def base_url(self) -> str:
        return self._base_url

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _get(
        self,
        path: str,
        jwt: str | None = None,
        timeout: float = 30.0,
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        headers: dict[str, str] = {}
        if jwt:
            headers["Authorization"] = f"Bearer {jwt}"
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            vcprint(
                f"[ApiClient] HTTP {exc.response.status_code} from {url}: {exc.response.text[:500]}",
                color="red",
            )
            raise
        except Exception as exc:
            vcprint(f"[ApiClient] Request failed for {url}: {exc}", color="red")
            raise

    # ------------------------------------------------------------------
    # Public endpoints (no auth required)
    # ------------------------------------------------------------------

    async def get_models(self) -> list[dict[str, Any]]:
        """GET /api/ai-models — returns all AI models."""
        data = await self._get("/api/ai-models")
        return data.get("models", [])

    async def get_tools(self, source_app: str | None = None) -> list[dict[str, Any]]:
        """GET /api/ai-tools or /api/ai-tools/app/{source_app} — returns tools."""
        if source_app:
            data = await self._get(f"/api/ai-tools/app/{source_app}")
        else:
            data = await self._get("/api/ai-tools")
        return data.get("tools", [])

    async def get_content_blocks(self) -> list[dict[str, Any]]:
        """GET /api/content-blocks — returns all content blocks."""
        data = await self._get("/api/content-blocks")
        return data.get("content_blocks", [])

    async def get_content_blocks_by_category(self, category_id: str) -> list[dict[str, Any]]:
        """GET /api/content-blocks/category/{category_id}"""
        data = await self._get(f"/api/content-blocks/category/{category_id}")
        return data.get("content_blocks", [])

    async def get_content_block(self, block_id: str) -> dict[str, Any]:
        """GET /api/content-blocks/{block_id}"""
        data = await self._get(f"/api/content-blocks/{block_id}")
        return data.get("content_block", {})

    async def get_prompt_builtins(self) -> list[dict[str, Any]]:
        """GET /api/prompts/builtins — returns all prompt builtins (no auth)."""
        data = await self._get("/api/prompts/builtins")
        return data.get("builtins", [])

    # ------------------------------------------------------------------
    # Authenticated endpoints (JWT required)
    # ------------------------------------------------------------------

    async def get_user_prompts(self, jwt: str) -> list[dict[str, Any]]:
        """GET /api/prompts — returns prompts belonging to the authenticated user."""
        data = await self._get("/api/prompts", jwt=jwt)
        return data.get("prompts", [])

    async def get_all_prompts(self, jwt: str) -> dict[str, Any]:
        """GET /api/prompts/all — returns user prompts + all builtins in one call."""
        return await self._get("/api/prompts/all", jwt=jwt)

    async def get_conversations(self, jwt: str) -> list[dict[str, Any]]:
        """GET /api/cx/conversations — returns all conversations for the authenticated user."""
        data = await self._get("/api/cx/conversations", jwt=jwt)
        return data.get("conversations", [])

    async def get_conversation(self, conversation_id: str, jwt: str) -> dict[str, Any]:
        """GET /api/cx/conversations/{conversation_id} — returns conversation + related data."""
        return await self._get(f"/api/cx/conversations/{conversation_id}", jwt=jwt)

    async def get_conversation_requests(
        self, conversation_id: str, jwt: str
    ) -> list[dict[str, Any]]:
        """GET /api/cx/conversations/{conversation_id}/requests"""
        data = await self._get(
            f"/api/cx/conversations/{conversation_id}/requests", jwt=jwt
        )
        return data.get("requests", [])
