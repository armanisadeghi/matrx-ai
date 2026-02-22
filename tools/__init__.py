"""tools — Unified tool execution system.

Public API:
    ToolExecutor        — The single entry point for all tool executions
    ToolRegistryV2      — Singleton registry (DB + code resolution)
    ToolDefinition      — Pydantic model describing a tool
    ToolContext          — Everything a tool needs about its execution environment
    ToolResult           — Structured result from any tool execution
    ToolError            — Rich error with traceback + suggested action
    ToolType             — LOCAL | EXTERNAL_MCP | AGENT
    CxToolCallRecord     — Pydantic model for the cx_tool_call DB row
    GuardrailEngine      — Centralized safety checks
    ToolStreamManager    — Streaming updates during tool execution
    ToolLifecycleManager — Resource cleanup
    ToolExecutionLogger  — DB logging (two-phase: INSERT on start, UPDATE on finish)
"""

from tools.models import (
    CxToolCallRecord,
    CxToolCallStatus,
    GuardrailResult,
    ToolContext,
    ToolDefinition,
    ToolError,
    ToolResult,
    ToolType,
)
from tools.registry import ToolRegistryV2
from tools.executor import ToolExecutor
from tools.guardrails import GuardrailEngine
from tools.streaming import ToolStreamEvent, ToolStreamManager
from tools.logger import ToolExecutionLogger
from tools.lifecycle import ToolLifecycleManager
from tools.external_mcp import ExternalMCPClient
from tools.agent_tool import execute_agent_tool, register_agent_as_tool

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
    "execute_agent_tool",
    "register_agent_as_tool",
]
