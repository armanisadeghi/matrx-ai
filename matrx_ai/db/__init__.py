from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_ai.client_mode.config import ClientModeConfig

# Module-level state — set once during initialize(), then read-only.
_client_mode: bool = False


def _setup(
    database_url: str | None = None,
    *,
    name: str = "supabase_automation_matrix",
    env_prefix: str = "SUPABASE_MATRIX",
    additional_schemas: list[str] | None = None,
    env_var_overrides: dict[str, str] | None = None,
    client_mode: bool = False,
    client_config: ClientModeConfig | None = None,
    # Legacy keyword arguments kept for backwards-compatibility with any
    # callers that still pass supabase_url / supabase_anon_key directly.
    # These are silently ignored when client_config is provided.
    supabase_url: str = "",
    supabase_anon_key: str = "",
) -> None:
    """Connect the ORM to a PostgreSQL instance, or activate client mode.

    Called by matrx_ai.initialize() or directly when you want full control
    over the database configuration without relying on .env auto-loading.

    When client_mode=True:
        - asyncpg connection is never opened.
        - client_config is validated fail-fast (all errors listed upfront).
        - The validated config + ApiClient singleton are stored in
          matrx_ai.client_mode for use by every subsystem.
    """
    if client_mode:
        _setup_client_mode(client_config, supabase_url=supabase_url, supabase_anon_key=supabase_anon_key)
        return

    from dotenv import load_dotenv
    from matrx_orm import register_database_from_env

    load_dotenv()
    register_database_from_env(
        name=name,
        env_prefix=env_prefix,
        additional_schemas=additional_schemas if additional_schemas is not None else ["auth"],
        env_var_overrides=env_var_overrides if env_var_overrides is not None else {"NAME": "SUPABASE_MATRIX_DATABASE_NAME"},
    )


def _setup_client_mode(
    config: ClientModeConfig | None,
    *,
    supabase_url: str = "",
    supabase_anon_key: str = "",
) -> None:
    """Validate ClientModeConfig and activate client mode.

    If config is None but legacy supabase_url/anon_key were passed, builds a
    minimal ClientModeConfig from them (backwards-compat only — missing
    conversation_handler means any conversation operation will raise at runtime).

    Stores the validated config and creates the ApiClient singleton in
    matrx_ai.client_mode. Sets the module-level _client_mode flag.
    """
    from matrx_ai.client_mode.config import ClientModeConfig as _ClientModeConfig

    global _client_mode

    if config is None:
        # Legacy path: caller passed supabase_url + supabase_anon_key directly.
        # Build a partial config — missing get_jwt and conversation_handler will
        # cause errors at runtime, not at init time. This path is deprecated.
        import os
        config = _ClientModeConfig(
            server_url=os.environ.get("AIDREAM_SERVER_URL_LIVE", ""),
            supabase_url=supabase_url,
            supabase_anon_key=supabase_anon_key,
            get_jwt=lambda: None,
            conversation_handler=None,
        )

    # Validate all required fields upfront — fail loudly with a full list of
    # every missing field before doing anything else.
    config.validate()

    # Activate the client_mode module state.
    from matrx_ai.client_mode import _activate
    _activate(config)

    # Register the PostgRESTClientAdapter so that all BaseManager / QueryBuilder
    # operations transparently route through Supabase PostgREST instead of
    # trying to open an asyncpg connection.
    try:
        from matrx_orm.adapters import AdapterRegistry
        from matrx_orm.adapters.postgrest_client_adapter import PostgRESTClientAdapter
        adapter = PostgRESTClientAdapter(
            url=config.supabase_url,
            anon_key=config.supabase_anon_key,
            get_jwt=config.get_jwt,
        )
        AdapterRegistry.register("supabase_automation_matrix", adapter)
    except Exception as _exc:  # pragma: no cover
        import logging as _logging
        _logging.getLogger("matrx_ai.db").warning(
            "Could not register PostgRESTClientAdapter: %s — "
            "BaseManager auto-fetch will be skipped in client mode.",
            _exc,
        )

    _client_mode = True


def is_client_mode() -> bool:
    """Return True if matrx-ai was initialized in client (desktop) mode."""
    return _client_mode
