"""External tool handler registry for matrx-ai.

When matrx-ai is consumed as a package by an external application (e.g. Matrx Local),
some tools in the database have implementations that live in the host application, not
in this codebase. These tools carry ``source_app != "matrx_ai"`` in the database.

The ``ExternalHandlerRegistry`` allows host applications to register async callables
that matrx-ai will dispatch to when the AI model calls one of those tools. The result
flows back through the same guardrails, streaming, persistence, and model-feedback
pipeline as any native tool -- the model cannot tell the difference.

----

Usage in the host application (e.g. Matrx Local)
-------------------------------------------------

Option A -- Register a handler for a single specific tool::

    from matrx_ai.tools import register_external_tool_handler, ToolContext, ToolResult

    async def handle_screenshot(args: dict, ctx: ToolContext) -> ToolResult:
        image_data = await take_local_screenshot(args.get("region"))
        return ToolResult(
            success=True,
            output=image_data,
            tool_name=ctx.tool_name,
            call_id=ctx.call_id,
        )

    register_external_tool_handler("screenshot", handle_screenshot)


Option B -- Register a single dispatcher for every tool owned by a source_app::

    from matrx_ai.tools import register_external_app_handler, ToolContext, ToolResult

    async def matrx_local_dispatcher(args: dict, ctx: ToolContext) -> ToolResult:
        # ctx.tool_name identifies which tool was called.
        result_data = await local_tool_router(ctx.tool_name, args)
        return ToolResult(
            success=True,
            output=result_data,
            tool_name=ctx.tool_name,
            call_id=ctx.call_id,
        )

    register_external_app_handler("matrx_local", matrx_local_dispatcher)


Resolution order (per execution)
---------------------------------
1. Exact tool-name match  →  ``register_external_tool_handler``
2. App-level fallback     →  ``register_external_app_handler`` (keyed on ``source_app``)
3. No handler found       →  structured error returned to the model (not a crash)

----

Call the registration functions *before* the first AI request that could trigger
the tool.  The registry is a process-level singleton so registrations persist for
the lifetime of the process.
"""

from __future__ import annotations

import traceback
from collections.abc import Awaitable, Callable
from typing import Any

from matrx_utils import vcprint

from matrx_ai.tools.models import ToolContext, ToolError, ToolResult

ExternalToolHandler = Callable[[dict[str, Any], ToolContext], Awaitable[ToolResult]]


class ExternalHandlerRegistry:
    """Process-level singleton that maps tool names / source-app names to async callables.

    Thread-safety: Registration is expected to happen at startup (single-threaded);
    reads during request handling are concurrent but safe because dicts in CPython
    have GIL-protected reads.  For truly concurrent registration, callers should
    synchronise externally.
    """

    _instance: ExternalHandlerRegistry | None = None

    def __init__(self) -> None:
        # tool_name → handler (highest priority)
        self._tool_handlers: dict[str, ExternalToolHandler] = {}
        # source_app → catch-all handler for every tool from that app
        self._app_handlers: dict[str, ExternalToolHandler] = {}

    @classmethod
    def get_instance(cls) -> ExternalHandlerRegistry:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, tool_name: str, handler: ExternalToolHandler) -> None:
        """Register a handler for one specific tool by name.

        Takes priority over any app-level handler for the same tool.
        Calling this again with the same ``tool_name`` replaces the previous handler.
        """
        if not callable(handler):
            raise TypeError(f"Handler for tool '{tool_name}' must be callable, got {type(handler)}")
        self._tool_handlers[tool_name] = handler
        vcprint(
            f"[ExternalHandlerRegistry] Registered handler for tool: {tool_name}",
            color="cyan",
        )

    def register_app_handler(self, source_app: str, handler: ExternalToolHandler) -> None:
        """Register a catch-all handler for every tool owned by ``source_app``.

        This is the simplest integration point: one async function receives every
        tool call from the given app, with ``ctx.tool_name`` identifying which
        specific tool was invoked.

        Calling this again with the same ``source_app`` replaces the previous handler.
        """
        if not callable(handler):
            raise TypeError(
                f"App handler for source_app '{source_app}' must be callable, got {type(handler)}"
            )
        self._app_handlers[source_app] = handler
        vcprint(
            f"[ExternalHandlerRegistry] Registered app-level handler for source_app: {source_app}",
            color="cyan",
        )

    def unregister(self, tool_name: str) -> bool:
        """Remove the per-tool handler for ``tool_name``. Returns True if one existed."""
        existed = tool_name in self._tool_handlers
        self._tool_handlers.pop(tool_name, None)
        return existed

    def unregister_app_handler(self, source_app: str) -> bool:
        """Remove the app-level handler for ``source_app``. Returns True if one existed."""
        existed = source_app in self._app_handlers
        self._app_handlers.pop(source_app, None)
        return existed

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------

    def get_handler(
        self, tool_name: str, source_app: str | None
    ) -> ExternalToolHandler | None:
        """Resolve the best handler for a tool call.

        Resolution order:
        1. Exact tool-name match (``register`` / ``register_external_tool_handler``)
        2. App-level fallback (``register_app_handler`` / ``register_external_app_handler``)
        3. ``None`` — caller should surface a structured error to the model
        """
        if tool_name in self._tool_handlers:
            return self._tool_handlers[tool_name]
        if source_app and source_app in self._app_handlers:
            return self._app_handlers[source_app]
        return None

    def has_handler(self, tool_name: str, source_app: str | None) -> bool:
        """Return True if any handler would be found for this tool."""
        return self.get_handler(tool_name, source_app) is not None

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    @property
    def registered_tools(self) -> list[str]:
        return list(self._tool_handlers.keys())

    @property
    def registered_apps(self) -> list[str]:
        return list(self._app_handlers.keys())

    def __repr__(self) -> str:
        return (
            f"ExternalHandlerRegistry("
            f"tools={self.registered_tools}, "
            f"apps={self.registered_apps})"
        )


