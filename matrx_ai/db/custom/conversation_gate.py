"""
Conversation Gate — Ensures cx_conversation and cx_user_request rows
exist before AI execution begins.

All database lifecycle setup is driven from ``execute_until_complete()``
in ``ai.executor``.  This guarantees that every execution path —
API routes, tests, agent-to-agent, internal services — gets the same
treatment.  Callers never need to manage database rows themselves.

**Conversation** — ``ensure_conversation_exists()``

  Idempotent: creates the ``cx_conversation`` row if it does not already
  exist, and is a no-op if it does.  Called at the start of
  ``execute_until_complete()`` before any other persistence.

  API routes may additionally call ``verify_existing_conversation()`` as
  an early-exit check for the ``is_new_conversation=False`` path.

**User Request** — ``create_pending_user_request()``

  A ``cx_user_request`` row with ``status='pending'`` is inserted at the
  start of ``execute_until_complete()``, using the ``request_id`` from
  ``AIMatrixRequest`` as the primary key.  This guarantees:
    - Every request attempt is recorded, even those that crash mid-flight.
    - Downstream ``cx_tool_call`` rows can immediately reference the
      ``request_id`` FK without a post-hoc backfill.

Downstream persistence (``ai.db.persistence``) only **updates** — it
never creates conversations or user requests.
"""

from __future__ import annotations  # noqa: I001

import asyncio
import traceback
from typing import Any
from uuid import UUID

from matrx_utils import vcprint
from .cx_managers import cxm


class ConversationGateError(Exception):
    pass


def _is_valid_uuid(value: str | None) -> bool:
    if not value:
        return False
    try:
        UUID(value)
        return True
    except (ValueError, AttributeError):
        return False


def _require_valid_user_id(user_id: str | None, context: str = "") -> str:
    if _is_valid_uuid(user_id):
        return user_id  # type: ignore[return-value]
    label = f" ({context})" if context else ""
    raise ConversationGateError(
        f"Invalid user_id{label}: {user_id!r} — "
        f"a valid UUID is required. Guest/anonymous users cannot create "
        f"database records without a proper user mapping."
    )


# =========================================================================
# Core operations
# =========================================================================


