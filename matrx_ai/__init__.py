"""
matrx-ai — Matrx AI Engine

Core FastAPI backend for AI orchestration across 7 providers, multi-turn
conversations, tool execution, and streaming via SSE/NDJSON.

Quickstart (library mode):
    import matrx_ai
    matrx_ai.initialize()          # connects DB from env vars
    from matrx_ai.orchestrator.executor import execute_ai_request

Quickstart (server mode — requires pip install matrx-ai[server]):
    matrx-ai-server                # CLI entry point
    # or programmatically:
    from matrx_ai.app.main import start
    start()
"""

from __future__ import annotations

__version__ = "0.1.8"


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
) -> None:
    """Initialize the matrx-ai library.

    Connects the ORM to PostgreSQL and loads environment variables. Call this
    once at application startup before using any db.* or orchestrator.* APIs.

    Args:
        database_url: Optional explicit DSN. When None, the ORM reads
            connection parameters from environment variables via env_prefix.
        db_name: ORM connection alias (default: "supabase_automation_matrix").
        db_env_prefix: Env var prefix for DB config (default: "SUPABASE_MATRIX").
        db_additional_schemas: Extra PostgreSQL schemas to expose (default: ["auth"]).
        db_env_var_overrides: Env var name overrides passed to register_database_from_env.
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
    )
    _initialized = True
