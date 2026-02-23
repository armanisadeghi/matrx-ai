from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

from app.models.chat import Message, StreamMode


class AgentStatus(StrEnum):
    idle = "idle"
    running = "running"
    paused = "paused"
    completed = "completed"
    failed = "failed"


class AgentRunRequest(BaseModel):
    """Body for POST /api/ai/agents/{agent_id} — start a new agent conversation."""
    user_input: str | None = None
    messages: list[Message] | None = None
    variables: dict[str, Any] = Field(default_factory=dict)
    config_overrides: dict[str, Any] = Field(default_factory=dict)
    stream: bool = True
    stream_mode: StreamMode = StreamMode.sse
    debug: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentEvent(BaseModel):
    event: str  # "thinking" | "tool_call" | "chunk" | "done" | "error"
    agent_id: str
    data: dict[str, Any] = Field(default_factory=dict)
    step: int = 0


class AgentInfo(BaseModel):
    agent_id: str
    status: AgentStatus
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)
