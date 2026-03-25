"""
matrx-ai — Matrx AI Engine

Core FastAPI backend for AI orchestration across 7 providers, multi-turn
conversations, tool execution, and streaming via SSE/NDJSON.

Quickstart (server mode — direct asyncpg to PostgreSQL):
    import matrx_ai
    matrx_ai.initialize()          # connects DB from env vars
    from matrx_ai.orchestrator.executor import execute_ai_request

Quickstart (client mode — desktop app, no direct DB access):
    import matrx_ai
    from matrx_ai.client_mode.config import ClientModeConfig
    import os

    matrx_ai.initialize(
        client_mode=True,
        client_config=ClientModeConfig(
            server_url=os.environ["AIDREAM_SERVER_URL_LIVE"],
            supabase_url="https://abc123.supabase.co",
            supabase_anon_key="eyJ...",
            get_jwt=lambda: auth_manager.current_token,
            conversation_handler=MyConversationHandler(),
        ),
    )
    # In client mode: public data (models, tools, content blocks) is fetched
    # from the server API. Conversation persistence is delegated to the
    # ConversationHandler provided above. No DB credentials are shipped.

Quickstart (FastAPI server — requires pip install matrx-ai[server]):
    matrx-ai-server                # CLI entry point
    # or programmatically:
    from matrx_ai.app.main import start
    start()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_ai.client_mode.config import ClientModeConfig

__version__ = "0.1.26"


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
    client_config: ClientModeConfig | None = None,
) -> None:
    """Initialize the matrx-ai library.

    Server mode (default):
        Connects the ORM directly to PostgreSQL via asyncpg.
        Reads connection parameters from environment variables via db_env_prefix.

    Client mode (client_mode=True):
        Skips asyncpg entirely. Public data (AI models, tools, content blocks,
        prompt builtins) is fetched from the AIDream server API. Conversation
        persistence is delegated to the ConversationHandler in client_config.
        Use when matrx-ai is embedded in a desktop application — no DB
        credentials are shipped to end users.

        Requires a fully configured ClientModeConfig. If any required field is
        missing, raises ClientModeConfigError listing every problem before doing
        anything else. There is no partial initialization.

    Args:
        database_url:
            Optional explicit PostgreSQL DSN (server mode only). When None,
            connection parameters are read from environment variables.
        db_name:
            ORM connection alias (default: "supabase_automation_matrix").
        db_env_prefix:
            Env var prefix for DB config (default: "SUPABASE_MATRIX").
        db_additional_schemas:
            Extra PostgreSQL schemas to expose (default: ["auth"]).
        db_env_var_overrides:
            Env var name overrides passed to register_database_from_env.
        client_mode:
            When True, activates client mode. Requires client_config.
        client_config:
            A ClientModeConfig instance (client mode only). All required fields
            are validated upfront; a ClientModeConfigError is raised on the
            first call if anything is missing.
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
        client_config=client_config,
    )
    _initialized = True


def is_client_mode() -> bool:
    """Return True if matrx-ai was initialized in client (desktop) mode.

    Use this to guard any code that would otherwise issue asyncpg queries.
    """
    from matrx_ai.db import is_client_mode as _is_client_mode
    return _is_client_mode()
