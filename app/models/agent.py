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
    messages: list[Message] = Field(..., min_length=1)
    stream: bool = True
    stream_mode: StreamMode = StreamMode.sse
    config: dict[str, Any] = Field(default_factory=dict)
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
