"""Tests for AppContext and ContextVar storage."""

from __future__ import annotations

import pytest

from matrx_service.context.app_context import (
    AppContext,
    clear_app_context,
    get_app_context,
    set_app_context,
    try_get_app_context,
)
from matrx_service.context.console_emitter import ConsoleEmitter


@pytest.fixture
def emitter() -> ConsoleEmitter:
    return ConsoleEmitter(label="test", accumulate=True)


@pytest.fixture
def ctx(emitter: ConsoleEmitter) -> AppContext:
    return AppContext(emitter=emitter, user_id="test-user", is_authenticated=True)


def test_app_context_defaults(emitter: ConsoleEmitter) -> None:
    ctx = AppContext(emitter=emitter)
    assert ctx.user_id == ""
    assert ctx.auth_type == "anonymous"
    assert not ctx.is_authenticated
    assert not ctx.is_admin
    assert ctx.conversation_id == ""


def test_app_context_extend(ctx: AppContext) -> None:
    ctx.extend(conversation_id="conv-123", debug=True)
    assert ctx.conversation_id == "conv-123"
    assert ctx.debug is True


def test_app_context_extend_unknown_key_raises(ctx: AppContext) -> None:
    with pytest.raises(AttributeError, match="has no field"):
        ctx.extend(nonexistent_field="value")


def test_fork_for_child_agent(ctx: AppContext) -> None:
    ctx.extend(conversation_id="parent-conv", request_id="req-1")
    child = ctx.fork_for_child_agent("child-conv")

    assert child.conversation_id == "child-conv"
    assert child.parent_conversation_id == "parent-conv"
    assert child.parent_request_id == "req-1"
    assert child.is_internal_agent is True
    assert child.request_id == ""
    # Identity is preserved
    assert child.user_id == ctx.user_id
    assert child.is_authenticated == ctx.is_authenticated


def test_context_var_set_and_get(ctx: AppContext) -> None:
    token = set_app_context(ctx)
    try:
        retrieved = get_app_context()
        assert retrieved is ctx
    finally:
        clear_app_context(token)


def test_get_app_context_raises_when_unset() -> None:
    # Ensure no context is set (run in isolation)
    assert try_get_app_context() is None
    with pytest.raises(RuntimeError, match="No AppContext"):
        get_app_context()


def test_try_get_app_context_returns_none_when_unset() -> None:
    assert try_get_app_context() is None


def test_context_var_cleared_after_reset(ctx: AppContext) -> None:
    token = set_app_context(ctx)
    clear_app_context(token)
    assert try_get_app_context() is None
