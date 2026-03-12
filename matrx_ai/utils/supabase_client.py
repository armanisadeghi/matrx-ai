from __future__ import annotations

import os

import httpx
from supabase import AsyncClient, create_client
from supabase.lib.client_options import AsyncClientOptions

_supabase_instance = None
_async_supabase_instance: AsyncClient | None = None

_DEFAULT_HTTP_TIMEOUT = 30.0


def _connection_details() -> tuple[str, str]:
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "") or os.environ.get("SUPABASE_ANON_KEY", "")
    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY) must be set."
        )
    return url, key


def get_supabase_client():
    global _supabase_instance
    if _supabase_instance is None:
        url, key = _connection_details()
        _supabase_instance = create_client(url, key)
    return _supabase_instance


def get_async_supabase_client() -> AsyncClient:
    global _async_supabase_instance
    if _async_supabase_instance is None:
        url, key = _connection_details()
        http_client = httpx.AsyncClient(timeout=_DEFAULT_HTTP_TIMEOUT)
        options = AsyncClientOptions(httpx_client=http_client)
        _async_supabase_instance = AsyncClient(url, key, options)
    return _async_supabase_instance
