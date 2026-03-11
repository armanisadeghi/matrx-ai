from __future__ import annotations

import json
import re
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from matrx_ai.config import TokenUsage
from matrx_ai.context.emitter_protocol import Emitter


class ToolType(StrEnum):
    LOCAL = "local"
    EXTERNAL_MCP = "external"
    AGENT = "agent"
    EXTERNAL_HANDLER = "external_handler"


class ToolError(BaseModel):
    error_type: str
    message: str
    traceback: str | None = None
    is_retryable: bool = False
    suggested_action: str | None = None

    def to_agent_message(self) -> str:
        parts = [f"TOOL ERROR [{self.error_type}]: {self.message}"]
        if self.suggested_action:
            parts.append(f"Suggested action: {self.suggested_action}")
        if self.traceback:
            parts.append(f"Technical details:\n{self.traceback}")
        return "\n".join(parts)


class ToolResult(BaseModel):
    success: bool
    output: Any = None
    error: ToolError | None = None

    usage: dict[str, Any] | None = None
    child_usages: list[TokenUsage] = Field(default_factory=list)

    started_at: float = 0.0
    completed_at: float = 0.0
    duration_ms: int = 0

    tool_name: str = ""
    call_id: str = ""
    retry_count: int = 0

    should_persist_output: bool = False
    persist_key: str | None = None

    model_config = {"arbitrary_types_allowed": True}

    def compute_duration(self) -> None:
        if self.started_at and self.completed_at:
            self.duration_ms = int((self.completed_at - self.started_at) * 1000)

    def to_tool_result_content(self) -> dict[str, Any]:
        """Return a dict that can construct an existing ToolResultContent dataclass.

        Keys match the ToolResultContent.__init__ signature defined in
        ai.config.tools_config so the caller can do:
            ToolResultContent(**result.to_tool_result_content())
        """
        if self.success:
            content = self.output
            if isinstance(content, dict):
                content = json.dumps(content)
            elif not isinstance(content, str):
                content = str(content) if content is not None else ""
        else:
            content = self.error.to_agent_message() if self.error else "Unknown error"

        return {
            "tool_use_id": self.call_id,
            "call_id": self.call_id,
            "name": self.tool_name,
            "content": content,
            "is_error": not self.success,
        }


class GuardrailResult(BaseModel):
    blocked: bool = False
    reason: str | None = None
    error_type: str = "guardrail"
    suggested_action: str | None = None

    def to_tool_result_content(
        self, call_id: str = "", tool_name: str = ""
    ) -> dict[str, Any]:
        error_msg = (
            f"TOOL BLOCKED [{self.error_type}]: {self.reason or 'Guardrail triggered'}"
        )
        if self.suggested_action:
            error_msg += f"\nSuggested action: {self.suggested_action}"
        return {
            "tool_use_id": call_id,
            "call_id": call_id,
            "name": tool_name,
            "content": error_msg,
            "is_error": True,
        }


class ToolContext(BaseModel):
    call_id: str
    tool_name: str = ""
    iteration: int = 0
    parent_agent_name: str | None = None
    user_role: str = "user"
    recursion_depth: int = 0
    cost_budget_remaining: float | None = None
    calls_remaining_this_conversation: int | None = None

    model_config = {"arbitrary_types_allowed": True}

    @property
    def user_id(self) -> str:
        from matrx_ai.context.app_context import get_app_context

        return get_app_context().user_id

    @property
    def conversation_id(self) -> str:
        from matrx_ai.context.app_context import get_app_context

        return get_app_context().conversation_id

    @property
    def request_id(self) -> str:
        from matrx_ai.context.app_context import get_app_context

        return get_app_context().request_id

    @property
    def emitter(self) -> Emitter | None:
        from matrx_ai.context.app_context import try_get_app_context

        ctx = try_get_app_context()
        return ctx.emitter if ctx else None

    @property
    def api_keys(self) -> dict[str, str]:
        from matrx_ai.context.app_context import try_get_app_context

        ctx = try_get_app_context()
        return ctx.api_keys if ctx else {}

    @property
    def project_id(self) -> str | None:
        from matrx_ai.context.app_context import try_get_app_context

        ctx = try_get_app_context()
        return ctx.project_id if ctx else None

    @property
    def organization_id(self) -> str | None:
        from matrx_ai.context.app_context import try_get_app_context

        ctx = try_get_app_context()
        return ctx.organization_id if ctx else None


