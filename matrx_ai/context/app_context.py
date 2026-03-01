from __future__ import annotations

import dataclasses
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from fastapi import Request

if TYPE_CHECKING:
    from matrx_ai.context.emitter_protocol import Emitter


@dataclass
class AppContext:
    emitter: Emitter

    user_id: str = ""
    email: str | None = None
    auth_type: Literal["token", "fingerprint", "anonymous"] = "anonymous"
    is_authenticated: bool = False
    is_admin: bool = False

    fingerprint_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    token: str | None = None

    request_id: str = ""

    organization_id: str | None = None
    project_id: str | None = None

    api_keys: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    debug: bool = False

    conversation_id: str = ""
    parent_conversation_id: str | None = None
    parent_request_id: str | None = None
    is_internal_agent: bool = False

    initial_variables: dict[str, Any] = field(default_factory=dict)
    initial_overrides: dict[str, Any] = field(default_factory=dict)

    def extend(self, **kwargs: Any) -> AppContext:
        valid = {f.name for f in dataclasses.fields(self)}
        for key, value in kwargs.items():
            if key not in valid:
                raise AttributeError(
                    f"AppContext has no field '{key}'. "
                    f"Add it to the dataclass before using extend()."
                )
            setattr(self, key, value)
        return self

    def fork_for_child_agent(self, new_conversation_id: str) -> AppContext:
        return dataclasses.replace(
            self,
            conversation_id=new_conversation_id,
            parent_conversation_id=self.conversation_id or None,
            parent_request_id=self.request_id or None,
            is_internal_agent=True,
            request_id="",
        )


_app_context: ContextVar[AppContext | None] = ContextVar("app_context", default=None)


def set_app_context(ctx: AppContext) -> Token:
    return _app_context.set(ctx)


def get_app_context() -> AppContext:
    ctx = _app_context.get(None)
    if ctx is None:
        raise RuntimeError(
            "No AppContext is set. Ensure middleware is registered and running "
            "before this code path."
        )
    return ctx


def try_get_app_context() -> AppContext | None:
    return _app_context.get(None)


def clear_app_context(token: Token) -> None:
    _app_context.reset(token)


def context_dep(request: Request) -> AppContext:
    from fastapi import HTTPException, status

    ctx = getattr(request.state, "context", None)
    if ctx is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "missing_context",
                "message": "AppContext not initialized. AuthMiddleware is misconfigured.",
            },
        )
    return ctx