async def create_new_conversation(
    conversation_id: str,
    user_id: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    """INSERT a cx_conversation row with the given client-generated ID.

    Reads ``initial_variables`` and ``initial_overrides`` from the current
    AppContext (set by agent/chat routes via ctx.extend()) so they are
    written on creation without callers needing to pass them explicitly.

    Raises ``ConversationGateError`` on any failure (duplicate PK, FK
    violation, network error, etc.).
    """
    if not _is_valid_uuid(conversation_id):
        raise ConversationGateError(
            f"conversation_id is not a valid UUID: {conversation_id!r}"
        )

    safe_user_id = _require_valid_user_id(user_id, "create_new_conversation")

    from matrx_ai.context.app_context import try_get_app_context

    ctx = try_get_app_context()

    create_kwargs: dict[str, Any] = {
        "id": conversation_id,
        "user_id": safe_user_id,
        "status": "active",
        "message_count": 0,
        "config": {},
        "metadata": metadata or {},
        "variables": ctx.initial_variables if ctx else {},
        "overrides": ctx.initial_overrides if ctx else {},
    }

    try:
        await cxm.conversation.create_cx_conversation(**create_kwargs)
        vcprint(
            f"[ConversationGate] Created conversation: {conversation_id}...",
            color="green",
        )
    except Exception as exc:
        raise ConversationGateError(
            f"Failed to create conversation {conversation_id}: {exc}"
        ) from exc


async def ensure_conversation_exists(
    conversation_id: str,
    user_id: str,
    parent_conversation_id: str | None = None,
) -> None:
    """Ensure a cx_conversation row exists for the given ID.

    Idempotent: creates if missing, no-op if already present.
    Called at the start of ``execute_until_complete()`` so every
    execution path (API, test, agent-to-agent, internal) is covered.

    On creation, writes ``initial_variables`` and ``initial_overrides``
    from the current AppContext (set by agent/chat routes via ctx.extend()).
    These are write-once — subsequent calls for the same conversation_id
    are no-ops and never overwrite them.

    Fire-and-forget safe — logs errors but never raises.

    In client mode (desktop app / PostgREST + RLS), this is a no-op —
    conversation rows are managed via the user's JWT and RLS policies,
    not pre-created server-side.
    """
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        from matrx_ai.client_mode import get_conversation_handler
        from matrx_ai.context.app_context import try_get_app_context
        ctx = try_get_app_context()
        try:
            await get_conversation_handler().ensure_conversation_exists(
                conversation_id=conversation_id,
                user_id=user_id,
                parent_conversation_id=parent_conversation_id,
                variables=ctx.initial_variables if ctx else {},
                overrides=ctx.initial_overrides if ctx else {},
            )
        except Exception as exc:
            vcprint(
                f"[ConversationGate] ConversationHandler.ensure_conversation_exists failed: {exc}",
                color="yellow",
            )
        return

    if not _is_valid_uuid(conversation_id):
        vcprint(
            f"[ConversationGate] Cannot ensure conversation: "
            f"not a valid UUID: {conversation_id!r}",
            color="yellow",
        )
        return

    safe_user_id = _require_valid_user_id(user_id, "ensure_conversation_exists")

    existing = await cxm.conversation.filter_cx_conversations(
        id=conversation_id,
    )
    if existing:
        return

    # Read write-once creation data from context (may be empty for non-agent calls)
    from matrx_ai.context.app_context import try_get_app_context

    ctx = try_get_app_context()

    create_kwargs: dict[str, Any] = {
        "id": conversation_id,
        "user_id": safe_user_id,
        "status": "active",
        "message_count": 0,
        "config": {},
        "metadata": {},
        "variables": ctx.initial_variables if ctx else {},
        "overrides": ctx.initial_overrides if ctx else {},
    }
    if parent_conversation_id and _is_valid_uuid(parent_conversation_id):
        create_kwargs["parent_conversation_id"] = parent_conversation_id

    try:
        await cxm.conversation.create_cx_conversation(**create_kwargs)
        vcprint(
            f"[ConversationGate] Auto-created conversation: {conversation_id}",
            color="green",
        )
    except Exception as exc:
        recheck = await cxm.conversation.filter_cx_conversations(
            id=conversation_id,
        )
        if recheck:
            return
        vcprint(
            f"[ConversationGate] Failed to ensure conversation: {exc}",
            color="yellow",
        )


async def verify_existing_conversation(
    conversation_id: str,
) -> dict[str, Any]:
    """SELECT and return the conversation row.

    Raises ``ConversationGateError`` if the conversation does not exist or
    the ID is invalid.
    """
    if not _is_valid_uuid(conversation_id):
        raise ConversationGateError(
            f"conversation_id is not a valid UUID: {conversation_id!r}"
        )

    matches = await cxm.conversation.filter_cx_conversations(
        id=conversation_id,
    )

    if not matches:
        raise ConversationGateError(f"Conversation not found: {conversation_id}")

    row = matches[0]
    vcprint(
        f"[ConversationGate] Verified conversation: {conversation_id}...",
        color="green",
    )
    return (
        row
        if isinstance(row, dict)
        else {"id": str(getattr(row, "id", conversation_id))}
    )


async def update_conversation_status(
    conversation_id: str,
    status: str,
) -> None:
    """Update the status field on an existing cx_conversation row.

    Fire-and-forget safe — logs errors but never raises.
    In client mode, this is a no-op.
    """
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        return

    if not _is_valid_uuid(conversation_id):
        return
    try:
        await cxm.conversation.update_cx_conversation(
            conversation_id,
            status=status,
        )
    except Exception as exc:
        vcprint(
            f"[ConversationGate] Failed to update status to {status!r}: {exc}",
            color="yellow",
        )


# =========================================================================
# User request lifecycle
# =========================================================================


async def create_pending_user_request(
    request_id: str,
    conversation_id: str,
    user_id: str,
) -> None:
    """INSERT a cx_user_request row with status='pending'.

    Called at the start of ``execute_until_complete()`` so the row exists
    before any tool calls run.  The ``request_id`` from ``AIMatrixRequest``
    becomes the PK so downstream systems can reference it immediately.

    Fire-and-forget safe — logs errors but never raises.

    In client mode (desktop app / PostgREST + RLS), this is a no-op.
    """
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        from matrx_ai.client_mode import get_conversation_handler
        try:
            await get_conversation_handler().create_pending_user_request(
                request_id=request_id,
                conversation_id=conversation_id,
                user_id=user_id,
            )
        except Exception as exc:
            vcprint(
                f"[ConversationGate] ConversationHandler.create_pending_user_request failed: {exc}",
                color="yellow",
            )
        return

    if not _is_valid_uuid(request_id):
        vcprint(
            f"[ConversationGate] Cannot create pending user_request: "
            f"request_id is not a valid UUID: {request_id!r}",
            color="yellow",
        )
        return

    safe_user_id = _require_valid_user_id(user_id, "create_pending_user_request")
    safe_conversation_id = conversation_id if _is_valid_uuid(conversation_id) else None

    create_kwargs: dict[str, Any] = {
        "id": request_id,
        "user_id": safe_user_id,
        "status": "pending",
        "iterations": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cached_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0,
        "total_tool_calls": 0,
        "metadata": {},
    }

    if safe_conversation_id:
        create_kwargs["conversation_id"] = safe_conversation_id

    try:
        await cxm.user_request.create_cx_user_request(**create_kwargs)
        vcprint(
            f"[ConversationGate] Created pending user_request: {request_id}...",
            color="green",
        )
    except Exception as exc:
        vcprint(
            f"[ConversationGate] Failed to create pending user_request: {exc}",
            color="yellow",
        )


async def ensure_user_request_exists(
    request_id: str,
    conversation_id: str,
    user_id: str,
) -> None:
    """Ensure a cx_user_request row exists for the given request_id.

    Idempotent: creates with status='pending' if missing, no-op if already
    present.  Analogous to ``ensure_conversation_exists()``.

    The boundary layer (API route, batch script, workflow trigger) calls
    this ONCE per user action before handing off to the AI engine.  All N
    AI API calls that result from that user action share this single row,
    which persistence updates with aggregate totals on completion.

    Fire-and-forget safe — logs errors but never raises.
    In client mode, this is a no-op.
    """
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        return

    if not _is_valid_uuid(request_id):
        vcprint(
            f"[ConversationGate] Cannot ensure user_request: "
            f"request_id is not a valid UUID: {request_id!r}",
            color="yellow",
        )
        return

    safe_user_id = _require_valid_user_id(user_id, "ensure_user_request_exists")
    safe_conversation_id = conversation_id if _is_valid_uuid(conversation_id) else None

    existing = await cxm.user_request.filter_cx_user_requests(id=request_id)
    if existing:
        return

    create_kwargs: dict[str, Any] = {
        "id": request_id,
        "user_id": safe_user_id,
        "status": "pending",
        "iterations": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_cached_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0,
        "total_tool_calls": 0,
        "metadata": {},
    }

    if safe_conversation_id:
        create_kwargs["conversation_id"] = safe_conversation_id

    try:
        await cxm.user_request.create_cx_user_request(**create_kwargs)
        vcprint(
            f"[ConversationGate] Ensured user_request: {request_id}...",
            color="green",
        )
    except Exception as exc:
        recheck = await cxm.user_request.filter_cx_user_requests(id=request_id)
        if recheck:
            return
        vcprint(
            f"[ConversationGate] Failed to ensure user_request: {exc}",
            color="yellow",
        )


async def update_user_request_status(
    request_id: str,
    status: str,
    error: str | None = None,
) -> None:
    """Update the status (and optionally error) on an existing cx_user_request.

    Fire-and-forget safe — logs errors but never raises.
    In client mode, this is a no-op.
    """
    from matrx_ai.db import is_client_mode
    if is_client_mode():
        return

    if not _is_valid_uuid(request_id):
        return

    update_kwargs: dict[str, Any] = {"status": status}
    if error is not None:
        update_kwargs["error"] = error

    try:
        await cxm.user_request.update_cx_user_request(
            request_id,
            **update_kwargs,
        )
    except Exception as exc:
        vcprint(
            f"[ConversationGate] Failed to update user_request status to {status!r}: {exc}",
            color="yellow",
        )


# =========================================================================
# Concurrent launch helper
# =========================================================================


def launch_conversation_gate(
    conversation_id: str,
    is_new_conversation: bool,
    execution_task: asyncio.Task[Any],
) -> asyncio.Task[Any] | None:
    """Wire up the conversation gate for new conversations.

    Reads ``user_id`` and ``emitter`` from the current ``ExecutionContext``.

    For ``is_new_conversation=True``:
        Fires the INSERT as a concurrent ``asyncio.Task``.  When that task
        finishes, a done-callback inspects the result:
        - On success -> no-op, execution continues.
        - On failure -> cancels ``execution_task`` and pushes a fatal error
          through the emitter.

    For ``is_new_conversation=False``:
        Returns ``None``.  The caller is expected to have already awaited
        ``verify_existing_conversation()`` before starting execution.

    Returns the gate task (or None) so the caller can track it if needed.
    """
    if not is_new_conversation:
        return None

    from matrx_ai.context.app_context import get_app_context

    exec_ctx = get_app_context()
    user_id = exec_ctx.user_id
    emitter = exec_ctx.emitter

    async def _gate_task() -> None:
        await create_new_conversation(
            conversation_id=conversation_id,
            user_id=user_id,
        )

    gate_task = asyncio.create_task(_gate_task())

    def _on_gate_done(t: asyncio.Task[Any]) -> None:
        exc = t.exception()
        if exc is None:
            return

        vcprint(
            f"[ConversationGate] INSERT failed — cancelling execution: {exc}",
            color="red",
        )

        execution_task.cancel()

        async def _send_fatal() -> None:
            try:
                await emitter.fatal_error(
                    error_type="conversation_gate_error",
                    message=str(exc),
                    user_message="Failed to initialize conversation. Please try again.",
                    details=traceback.format_exception(
                        type(exc), exc, exc.__traceback__
                    ),
                )
            except Exception:
                pass

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(_send_fatal())
        except RuntimeError:
            pass

    gate_task.add_done_callback(_on_gate_done)
    return gate_task
