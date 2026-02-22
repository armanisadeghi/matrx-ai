"""Centralized test/dev context factory.

Produces fully-formed AppContext objects identical to what AuthMiddleware
creates for real requests. No fakes, no silent defaults — everything must
be backed by a real value from .env or the call raises immediately.

Required environment variables (must be set in .env):
    DEVELOPER_USER_ID        -- Your personal Supabase UUID (no placeholder allowed)
    TEST_USER_EMAIL          -- Email associated with your Supabase account
    TEST_CONVERSATION_ID     -- A real conversation UUID for repeatable tests

Optional environment variables:
    TEST_PROJECT_ID          -- Project UUID for scoped tests
    TEST_ORGANIZATION_ID     -- Organization UUID for scoped tests

Rules enforced:
    - DEVELOPER_USER_ID must be a valid non-empty UUID string — no empty string,
      no placeholder like "your-user-id-here"
    - TEST_USER_EMAIL must contain "@"
    - Emitter is always a real ConsoleEmitter — never None, never a mock
    - request_id is always a fresh UUID — callers cannot pass empty strings
    - ip_address and user_agent are the only fields allowed to be synthetic
      ("127.0.0.1" / "ai-dream-test/1.0") since they are browser-only values

Usage:
    from tests.ai.test_context import create_test_app_context

    token = create_test_app_context()
    session = create_test_session()

    from tests.ai.test_context import create_test_tool_context
    ctx = create_test_tool_context("web_search")

    from context.app_context import clear_app_context
    clear_app_context(token)
"""
from __future__ import annotations

import os
from contextvars import Token
from uuid import uuid4

from context.app_context import AppContext, set_app_context
from context.emitter_protocol import Emitter
from context.console_emitter import ConsoleEmitter
from prompts.session import SimpleSession
from tools.models import ToolContext


# ---------------------------------------------------------------------------
# Environment helpers — always raise on missing or invalid values
# ---------------------------------------------------------------------------

def _require_env(key: str, validator: callable | None = None, hint: str = "") -> str:
    val = os.environ.get(key, "").strip()
    if not val:
        raise EnvironmentError(
            f"[test_context] Required env var '{key}' is not set. "
            f"Add it to your .env file before running tests."
            + (f" Hint: {hint}" if hint else "")
        )
    if validator and not validator(val):
        raise EnvironmentError(
            f"[test_context] Env var '{key}' has an invalid value: {val!r}. "
            + (f"Hint: {hint}" if hint else "")
        )
    return val


def _optional_env(key: str) -> str | None:
    val = os.environ.get(key, "").strip()
    return val or None


def _is_valid_uuid(val: str) -> bool:
    import re
    return bool(re.match(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
        val.lower(),
    ))


def _is_valid_email(val: str) -> bool:
    return "@" in val and "." in val.split("@")[-1]


def get_developer_user_id() -> str:
    return _require_env(
        "DEVELOPER_USER_ID",
        validator=_is_valid_uuid,
        hint="Must be your real Supabase user UUID, e.g. 4cf62e4e-2679-484f-b652-034e697418df",
    )


def get_test_email() -> str:
    return _require_env(
        "TEST_USER_EMAIL",
        validator=_is_valid_email,
        hint="Must be the email address for your Supabase account.",
    )


def get_test_conversation_id() -> str:
    return _require_env(
        "TEST_CONVERSATION_ID",
        validator=_is_valid_uuid,
        hint="Must be a real conversation UUID. Create one or use an existing one from the DB.",
    )


def get_test_project_id() -> str | None:
    val = _optional_env("TEST_PROJECT_ID")
    if val and not _is_valid_uuid(val):
        raise EnvironmentError(
            f"[test_context] TEST_PROJECT_ID is set but is not a valid UUID: {val!r}"
        )
    return val


def get_test_organization_id() -> str | None:
    val = _optional_env("TEST_ORGANIZATION_ID")
    if val and not _is_valid_uuid(val):
        raise EnvironmentError(
            f"[test_context] TEST_ORGANIZATION_ID is set but is not a valid UUID: {val!r}"
        )
    return val


# ---------------------------------------------------------------------------
# AppContext factory — the ONE way to create context for tests/dev scripts
# ---------------------------------------------------------------------------

def create_test_app_context(
    *,
    conversation_id: str | None = None,
    project_id: str | None = None,
    organization_id: str | None = None,
    emitter: Emitter | None = None,
    label: str = "test",
    debug: bool = True,
    is_admin: bool = False,
    new_conversation: bool = False,
) -> Token:
    """
    Build a fully-formed AppContext from .env values and set it as the active
    context (ContextVar). Returns the Token needed to restore state when done.

    All identity fields use real values from .env — no fakes, no empty strings.
    Raises EnvironmentError immediately if any required env var is missing or invalid.

        token = create_test_app_context()
        # ... run test ...
        from context.app_context import clear_app_context
        clear_app_context(token)
    """
    conv_id = str(uuid4()) if new_conversation else (conversation_id or get_test_conversation_id())

    ctx = AppContext(
        user_id=get_developer_user_id(),
        email=get_test_email(),
        auth_type="token",
        is_authenticated=True,
        is_admin=is_admin,
        fingerprint_id=None,
        ip_address="127.0.0.1",        # synthetic: browser-only, irrelevant in tests
        user_agent="ai-dream-test/1.0", # synthetic: browser-only, irrelevant in tests
        token=None,
        request_id=str(uuid4()),        # always a fresh UUID — never empty
        project_id=project_id or get_test_project_id(),
        organization_id=organization_id or get_test_organization_id(),
        debug=debug,
        emitter=emitter or ConsoleEmitter(label, debug=debug),
        conversation_id=conv_id,
    )
    return set_app_context(ctx)


# ---------------------------------------------------------------------------
# SimpleSession — requires AppContext to already be set
# ---------------------------------------------------------------------------

def create_test_session(
    *,
    conversation_id: str | None = None,
    debug: bool = True,
    new_conversation: bool = False,
) -> SimpleSession:
    conv_id = str(uuid4()) if new_conversation else (conversation_id or get_test_conversation_id())
    return SimpleSession(conversation_id=conv_id, debug=debug)


# ---------------------------------------------------------------------------
# ToolContext — requires AppContext to already be set
# ---------------------------------------------------------------------------

def create_test_tool_context(
    tool_name: str,
    *,
    call_id: str | None = None,
    iteration: int = 0,
    user_role: str = "user",
    cost_budget_remaining: float | None = None,
) -> ToolContext:
    return ToolContext(
        call_id=call_id or f"call_{uuid4().hex[:12]}",
        tool_name=tool_name,
        iteration=iteration,
        user_role=user_role,
        cost_budget_remaining=cost_budget_remaining,
    )


# ---------------------------------------------------------------------------
# Backward-compat alias — old test files that still call the old name work
# ---------------------------------------------------------------------------

create_test_execution_context = create_test_app_context
