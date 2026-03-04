"""ai.tools — Unified tool execution system.

Public API:
    ToolExecutor              — The single entry point for all tool executions
    ToolRegistryV2            — Singleton registry (DB + code resolution)
    ToolDefinition            — Pydantic model describing a tool
    ToolContext               — Everything a tool needs about its execution environment
    ToolResult                — Structured result from any tool execution
    ToolError                 — Rich error with traceback + suggested action
    ToolType                  — LOCAL | EXTERNAL_MCP | AGENT | EXTERNAL_HANDLER
    CxToolCallRecord          — Pydantic model for the cx_tool_call DB row
    GuardrailEngine           — Centralized safety checks
    ToolStreamManager         — Streaming updates during tool execution
    ToolLifecycleManager      — Resource cleanup
    ToolExecutionLogger       — DB logging (two-phase: INSERT on start, UPDATE on finish)

External tool integration (for apps consuming matrx-ai as a package):
    ExternalToolAdapter       — Base class: subclass, decorate with @external_tool, call register()
    external_tool             — Decorator: marks a method as the handler for a named tool
    ExternalHandlerRegistry   — Underlying singleton registry (advanced use / testing)
    ExternalToolHandler       — Type alias for the handler callable signature
    register_external_tool_handler  — Register a standalone function for one tool
    register_external_app_handler   — Register a catch-all for all tools from a source_app

See docs/external-tool-integration.md for the full integration guide.
"""

from .agent_tool import execute_agent_tool, register_agent_as_tool
from .executor import ToolExecutor
from .external_handlers import (
    ExternalHandlerRegistry,
    ExternalToolAdapter,
    ExternalToolHandler,
    external_tool,
    register_external_app_handler,
    register_external_tool_handler,
)
from .external_mcp import ExternalMCPClient
from .guardrails import GuardrailEngine
from .lifecycle import ToolLifecycleManager
from .logger import ToolExecutionLogger
from .models import (
    CxToolCallRecord,
    CxToolCallStatus,
    GuardrailResult,
    ToolContext,
    ToolDefinition,
    ToolError,
    ToolResult,
    ToolType,
)
from .registry import ToolRegistryV2
from .streaming import ToolStreamEvent, ToolStreamManager

__all__ = [
    "ToolExecutor",
    "ToolRegistryV2",
    "ToolDefinition",
    "ToolContext",
    "ToolResult",
    "ToolError",
    "ToolType",
    "CxToolCallRecord",
    "CxToolCallStatus",
    "GuardrailResult",
    "GuardrailEngine",
    "ToolStreamEvent",
    "ToolStreamManager",
    "ToolExecutionLogger",
    "ToolLifecycleManager",
    "ExternalMCPClient",
    "ExternalHandlerRegistry",
    "ExternalToolAdapter",
    "ExternalToolHandler",
    "external_tool",
    "register_external_tool_handler",
    "register_external_app_handler",
    "execute_agent_tool",
    "register_agent_as_tool",
]
