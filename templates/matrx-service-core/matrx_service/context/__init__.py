"""App Context & Emitter.

- AppContext: ContextVar-based request context (set by AuthMiddleware)
- Emitter: Runtime-checkable Protocol for streaming
- EventType: Event types and payload models
- ConsoleEmitter: Dev/test emitter
- StreamEmitter: Production NDJSON emitter

Usage:
    from matrx_service.context.app_context import AppContext, get_app_context
    from matrx_service.context.emitter_protocol import Emitter
    from matrx_service.context.events import EventType, build_event
"""

from matrx_service.context.app_context import (
    AppContext,
    clear_app_context,
    context_dep,
    get_app_context,
    set_app_context,
    try_get_app_context,
)
from matrx_service.context.emitter_protocol import Emitter
from matrx_service.context.events import EventType

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
