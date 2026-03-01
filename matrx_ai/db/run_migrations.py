"""ORM migration runner for matrx-ai.

Only the tables listed in MANAGED_TABLES are tracked by this migration set.
All other tables in the database are ignored — they won't be created, dropped,
or modified by these migrations.

Usage
-----
Generate a migration file from model/DB differences:

    python run_migrations.py make

Apply all pending migrations to the database:

    python run_migrations.py apply

Roll back the last migration:

    python run_migrations.py rollback

Show which migrations have been applied:

    python run_migrations.py status

Create a blank migration file for hand-written SQL:

    python run_migrations.py empty --name my_custom_change
"""

import asyncio
import sys

from dotenv import load_dotenv

load_dotenv()

from matrx_orm import (
    create_empty,
    makemigrations,
    migrate,
    migration_status,
    register_database_from_env,
    rollback,
)

register_database_from_env(
    name="supabase_automation_matrix",
    env_prefix="SUPABASE_MATRIX",
    additional_schemas=["auth"],
    env_var_overrides={"NAME": "SUPABASE_MATRIX_DATABASE_NAME"},
)

DATABASE = "supabase_automation_matrix"
MIGRATIONS_DIR = "migrations"

MANAGED_TABLES = {
    "cx_conversation",
    "cx_messages",
    "cx_agent_memory",
    "cx_media",
    "cx_request",
    "cx_tool_call",
    "cx_user_request",
    "ai_model",
}


async def make(name: str | None = None) -> None:
    await makemigrations(
        DATABASE,
        MIGRATIONS_DIR,
        name=name,
        include_tables=MANAGED_TABLES,
    )


async def apply() -> None:
    await migrate(DATABASE, MIGRATIONS_DIR)


async def rollback_last(steps: int = 1) -> None:
    await rollback(DATABASE, MIGRATIONS_DIR, steps=steps)


async def status() -> None:
    await migration_status(DATABASE, MIGRATIONS_DIR)


async def empty(name: str = "custom") -> None:
    await create_empty(DATABASE, MIGRATIONS_DIR, name=name)


def _usage() -> None:
    print(__doc__)
    sys.exit(1)


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args:
        _usage()

    command = args[0]

    match command:
        case "make":
            name_arg = args[1] if len(args) > 1 else None
            asyncio.run(make(name=name_arg))
        case "apply":
            asyncio.run(apply())
        case "rollback":
            steps = int(args[1]) if len(args) > 1 else 1
            asyncio.run(rollback_last(steps=steps))
        case "status":
            asyncio.run(status())
        case "empty":
            name_arg = args[1] if len(args) > 1 else "custom"
            asyncio.run(empty(name=name_arg))
        case _:
            print(f"Unknown command: {command!r}")
            _usage()