# ------------------------------------------------------------------
# Module-level helpers — the primary public API for host applications
# ------------------------------------------------------------------

def register_external_tool_handler(
    tool_name: str, handler: ExternalToolHandler
) -> None:
    """Register an async handler for a single named tool.

    The handler signature must be::

        async def my_handler(args: dict, ctx: ToolContext) -> ToolResult: ...

    Args:
        tool_name: Exact name of the tool as stored in the ``tools`` database table.
        handler:   Async callable that executes the tool and returns a ``ToolResult``.

    This registration takes priority over any app-level handler registered via
    ``register_external_app_handler``.
    """
    ExternalHandlerRegistry.get_instance().register(tool_name, handler)


def register_external_app_handler(
    source_app: str, handler: ExternalToolHandler
) -> None:
    """Register a catch-all async handler for all tools owned by ``source_app``.

    The handler receives every tool call for tools whose ``source_app`` column in
    the database matches the given string.  Use ``ctx.tool_name`` inside the handler
    to route to the correct local implementation.

    The handler signature must be::

        async def my_dispatcher(args: dict, ctx: ToolContext) -> ToolResult: ...

    Args:
        source_app: Value of the ``source_app`` DB column for the tools this handles
                    (e.g. ``"matrx_local"``).
        handler:    Async callable that dispatches to the appropriate local tool.
    """
    ExternalHandlerRegistry.get_instance().register_app_handler(source_app, handler)


async def invoke_external_handler(
    tool_name: str,
    source_app: str | None,
    args: dict[str, Any],
    ctx: ToolContext,
) -> ToolResult:
    """Invoke the registered handler for a tool, returning a normalised ``ToolResult``.

    This is called internally by ``ToolExecutor._execute_external_handler``.
    It handles:
    - handler lookup (with graceful error if none registered)
    - invocation with timeout guard inherited from the executor
    - normalisation of raw return values into ``ToolResult``
    - exception capture → structured ``ToolResult`` with error details
    """
    import time

    registry = ExternalHandlerRegistry.get_instance()
    handler = registry.get_handler(tool_name, source_app)

    if handler is None:
        app_label = f"'{source_app}'" if source_app else "unknown"
        vcprint(
            {
                "tool_name": tool_name,
                "source_app": source_app,
                "registered_tools": registry.registered_tools,
                "registered_apps": registry.registered_apps,
            },
            f"[ExternalHandlerRegistry] No handler registered for tool '{tool_name}' (source_app={app_label})",
            color="red",
        )
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="no_handler",
                message=(
                    f"Tool '{tool_name}' (source_app={app_label}) requires an external handler "
                    f"that has not been registered. "
                    f"Call register_external_tool_handler('{tool_name}', handler) or "
                    f"register_external_app_handler({app_label}, handler) at startup."
                ),
                is_retryable=False,
                suggested_action=(
                    "This tool cannot be executed in the current environment. "
                    "Inform the user and suggest an alternative approach."
                ),
            ),
            started_at=time.time(),
            completed_at=time.time(),
            tool_name=tool_name,
            call_id=ctx.call_id,
        )

    started_at = time.time()
    try:
        raw_result = await handler(args, ctx)
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="external_handler_error",
                message=str(exc),
                traceback=traceback.format_exc(),
                is_retryable=False,
                suggested_action="The external tool handler raised an unexpected exception. Check the host application logs.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_name,
            call_id=ctx.call_id,
        )

    # Normalise: if the handler already returned a ToolResult, pass it through.
    if isinstance(raw_result, ToolResult):
        raw_result.started_at = raw_result.started_at or started_at
        raw_result.completed_at = raw_result.completed_at or time.time()
        raw_result.tool_name = raw_result.tool_name or tool_name
        raw_result.call_id = raw_result.call_id or ctx.call_id
        return raw_result

    # Legacy / simple return: wrap any non-ToolResult value.
    if isinstance(raw_result, dict) and raw_result.get("status") == "error":
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution",
                message=str(raw_result.get("error", raw_result.get("result", "Unknown error"))),
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name=tool_name,
            call_id=ctx.call_id,
        )

    return ToolResult(
        success=True,
        output=raw_result,
        started_at=started_at,
        completed_at=time.time(),
        tool_name=tool_name,
        call_id=ctx.call_id,
    )
