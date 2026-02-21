from typing import Any

from pydantic import BaseModel, Field


class ToolParameter(BaseModel):
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: list[ToolParameter] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallRequest(BaseModel):
    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    call_id: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ToolCallResult(BaseModel):
    call_id: str | None = None
    tool_name: str
    result: Any
    error: str | None = None
    elapsed_ms: float | None = None
