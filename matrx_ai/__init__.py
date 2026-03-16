"""
matrx-ai — Matrx AI Engine

Core FastAPI backend for AI orchestration across 7 providers, multi-turn
conversations, tool execution, and streaming via SSE/NDJSON.

Quickstart (library mode — server, direct asyncpg):
    import matrx_ai
    matrx_ai.initialize()          # connects DB from env vars
    from matrx_ai.orchestrator.executor import execute_ai_request

Quickstart (client mode — desktop app, Supabase PostgREST + RLS):
    import matrx_ai
    matrx_ai.initialize(
        client_mode=True,
        supabase_url="https://abc123.supabase.co",
        supabase_anon_key="eyJ...",
    )
    # No asyncpg connection; all DB access goes through the user's JWT + RLS.

Quickstart (server mode — requires pip install matrx-ai[server]):
    matrx-ai-server                # CLI entry point
    # or programmatically:
    from matrx_ai.app.main import start
    start()
"""

from __future__ import annotations

__version__ = "0.1.17"


def _get_version() -> str:
    try:
        from importlib.metadata import version

        return version("matrx-ai")
    except Exception:
        return __version__


__version__ = _get_version()

_initialized = False


def initialize(
    database_url: str | None = None,
    *,
    db_name: str = "supabase_automation_matrix",
    db_env_prefix: str = "SUPABASE_MATRIX",
    db_additional_schemas: list[str] | None = None,
    db_env_var_overrides: dict[str, str] | None = None,
    client_mode: bool = False,
    supabase_url: str = "",
    supabase_anon_key: str = "",
) -> None:
    """Initialize the matrx-ai library.

    Server mode (default): Connects the ORM directly to PostgreSQL via asyncpg.
    Reads connection parameters from environment variables via env_prefix.

    Client mode: Skips asyncpg entirely. Sets up the Supabase PostgREST adapter
    (anon key + user JWT + RLS policies). Use when matrx-ai is embedded in a
    desktop application distributed to end users — no DB credentials are shipped.

    Args:
        database_url: Optional explicit DSN (server mode only). When None, reads
            connection parameters from environment variables via env_prefix.
        db_name: ORM connection alias (default: "supabase_automation_matrix").
        db_env_prefix: Env var prefix for DB config (default: "SUPABASE_MATRIX").
        db_additional_schemas: Extra PostgreSQL schemas to expose (default: ["auth"]).
        db_env_var_overrides: Env var name overrides passed to register_database_from_env.
        client_mode: When True, uses Supabase PostgREST instead of asyncpg.
            Requires supabase_url and supabase_anon_key.
        supabase_url: Supabase project URL (client mode only).
            e.g. "https://abc123.supabase.co"
        supabase_anon_key: Supabase publishable anon key (client mode only).
            Safe to embed in desktop apps — RLS enforces per-user data isolation.
    """
    global _initialized
    if _initialized:
        return

    from matrx_ai.db import _setup

    _setup(
        database_url=database_url,
        name=db_name,
        env_prefix=db_env_prefix,
        additional_schemas=db_additional_schemas,
        env_var_overrides=db_env_var_overrides,
        client_mode=client_mode,
        supabase_url=supabase_url,
        supabase_anon_key=supabase_anon_key,
    )
    _initialized = True


def is_client_mode() -> bool:
    """Return True if matrx-ai was initialized in client (PostgREST/RLS) mode.

    Use this to guard any code that would otherwise issue asyncpg queries.
    """
    from matrx_ai.db import is_client_mode as _is_client_mode
    return _is_client_mode()
