from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matrx_ai.orchestrator.executor import execute_ai_request, execute_until_complete
    from matrx_ai.orchestrator.requests import AIMatrixRequest, CompletedRequest
    from matrx_ai.orchestrator.tracking import TimingUsage, ToolCallUsage

__all__ = [
    "AIMatrixRequest",
    "CompletedRequest",
    "TimingUsage",
    "ToolCallUsage",
    "execute_ai_request",
    "execute_until_complete",
]

_module_map: dict[str, str] = {
    "execute_ai_request": "matrx_ai.orchestrator.executor",
    "execute_until_complete": "matrx_ai.orchestrator.executor",
    "AIMatrixRequest": "matrx_ai.orchestrator.requests",
    "CompletedRequest": "matrx_ai.orchestrator.requests",
    "TimingUsage": "matrx_ai.orchestrator.tracking",
    "ToolCallUsage": "matrx_ai.orchestrator.tracking",
}


def __getattr__(name: str) -> object:
    if name in _module_map:
        import importlib

        mod = importlib.import_module(_module_map[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
