"""
Unified AI API System for OpenAI, Anthropic, and Google Gemini
Preserves ALL content types and metadata from all providers
"""

from models.ai_model_manager import get_ai_model_manager
from typing import Any, Dict, List, Literal, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import uuid
from client.usage import TokenUsage, AggregatedUsage
from client.timing import TimingUsage
from client.tool_call_tracking import ToolCallUsage
from context.emitter_protocol import Emitter
from dataclasses import replace
from config.unified_config import (
    UnifiedConfig,
    UnifiedResponse,
    UnifiedMessage,
    MessageList,
    ToolResultContent,
)
from matrx_utils import vcprint
from prompts.session import SimpleSession


# ============================================================================
# UNIFIED CLIENT
# ============================================================================


@dataclass
class AIMatrixRequest:
    conversation_id: str

    config: UnifiedConfig

    debug: Optional[bool] = False

    request_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: Optional[str] = None  # API key ID or session ID
    status: Optional[str] = None

    # === USAGE TRACKING ===
    usage_history: List[TokenUsage] = field(default_factory=list)
    """Track usage from each API call in this request"""

    timing_history: List[TimingUsage] = field(default_factory=list)
    """Track timing from each step in this request"""

    tool_call_history: List[ToolCallUsage] = field(default_factory=list)
    """Track tool calls from each iteration in this request"""

    # === PARENT TRACKING ===
    parent_conversation_id: Optional[str] = None

    # === EXTENSIBILITY ===
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.request_id is None:
            self.request_id = str(uuid.uuid4())

    @property
    def user_id(self) -> str:
        from context.app_context import get_app_context
        return get_app_context().user_id

    @property
    def emitter(self) -> Optional[Emitter]:
        from context.app_context import try_get_app_context
        ctx = try_get_app_context()
        return ctx.emitter if ctx else None

    @property
    def total_usage(self) -> AggregatedUsage:
        return TokenUsage.aggregate_by_model(self.usage_history)

    @property
    def timing_stats(self) -> Dict[str, Any]:
        """Aggregate timing statistics for the request process."""
        return TimingUsage.aggregate(self.timing_history)

    @property
    def tool_call_stats(self) -> Dict[str, Any]:
        """Aggregate tool call statistics for the request process."""
        return ToolCallUsage.aggregate(self.tool_call_history)

    def add_usage(self, usage: Optional[TokenUsage]) -> None:
        """Add usage from an API response to the history."""
        if usage:
            self.usage_history.append(usage)

    def add_timing(self, timing: Optional[TimingUsage]) -> None:
        """Add timing statistics to the history."""
        if timing:
            self.timing_history.append(timing)

    def add_tool_calls(self, tool_calls: Optional[ToolCallUsage]) -> None:
        """Add tool call statistics to the history."""
        if tool_calls:
            self.tool_call_history.append(tool_calls)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], emitter: Optional[Emitter] = None
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
    def from_session(
        cls,
        config: UnifiedConfig,
        session: SimpleSession,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "AIMatrixRequest":
        """Create AIMatrixRequest from SimpleSession.

        User identity and emitter are read from ExecutionContext.
        """
        return cls(
            conversation_id=session.conversation_id,
            config=config,
            debug=session.debug,
            parent_conversation_id=getattr(session, "parent_conversation_id", None),
            metadata=metadata or {},
        )

    @classmethod
    def add_response(
        cls,
        original_request: "AIMatrixRequest",
        response: UnifiedResponse,
        tool_results: Optional[List[ToolResultContent]] = None,
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

    def to_dict(self) -> Dict[str, Any]:
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


# Maps api_class to endpoint name for routing
API_CLASS_TO_ENDPOINT = {
    "openai_standard": "openai_chat",
    "openai_reasoning": "openai_chat",
    "google_standard": "google_chat",
    "google_thinking": "google_chat",
    "google_thinking_3": "google_chat",
    "google_image_generation": "google_chat",
    "anthropic_standard": "anthropic_chat",
    "anthropic_adaptive": "anthropic_chat",
    "together_text_standard": "together_chat",
    "together_image": "together_image",
    "together_video": "together_video",
    "groq_standard": "groq_chat",
    "cerebras_standard": "cerebras_chat",
    "cerebras_reasoning": "cerebras_chat",
    "xai_standard": "xai_chat",
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

    timing_stats: Dict[str, Any] = field(default_factory=dict)
    """Complete timing breakdown including total duration, API time, and tool time"""

    tool_call_stats: Dict[str, Any] = field(default_factory=dict)
    """Complete tool call breakdown including total calls, by tool name, and success/error counts"""

    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata (finish_reason, timestamps, etc.)"""

    # Position tracking for cx_user_request
    trigger_message_position: Optional[int] = None
    """Position of the user message that triggered this execution"""

    result_start_position: Optional[int] = None
    """First message position produced by this execution"""

    result_end_position: Optional[int] = None
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

    def to_dict(self) -> Dict[str, Any]:
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

    def to_storage_dict(self) -> Dict[str, Any]:
        """Serialize to the cx_ v2 storage format for database persistence.

        Returns dict with:
            - conversation: dict matching cx_conversation columns
            - messages: list[dict] matching cx_message rows
            - user_request: dict matching cx_user_request row (aggregated parent)
            - requests: list[dict] matching cx_request rows (one per iteration)
        """
        config = self.request.config
        config_storage = config.to_storage_dict()

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
            msg_row: Dict[str, Any] = {
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
        tool_calls_by_iter: Dict[int, ToolCallUsage] = {}
        for tc in self.request.tool_call_history:
            tool_calls_by_iter[tc.iteration] = tc

        request_rows: List[Dict[str, Any]] = []
        for i in range(self.iterations):
            row: Dict[str, Any] = {"iteration": i + 1}

            # Usage for this iteration
            if i < len(usage_list):
                u = usage_list[i]
                row["ai_model"] = u.model
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

        user_request: Dict[str, Any] = {
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
            "finish_reason": str(self.metadata["finish_reason"]) if self.metadata.get("finish_reason") is not None else None,
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
        request_metadata: Dict[str, Any] = dict(self.request.metadata)
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


class UnifiedAIClient:
    """Unified client for all AI providers"""

    model_manager = get_ai_model_manager()

    def __init__(self):
        from providers.google_api import GoogleChat
        from providers.openai_api import OpenAIChat
        from providers.anthropic_api import AnthropicChat
        from providers.cerebras_api import CerebrasChat
        from providers.together_api import TogetherChat
        from providers.groq_api import GroqChat
        from providers.xai_api import XAIChat

        self.google_chat = GoogleChat()
        self.openai_chat = OpenAIChat()
        self.anthropic_chat = AnthropicChat()
        self.cerebras_chat = CerebrasChat()
        self.together_chat = TogetherChat()
        self.groq_chat = GroqChat()
        self.xai_chat = XAIChat()

    async def execute(
        self,
        request: AIMatrixRequest,
    ) -> Dict[str, Any]:
        from media.audio.audio_preprocessing import (
            preprocess_audio_in_messages,
            should_preprocess_audio,
        )
        from media.audio.audio_support import api_class_supports_audio

        config = request.config
        model_id_or_name = config.model
        debug = request.debug

        # Get model details first (need to know API class for audio support check)
        model_data = await self.model_manager.load_model(model_id_or_name)

        if not model_data:
            raise ValueError(f"Model not found: {model_id_or_name}")

        model_name = model_data.name
        config.model = model_name

        api_class = model_data.api_class
        endpoint = API_CLASS_TO_ENDPOINT.get(api_class)

        # Check if audio needs transcription (either explicitly requested or API doesn't support audio)
        if should_preprocess_audio(config.messages, api_class):
            if debug:
                if api_class_supports_audio(api_class):
                    vcprint(
                        "Audio auto-transcription explicitly enabled - preprocessing messages",
                        "Unified Client",
                        color="cyan",
                    )
                else:
                    vcprint(
                        f"API '{api_class}' doesn't support audio - auto-transcribing as fallback",
                        "Unified Client",
                        color="yellow",
                    )

            config.messages, transcription_usage_list = preprocess_audio_in_messages(
                config.messages, api_class, debug=debug
            )

            # Add transcription usage to request history
            for usage in transcription_usage_list:
                request.add_usage(usage)
                if debug:
                    vcprint(
                        f"Tracked Groq transcription: {usage.metadata.get('duration_seconds', 0):.1f}s "
                        f"({usage.metadata.get('billed_duration', 0):.1f}s billed)",
                        "Usage Tracking",
                        color="blue",
                    )

        if not endpoint:
            raise ValueError(f"No endpoint mapping for api_class: {api_class}")

        if endpoint == "openai_chat":
            return await self.openai_chat.execute(config, api_class, debug)
        elif endpoint == "anthropic_chat":
            return await self.anthropic_chat.execute(config, api_class, debug)
        elif endpoint == "google_chat":
            return await self.google_chat.execute(config, api_class, debug)
        elif endpoint == "cerebras_chat":
            return await self.cerebras_chat.execute(config, api_class, debug)
        elif endpoint == "together_chat":
            return await self.together_chat.execute(config, api_class, debug)
        elif endpoint == "groq_chat":
            return await self.groq_chat.execute(config, api_class, debug)
        elif endpoint == "xai_chat":
            return await self.xai_chat.execute(config, api_class, debug)
        else:
            raise ValueError(f"No execution method for api_class: {api_class}")

    async def translate_request(
        self,
        request: AIMatrixRequest,
    ) -> Dict[str, Any]:
        """Translate unified request to provider-specific format"""
        from client.translators import (
            OpenAITranslator,
            AnthropicTranslator,
            GoogleTranslator,
            TogetherTranslator,
            GroqTranslator,
            XAITranslator,
            CerebrasTranslator,
        )

        config = request.config
        model_id_or_name = config.model

        # Get model details
        model_data = await self.model_manager.load_model(model_id_or_name)

        if not model_data:
            raise ValueError(f"Model not found: {model_id_or_name}")

        model_name = model_data.name
        config.model = model_name

        api_class = model_data.api_class
        endpoint = API_CLASS_TO_ENDPOINT.get(api_class)

        if not endpoint:
            raise ValueError(f"No endpoint mapping for api_class: {api_class}")

        if api_class == "openai_standard":
            return OpenAITranslator().to_openai(config, api_class)
        elif api_class == "openai_reasoning":
            return OpenAITranslator().to_openai(config, api_class)
        elif api_class in ("anthropic_standard", "anthropic", "anthropic_adaptive"):
            return AnthropicTranslator().to_anthropic(config, api_class)
        elif api_class == "google_standard":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "google_thinking":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "google_thinking_3":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "cerebras_standard":
            return CerebrasTranslator().to_cerebras(config, api_class)
        elif api_class == "cerebras_reasoning":
            return CerebrasTranslator().to_cerebras(config, api_class)
        elif api_class == "together_text_standard":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "together_image":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "together_video":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "groq_standard":
            return GroqTranslator().to_groq(config, api_class)
        elif api_class == "xai_standard":
            return XAITranslator().to_xai(config, api_class)
        else:
            raise ValueError(f"Unknown provider: {endpoint}")

    def translate_response(
        self,
        provider: Literal[
            "openai", "anthropic", "gemini", "together", "groq", "xai", "cerebras"
        ],
        response: Dict[str, Any],
    ) -> UnifiedResponse:
        """Translate provider-specific response to unified format"""
        from client.translators import (
            OpenAITranslator,
            AnthropicTranslator,
            GoogleTranslator,
            TogetherTranslator,
            GroqTranslator,
            XAITranslator,
            CerebrasTranslator,
        )

        if provider.startswith("openai"):
            return OpenAITranslator().from_openai(response)
        elif provider.startswith("anthropic"):
            return AnthropicTranslator().from_anthropic(response)
        elif provider.startswith("gemini"):
            return GoogleTranslator().from_google(response)
        elif provider.startswith("together"):
            return TogetherTranslator().from_together(response)
        elif provider.startswith("groq"):
            return GroqTranslator().from_groq(response)
        elif provider.startswith("xai"):
            return XAITranslator().from_xai(response)
        elif provider.startswith("cerebras"):
            return CerebrasTranslator().from_cerebras(response)
        else:
            raise ValueError(f"Unknown provider: {provider}")
