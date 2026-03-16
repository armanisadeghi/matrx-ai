from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_orm.client import SupabaseAuth, SupabaseClientConfig

# Module-level state — set once during initialize(), then read-only.
_client_mode: bool = False
_client_singleton: tuple[SupabaseClientConfig, SupabaseAuth] | None = None


def _setup(
    database_url: str | None = None,
    *,
    name: str = "supabase_automation_matrix",
    env_prefix: str = "SUPABASE_MATRIX",
    additional_schemas: list[str] | None = None,
    env_var_overrides: dict[str, str] | None = None,
    client_mode: bool = False,
    supabase_url: str = "",
    supabase_anon_key: str = "",
) -> None:
    """Connect the ORM to a PostgreSQL instance, or configure the Supabase client adapter.

    Called by matrx_ai.initialize() or directly when you want full control
    over the database configuration without relying on .env auto-loading.

    When client_mode=True, skips the asyncpg connection entirely and sets up
    the Supabase PostgREST adapter (anon key + user JWT + RLS). Use this when
    matrx-ai is embedded in a desktop app distributed to end users.
    """
    if client_mode:
        _setup_client_mode(supabase_url, supabase_anon_key)
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


def _setup_client_mode(url: str, anon_key: str) -> None:
    """Initialize the Supabase PostgREST adapter for client-side (desktop) use.

    Stores a (SupabaseClientConfig, SupabaseAuth) singleton that can be
    retrieved via get_client_singleton(). No asyncpg connection is opened.
    The anon key is safe to embed in desktop apps — per-user RLS policies
    enforce data isolation via the user's JWT.
    """
    from matrx_orm.client import SupabaseAuth, SupabaseClientConfig

    global _client_mode, _client_singleton

    if not url:
        raise ValueError(
            "client_mode=True requires supabase_url. "
            "Set SUPABASE_URL in .env or pass it explicitly to initialize()."
        )
    if not anon_key:
        raise ValueError(
            "client_mode=True requires supabase_anon_key. "
            "Set SUPABASE_PUBLISHABLE_KEY in .env or pass it explicitly to initialize()."
        )

    config = SupabaseClientConfig(url=url, anon_key=anon_key)
    auth = SupabaseAuth(config)
    _client_singleton = (config, auth)
    _client_mode = True


def is_client_mode() -> bool:
    """Return True if matrx-ai was initialized in client (PostgREST) mode."""
    return _client_mode


def get_client_singleton() -> tuple[SupabaseClientConfig, SupabaseAuth]:
    """Return the (SupabaseClientConfig, SupabaseAuth) singleton.

    Raises RuntimeError if not initialized in client mode.
    """
    if _client_singleton is None:
        raise RuntimeError(
            "matrx-ai is not initialized in client mode. "
            "Call matrx_ai.initialize(client_mode=True, ...) first."
        )
    return _client_singleton
