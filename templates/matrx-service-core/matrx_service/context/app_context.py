from __future__ import annotations

import dataclasses
from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal

from fastapi import Request

if TYPE_CHECKING:
    from matrx_service.context.emitter_protocol import Emitter


@dataclass
class AppContext:
    """Request-scoped context carried through the entire call stack via ContextVar.

    Set by AuthMiddleware on every inbound request. Readable anywhere via
    get_app_context(). Writable only via extend() — never mutate fields directly
    outside middleware or the router layer.

    Auth fields
    -----------
    auth_type       : "token" (JWT or admin token) | "fingerprint" | "anonymous"
    is_authenticated: True only for valid JWT or admin token
    is_admin        : True only for admin token

    Identity fields
    ---------------
    All services share the same identity model so service-to-service calls
    propagate a consistent context regardless of which service originates the
    request.
    """

    emitter: Emitter

    # --- Auth ---
    user_id: str = ""
    email: str | None = None
    auth_type: Literal["token", "fingerprint", "anonymous"] = "anonymous"
    is_authenticated: bool = False
    is_admin: bool = False

    # --- Request metadata ---
    fingerprint_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    token: str | None = None

    request_id: str = ""

    # --- Organizational scope ---
    organization_id: str | None = None
    project_id: str | None = None

    # --- Extensible metadata ---
    api_keys: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    debug: bool = False

    # --- Conversation / AI context ---
    # Included in the base because all Matrx services participate in
    # the same conversation ecosystem and talk to each other.
    conversation_id: str = ""
    parent_conversation_id: str | None = None
    parent_request_id: str | None = None
    is_internal_agent: bool = False

    # --- Per-request AI overrides ---
    initial_variables: dict[str, Any] = field(default_factory=dict)
    initial_overrides: dict[str, Any] = field(default_factory=dict)

    def extend(self, **kwargs: Any) -> AppContext:
        """Mutate fields in-place. Raises AttributeError for unknown keys.

        Use in router handlers to set route-specific fields (e.g. conversation_id,
        debug) after the middleware has populated auth fields.
        """
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
        """Create a derived context for a child agent call.

        Preserves user identity and auth, sets parent pointers, and marks
        the fork as an internal agent so downstream services can distinguish
        user-originated requests from service-to-service calls.
        """
        return dataclasses.replace(
            self,
            conversation_id=new_conversation_id,
            parent_conversation_id=self.conversation_id or None,
            parent_request_id=self.request_id or None,
            is_internal_agent=True,
            request_id="",
        )


# ---------------------------------------------------------------------------
# ContextVar storage — one slot per async task / request
# ---------------------------------------------------------------------------

_app_context: ContextVar[AppContext | None] = ContextVar("app_context", default=None)


def set_app_context(ctx: AppContext) -> Token:
    return _app_context.set(ctx)


def get_app_context() -> AppContext:
    ctx = _app_context.get(None)
    if ctx is None:
        raise RuntimeError(
            "No AppContext is set. Ensure AuthMiddleware is registered and running "
            "before this code path."
        )
    return ctx


def try_get_app_context() -> AppContext | None:
    return _app_context.get(None)


def clear_app_context(token: Token) -> None:
    _app_context.reset(token)


def context_dep(request: Request) -> AppContext:
    """FastAPI dependency — resolves AppContext from request.state.

    Use as:  ctx: AppContext = Depends(context_dep)

    Raises HTTP 500 if AuthMiddleware is not registered (configuration error,
    not a client error).
    """
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
