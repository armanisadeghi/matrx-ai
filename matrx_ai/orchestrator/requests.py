"""
Unified AI API System for OpenAI, Anthropic, and Google Gemini
Preserves ALL content types and metadata from all providers
"""

import uuid
from dataclasses import asdict, dataclass, field, replace
from datetime import datetime, timezone
from typing import Any

from config import (
    MessageList,
    ToolResultContent,
    UnifiedConfig,
    UnifiedMessage,
    UnifiedResponse,
)
from config.usage_config import AggregatedUsage, TokenUsage
from context.emitter_protocol import Emitter
from orchestrator.tracking import TimingUsage

from .tracking import ToolCallUsage

# ============================================================================
# UNIFIED CLIENT
# ============================================================================


@dataclass
class AIMatrixRequest:
    conversation_id: str

    config: UnifiedConfig

    debug: bool | None = False

    request_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str | None = None  # API key ID or session ID
    status: str | None = None

    # === USAGE TRACKING ===
    usage_history: list[TokenUsage] = field(default_factory=list)
    """Track usage from each API call in this request"""

    timing_history: list[TimingUsage] = field(default_factory=list)
    """Track timing from each step in this request"""

    tool_call_history: list[ToolCallUsage] = field(default_factory=list)
    """Track tool calls from each iteration in this request"""

    # === PARENT TRACKING ===
    parent_conversation_id: str | None = None

    # === EXTENSIBILITY ===
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())

    @property
    def user_id(self) -> str:
        from context.app_context import get_app_context

        return get_app_context().user_id

    @property
    def emitter(self) -> Emitter | None:
        from context.app_context import try_get_app_context

        ctx = try_get_app_context()
        return ctx.emitter if ctx else None

    @property
    def total_usage(self) -> AggregatedUsage:
        return TokenUsage.aggregate_by_model(self.usage_history)

    @property
    def timing_stats(self) -> dict[str, Any]:
        """Aggregate timing statistics for the request process."""
        return TimingUsage.aggregate(self.timing_history)

    @property
    def tool_call_stats(self) -> dict[str, Any]:
        """Aggregate tool call statistics for the request process."""
        return ToolCallUsage.aggregate(self.tool_call_history)

    def add_usage(self, usage: TokenUsage | None) -> None:
        """Add usage from an API response to the history."""
        if usage:
            self.usage_history.append(usage)

    def add_timing(self, timing: TimingUsage | None) -> None:
        """Add timing statistics to the history."""
        if timing:
            self.timing_history.append(timing)

    def add_tool_calls(self, tool_calls: ToolCallUsage | None) -> None:
        """Add tool call statistics to the history."""
        if tool_calls:
            self.tool_call_history.append(tool_calls)

    @classmethod
    def from_dict(
        cls, data: dict[str, Any], emitter: Emitter | None = None
    ) -> "AIMatrixRequest":
        """Create AIMatrixRequest from dictionary.

        The ``emitter`` parameter is accepted for backward compatibility
        but ignored; the emitter is read from ExecutionContext.
        """
        config_data = data.get("config", {})
        if isinstance(config_data, dict):
            config = UnifiedConfig.from_dict(config_data)
        else:
            config = config_data

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)

        return cls(
            conversation_id=data.get("conversation_id", ""),
            config=config,
            debug=data.get("debug", False),
            request_id=data.get("request_id"),
            created_at=created_at,
            created_by=data.get("created_by"),
            status=data.get("status"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def add_response(
        cls,
        original_request: "AIMatrixRequest",
        response: UnifiedResponse,
        tool_results: list[ToolResultContent] | None = None,
    ) -> "AIMatrixRequest":
        """Add response (and optionally tool results) to the conversation history.

        This is used both when continuing with tool results and when finishing
        without tool results.
        """
        messages = response.messages
        if isinstance(response.messages, UnifiedMessage):
            messages = [messages]
            print("Converted UnifiedMessage to list of messages")

        # Create new MessageList with extended messages
        updated_messages = MessageList(
            _messages=[
                *original_request.config.messages.to_list(),
                *messages,
            ]
        )

        if tool_results:
            # Use role='tool' to distinguish from actual user messages
            updated_messages.append(UnifiedMessage(role="tool", content=tool_results))

        # Create new request with updated messages (everything else stays the same)
        new_config = replace(original_request.config, messages=updated_messages)
        return replace(original_request, config=new_config)

    def to_dict(self) -> dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            # "ai_model_id": self.ai_model_id,
            "debug": self.debug,
            "config": self.config.to_dict(),
            "request_id": self.request_id,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "status": self.status,
            "metadata": self.metadata,
        }


@dataclass
class CompletedRequest:
    """
    Represents a completed AI request with all accumulated responses and usage.

    Designed for easy client-side continuation:
    - Simply add a new message to `request.config.messages`
    - Call the API again with the updated `request`
    - All conversation history and usage is automatically tracked

    No duplication - all messages are in `request.config.messages`
    """

    request: AIMatrixRequest
    """Complete request with full conversation history - ready for next call"""

    iterations: int
    """Number of API calls made"""

    final_response: UnifiedResponse
    """The final API response that completed execution"""

    total_usage: AggregatedUsage = field(default_factory=AggregatedUsage)
    """Complete usage breakdown with individual calls by model and totals"""

    timing_stats: dict[str, Any] = field(default_factory=dict)
    """Complete timing breakdown including total duration, API time, and tool time"""

    tool_call_stats: dict[str, Any] = field(default_factory=dict)
    """Complete tool call breakdown including total calls, by tool name, and success/error counts"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata (finish_reason, timestamps, etc.)"""

    # Position tracking for cx_user_request
    trigger_message_position: int | None = None
    """Position of the user message that triggered this execution"""

    result_start_position: int | None = None
    """First message position produced by this execution"""

    result_end_position: int | None = None
    """Last message position produced by this execution"""

    # Convenience properties for easy access to key info
    @property
    def conversation_id(self) -> str:
        """Quick access to conversation ID"""
        return self.request.conversation_id

    @property
    def user_id(self) -> str:
        """Quick access to user ID"""
        return self.request.user_id

    @property
    def messages(self) -> MessageList:
        """Quick access to all messages in conversation"""
        return self.request.config.messages

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding non-serializable fields like emitter"""
        return {
            "request": self.request.to_dict(),  # Uses AIMatrixRequest.to_dict() which excludes emitter
            "iterations": self.iterations,
            "final_response": self.final_response.to_dict()
            if hasattr(self.final_response, "to_dict")
            else {},
            "total_usage": self.total_usage.to_dict(),
            "timing_stats": self.timing_stats,
            "tool_call_stats": self.tool_call_stats,
            "metadata": self.metadata,
        }

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to the cx_ v2 storage format for database persistence.

        Returns dict with:
            - conversation: dict matching cx_conversation columns
            - messages: list[dict] matching cx_message rows
            - user_request: dict matching cx_user_request row (aggregated parent)
            - requests: list[dict] matching cx_request rows (one per iteration)
        """
        config = self.request.config
        config_storage = config.to_storage_dict()
        # vcprint(config_storage, "[CompletedRequest] Config Storage", color="yellow")

        # --- cx_conversation row ---
        conversation = {
            "user_id": self.request.user_id,
            "ai_model": config_storage["model"],
            "system_instruction": config_storage["system_instruction"],
            "config": config_storage["config"],
            "message_count": len(config_storage["messages"]),
            "parent_conversation_id": self.request.parent_conversation_id,
        }

        # --- cx_message rows (with position and status) ---
        messages = []
        for position, msg_dict in enumerate(config_storage["messages"]):
            msg_row: dict[str, Any] = {
                "role": msg_dict["role"],
                "position": position,
                "content": msg_dict["content"],
            }
            msg_status = msg_dict.get("status")
            if msg_status and msg_status != "active":
                msg_row["status"] = msg_status
            messages.append(msg_row)

        # --- cx_request rows (one per iteration) ---
        # Zip the three history lists by iteration index.
        # usage_history and timing_history should be 1:1 with iterations;
        # tool_call_history only has entries for iterations that had tool calls.
        usage_list = self.request.usage_history
        timing_list = self.request.timing_history

        # Index tool_call_history by iteration number for quick lookup
        tool_calls_by_iter: dict[int, ToolCallUsage] = {}
        for tc in self.request.tool_call_history:
            tool_calls_by_iter[tc.iteration] = tc

        request_rows: list[dict[str, Any]] = []
        for i in range(self.iterations):
            row: dict[str, Any] = {"iteration": i + 1}

            # Usage for this iteration
            if i < len(usage_list):
                u = usage_list[i]
                row["ai_model"] = u.matrx_model_name
                row["api_class"] = u.api
                row["input_tokens"] = u.input_tokens
                row["output_tokens"] = u.output_tokens
                row["cached_tokens"] = u.cached_input_tokens
                row["total_tokens"] = u.total_tokens
                row["response_id"] = u.response_id or None
                cost = u.calculate_cost()
                if cost is not None:
                    row["cost"] = round(cost, 6)

            # Timing for this iteration
            if i < len(timing_list):
                t = timing_list[i]
                row["api_duration_ms"] = int(t.api_call_duration * 1000)
                row["tool_duration_ms"] = int(t.tool_execution_duration * 1000)
                row["total_duration_ms"] = int(t.total_duration * 1000)

            # Tool calls for this iteration (iteration is 1-based)
            tc_entry = tool_calls_by_iter.get(i + 1)
            if tc_entry:
                row["tool_calls_count"] = tc_entry.tool_calls_count
                row["tool_calls_details"] = tc_entry.tool_calls_details
            else:
                row["tool_calls_count"] = 0

            # Finish reason only on last iteration
            if i == self.iterations - 1:
                fr = self.metadata.get("finish_reason")
                row["finish_reason"] = str(fr) if fr is not None else None

            request_rows.append(row)

        # --- cx_user_request row (aggregated parent) ---
        usage_total = self.total_usage.total
        timing_agg = self.timing_stats
        tool_stats = self.tool_call_stats

        # Calculate total cost from per-iteration costs
        total_cost = sum(r.get("cost", 0) for r in request_rows)

        user_request: dict[str, Any] = {
            "request_id": self.request.request_id,
            "conversation_id": self.request.conversation_id,
            "user_id": self.request.user_id,
            "ai_model": config.model,
            "api_class": usage_list[0].api if usage_list else None,
            "total_input_tokens": usage_total.input_tokens,
            "total_output_tokens": usage_total.output_tokens,
            "total_cached_tokens": usage_total.cached_input_tokens,
            "total_tokens": usage_total.total_tokens,
            "total_cost": round(total_cost, 6) if total_cost else 0,
            "iterations": self.iterations,
            "total_tool_calls": tool_stats.get("total_tool_calls", 0),
            "finish_reason": str(self.metadata["finish_reason"])
            if self.metadata.get("finish_reason") is not None
            else None,
        }

        # Aggregated timing
        if timing_agg:
            api_dur = timing_agg.get("api_duration")
            tool_dur = timing_agg.get("tool_duration")
            total_dur = timing_agg.get("total_duration")
            if api_dur is not None:
                user_request["api_duration_ms"] = int(api_dur * 1000)
            if tool_dur is not None:
                user_request["tool_duration_ms"] = int(tool_dur * 1000)
            if total_dur is not None:
                user_request["total_duration_ms"] = int(total_dur * 1000)

        # Position tracking
        if self.trigger_message_position is not None:
            user_request["trigger_message_position"] = self.trigger_message_position
        if self.result_start_position is not None:
            user_request["result_start_position"] = self.result_start_position
        if self.result_end_position is not None:
            user_request["result_end_position"] = self.result_end_position

        # Status from metadata
        status = self.metadata.get("status")
        if status == "failed" or status == "max_iterations_exceeded":
            user_request["status"] = "failed"
            user_request["error"] = self.metadata.get("error")
        else:
            user_request["status"] = "completed"

        # Caller-supplied metadata from the request is the base layer.
        # System-generated fields (response_id, usage_by_model) are merged on top
        # so they are always present regardless of what the caller provided.
        request_metadata: dict[str, Any] = dict(self.request.metadata)
        if self.metadata.get("response_id"):
            request_metadata["response_id"] = self.metadata["response_id"]
        if self.total_usage.by_model:
            request_metadata["usage_by_model"] = {
                k: asdict(v) for k, v in self.total_usage.by_model.items()
            }
        user_request["metadata"] = request_metadata

        return {
            "conversation": conversation,
            "messages": messages,
            "user_request": user_request,
            "requests": request_rows,
        }
