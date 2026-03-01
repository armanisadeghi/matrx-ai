"""App Context & Emitter Protocol.

- AppContext: ContextVar-based request context
- Emitter: Runtime-checkable Protocol for streaming
- EventType: Event types and payload models
- ConsoleEmitter: Dev/test emitter

Usage:
    from matrx_ai.context.app_context import AppContext, get_app_context, set_app_context
    from matrx_ai.context.emitter_protocol import Emitter
    from matrx_ai.context.events import EventType
"""

from matrx_ai.context.app_context import (
    AppContext,
    clear_app_context,
    context_dep,
    get_app_context,
    set_app_context,
    try_get_app_context,
)
from matrx_ai.context.emitter_protocol import Emitter
from matrx_ai.context.events import EventType

__all__ = [
    "AppContext",
    "get_app_context",
    "set_app_context",
    "try_get_app_context",
    "clear_app_context",
    "context_dep",
    "Emitter",
    "EventType",
]