class ToolDefinition(BaseModel):
    name: str = Field(description="Unique tool identifier")
    description: str = ""
    parameters: dict[str, Any] = Field(
        default_factory=dict,
        description="Internal parameter schema (key→property dict). Converted to JSON Schema by format methods.",
    )
    output_schema: dict[str, Any] | None = None
    annotations: list[dict[str, Any]] = Field(default_factory=list)

    tool_type: ToolType = ToolType.LOCAL
    function_path: str = Field(
        default="", description="Dotted import path or 'agent:<prompt_id>'"
    )
    source_app: str | None = Field(
        default=None,
        description="The application that owns this tool's implementation (e.g. 'ai', 'matrx_local'). "
        "Tools with source_app != 'ai' require an external handler registered at runtime.",
    )

    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    icon: str | None = None
    is_active: bool = True
    version: str = "1.0.0"

    prompt_id: str | None = None
    mcp_server_url: str | None = None
    mcp_server_auth: dict[str, Any] | None = None

    max_calls_per_conversation: int | None = None
    max_calls_per_minute: int | None = None
    cost_cap_per_call: float | None = None
    timeout_seconds: float = 120.0
    max_recursion_depth: int = 3

    on_call_message_template: str | None = None

    _callable: Callable[..., Awaitable[Any]] | None = PrivateAttr(default=None)

    model_config = {"arbitrary_types_allowed": True}

    # ------------------------------------------------------------------
    # JSON Schema helpers (ported from mcp_server/core/definitions.py)
    # ------------------------------------------------------------------

    def _build_json_schema(
        self, *, strip_openai_unsupported: bool = False
    ) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []

        for key, param in self.parameters.items():
            if isinstance(param, str):
                param = {"type": param}
            raw_type = param.get("type", "string")
            if isinstance(raw_type, list):
                non_null = [t for t in raw_type if t != "null"]
                raw_type = non_null[0] if non_null else "string"
            prop: dict[str, Any] = {
                "type": raw_type,
                "description": param.get("description", ""),
            }
            if raw_type == "array" and "items" in param:
                prop["items"] = self._process_nested(
                    param["items"], strip_openai_unsupported
                )
            for f in (
                "minItems",
                "maxItems",
                "uniqueItems",
                "minimum",
                "maximum",
                "pattern",
            ):
                if f in param and not strip_openai_unsupported:
                    prop[f] = param[f]
            if "default" in param:
                prop["default"] = param["default"]
            if "enum" in param:
                prop["enum"] = param["enum"]
            if prop["type"] == "object" and "properties" in param:
                prop["properties"] = {
                    sk: self._process_nested(sv, strip_openai_unsupported)
                    for sk, sv in param["properties"].items()
                }
                prop["required"] = param.get("required", [])
                prop["additionalProperties"] = False

            properties[key] = prop
            if param.get("required", False):
                required.append(key)

        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }

    @staticmethod
    def _process_nested(
        schema: dict[str, Any] | str, strip_unsupported: bool
    ) -> dict[str, Any]:
        if isinstance(schema, str):
            return {"type": schema}
        processed = schema.copy()
        if strip_unsupported:
            for f in (
                "minItems",
                "maxItems",
                "uniqueItems",
                "minimum",
                "maximum",
                "pattern",
            ):
                processed.pop(f, None)
        if processed.get("type") == "object" and "properties" in processed:
            processed["additionalProperties"] = False
            processed["required"] = processed.get("required", [])
            processed["properties"] = {
                k: ToolDefinition._process_nested(v, strip_unsupported)
                for k, v in processed["properties"].items()
            }
        elif processed.get("type") == "array" and "items" in processed:
            processed["items"] = ToolDefinition._process_nested(
                processed["items"], strip_unsupported
            )
        return processed

    # ------------------------------------------------------------------
    # Provider format converters
    # ------------------------------------------------------------------

    def to_mcp_format(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self._build_json_schema(),
            "output_schema": self.output_schema or {"type": "null"},
            "annotations": self.annotations,
        }

    def to_openai_format(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._build_json_schema(strip_openai_unsupported=True),
            },
        }

    def to_openai_responses_format(self) -> dict[str, Any]:
        return {
            "type": "function",
            "name": self.name,
            "description": self.description,
            "parameters": self._build_json_schema(strip_openai_unsupported=True),
        }

    def to_google_format(self) -> dict[str, Any]:
        def _build(param_dict: dict[str, Any] | str) -> dict[str, Any]:
            if isinstance(param_dict, str):
                return {"type": param_dict}
            s: dict[str, Any] = {}
            ptype = param_dict.get("type", "string")
            if isinstance(ptype, list):
                non_null = [t for t in ptype if t != "null"]
                ptype = non_null[0] if non_null else "string"
            s["type"] = ptype
            if param_dict.get("description"):
                s["description"] = param_dict["description"]
            if "enum" in param_dict:
                s["enum"] = param_dict["enum"]
            if ptype == "array" and "items" in param_dict:
                s["items"] = _build(param_dict["items"])
            if ptype == "object" and "properties" in param_dict:
                s["properties"] = {
                    k: _build(v) for k, v in param_dict["properties"].items()
                }
                if "required" in param_dict:
                    s["required"] = param_dict["required"]
            return s

        properties: dict[str, Any] = {}
        required: list[str] = []
        for key, param in self.parameters.items():
            properties[key] = _build(param)
            if param.get("required", False):
                required.append(key)

        params_schema: dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            params_schema["required"] = required
        return {
            "name": self.name,
            "description": self.description,
            "parameters": params_schema,
        }

    def to_anthropic_format(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self._build_json_schema(),
        }

    def get_provider_format(self, provider: str) -> dict[str, Any]:
        formatters: dict[str, Callable[[], dict[str, Any]]] = {
            "openai": self.to_openai_responses_format,
            "anthropic": self.to_anthropic_format,
            "google": self.to_google_format,
            "cerebras": self.to_openai_format,
            "xai": self.to_openai_format,
            "together": self.to_openai_format,
            "groq": self.to_openai_format,
            "mcp": self.to_mcp_format,
        }
        return formatters.get(provider, self.to_openai_format)()

    # ------------------------------------------------------------------
    # User-facing message
    # ------------------------------------------------------------------

    def format_user_message(self, arguments: dict[str, Any]) -> str:
        if not self.on_call_message_template:
            return f"Executing {' '.join(self.name.split('_')).title()}"
        message = self.on_call_message_template
        for placeholder in re.findall(r"\{\{(\w+)\}\}", message):
            if placeholder in arguments:
                val = arguments[placeholder]
                replacement = (
                    ", ".join(str(i) for i in val)
                    if isinstance(val, list)
                    else str(val)
                )
                message = message.replace(f"{{{{{placeholder}}}}}", replacement)
        return message


