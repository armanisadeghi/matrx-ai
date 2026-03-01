from __future__ import annotations


def _setup(
    database_url: str | None = None,
    *,
    name: str = "supabase_automation_matrix",
    env_prefix: str = "SUPABASE_MATRIX",
    additional_schemas: list[str] | None = None,
    env_var_overrides: dict[str, str] | None = None,
) -> None:
    """Connect the ORM to a PostgreSQL instance.

    Called by matrx_ai.initialize() or directly when you want full control
    over the database configuration without relying on .env auto-loading.
    """
    from dotenv import load_dotenv
    from matrx_orm import register_database_from_env

    load_dotenv()
    register_database_from_env(
        name=name,
        env_prefix=env_prefix,
        additional_schemas=additional_schemas if additional_schemas is not None else ["auth"],
        env_var_overrides=env_var_overrides if env_var_overrides is not None else {"NAME": "SUPABASE_MATRIX_DATABASE_NAME"},
    )