CxToolCallStatus = Literal["pending", "running", "completed", "error"]


class CxToolCallRecord(BaseModel):
    """Row in the ``cx_tool_call`` table — single source of truth for a tool call.

    Two-phase lifecycle:
      1. INSERT with status='running' when execution starts (captures the attempt)
      2. UPDATE with status='completed'/'error' when execution finishes

    cx_message rows with role='tool' are lightweight positional markers;
    the full data lives here.
    """

    id: str = Field(default_factory=lambda: str(uuid4()))

    # Relationships
    conversation_id: str
    message_id: str | None = None
    user_id: str
    request_id: str | None = None

    # Tool identity
    tool_name: str
    tool_type: ToolType = ToolType.LOCAL
    call_id: str

    # Lifecycle status
    status: CxToolCallStatus = "pending"

    # Input
    arguments: dict[str, Any] = Field(default_factory=dict)

    # Output (single source of truth)
    success: bool = True
    output: str | None = None
    output_type: str = "text"
    is_error: bool = False
    error_type: str | None = None
    error_message: str | None = None

    # Performance
    duration_ms: int = 0
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Cost / usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cost_usd: float = 0.0

    # Execution context
    iteration: int = 0
    retry_count: int = 0
    parent_call_id: str | None = None

    # Streaming events (accumulated during execution, written once)
    execution_events: list[dict[str, Any]] = Field(default_factory=list)

    # Persistence
    persist_key: str | None = None
    file_path: str | None = None

    # Standard cx_ fields
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deleted_at: datetime | None = None
