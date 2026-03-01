"""
Unified AI API Configuration System for OpenAI, Anthropic, and Google Gemini
Preserves ALL content types and metadata from all providers
"""

from dataclasses import dataclass, field, fields
from typing import Any, Literal

from matrx_utils import vcprint

from instructions.core import SystemInstruction
from instructions.pattern_parser import resolve_matrx_patterns

from .enums import Role
from .message_config import MessageList, UnifiedMessage
from .unified_content import (
    TextContent,
)
from .usage_config import TokenUsage


@dataclass
class UnifiedConfig:
    """
    Pure LLM request - no AI Matrix specifics

    Core Principle:
    - system_instruction is stored ONLY in the system_instruction field
    - messages NEVER contain system/developer roles in UnifiedConfig
    - System messages are only created during API conversion (translator methods)
    """

    model: str
    messages: MessageList | list[UnifiedMessage] | list[dict[str, Any]]
    system_instruction: str | dict | SystemInstruction | None = None
    stream: bool = False

    max_output_tokens: int | None = None
    temperature: float | None = None
    top_p: float | None = None
    top_k: int | None = None

    tools: list = field(default_factory=list)
    # Literal["none", "auto", "required"]
    tool_choice: Literal["none", "auto", "required"] | None = None
    parallel_tool_calls: bool = True

    # OpenAI thinking format
    reasoning_effort: Literal["auto", "none", "minimal", "low", "medium", "high", "xhigh"] | None = None
    reasoning_summary: Literal["concise", "detailed", "never", "auto", "always"] | None = None

    # Google Gemini 3 thinking format
    thinking_level: Literal["minimal", "low", "medium", "high"] | None = None
    include_thoughts: bool | None = None

    # Anthropic thinking & legacy Google Gemini 2 thinking format
    thinking_budget: int | None = None

    response_format: dict[str, Any] | None = None
    stop_sequences: list = field(default_factory=list)

    store: bool | None = None
    verbosity: str | None = None

    # Media/attachment settings
    internal_web_search: bool | None = None
    internal_url_context: bool | None = None

    # Image generation settings
    size: str | None = None
    quality: str | None = None
    count: int = 1

    # Audio settings
    audio_voice: str | None = None
    audio_format: str | None = None

    # Video generation settings
    seconds: str | None = None
    fps: int | None = None
    steps: int | None = None
    seed: int | None = None
    guidance_scale: int | None = None
    output_quality: int | None = None
    negative_prompt: str | None = None
    output_format: str | None = None
    width: int | None = None
    height: int | None = None
    frame_images: list | None = None
    reference_images: list | None = None
    disable_safety_checker: bool | None = None

    custom_configs: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """
        Normalize messages and system_instruction.

        System instruction normalization:
        - str: Wrapped in SystemInstruction (date auto-injected by default), resolved to string.
        - dict: Converted to SystemInstruction from keys (content, include_date, etc.), resolved to string.
        - SystemInstruction: Resolved to string directly.
        - None: Left as None.

        After __post_init__, system_instruction is always str | None.
        """
        # Convert messages to MessageList if needed
        if not isinstance(self.messages, MessageList):
            if isinstance(self.messages, list):
                self.messages = MessageList(_messages=self.messages)
            else:
                raise TypeError(
                    f"messages must be MessageList or list, got {type(self.messages)}"
                )

        self.tool_choice = self._normalize_tool_choice(self.tool_choice)
        self.system_instruction = self._resolve_system_instruction(
            self.system_instruction
        )
        self._resolve_message_patterns()

    def _resolve_message_patterns(self) -> None:
        """Resolve <<MATRX>> data-fetch patterns in all TextContent across messages."""
        for message in self.messages:
            for content in message.content:
                if isinstance(content, TextContent) and content.text:
                    content.text = resolve_matrx_patterns(content.text)

    @staticmethod
    def _resolve_system_instruction(
        raw: str | dict | SystemInstruction | None,
    ) -> str | None:
        if raw is None:
            return None
        # Already resolved — skip re-wrapping to prevent date being prepended again
        # on every dataclasses.replace() call during tool-call iteration loops.
        if isinstance(raw, str):
            return raw
        return str(SystemInstruction.from_value(raw))

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UnifiedConfig":
        """
        Create UnifiedConfig from dictionary (e.g., from API).

        Extracts system/developer messages from messages list and places them
        in system_instruction field.
        """
        # Map max_tokens to max_output_tokens if needed (for API compatibility)
        if "max_tokens" in data and "max_output_tokens" not in data:
            data["max_output_tokens"] = data["max_tokens"]
            del data["max_tokens"]
        elif "max_tokens" in data:
            # If both exist, remove max_tokens and use max_output_tokens
            del data["max_tokens"]

        valid_fields = {f.name for f in fields(cls)}
        valid_fields.add("model_id")
        unrecognized_keys = set(data.keys()) - valid_fields

        if unrecognized_keys:
            vcprint(
                unrecognized_keys,
                "Unrecognized keys in UnifiedConfig (likely expected, but confirm if update is needed on client side or our server side code)",
                color="red",
            )

        # Parse messages and extract system instruction
        messages_data = data.get("messages", [])
        parsed_messages = []
        extracted_system_text = ""

        for msg_data in messages_data:
            # Convert to UnifiedMessage if needed
            if isinstance(msg_data, dict):
                msg = UnifiedMessage.from_dict(msg_data)
            elif hasattr(msg_data, "__dict__"):  # Already a UnifiedMessage object
                msg = msg_data
            else:
                continue

            # Extract system/developer messages to system_instruction
            if msg.role in (Role.SYSTEM, Role.DEVELOPER, "system", "developer"):
                # Extract text content from first system/developer message
                if not extracted_system_text and msg.content:
                    for content in msg.content:
                        if isinstance(content, TextContent):
                            extracted_system_text += content.text
                # Don't add to parsed_messages - system goes to system_instruction
            else:
                # Regular message - add to list
                parsed_messages.append(msg)

        # Priority: explicit system_instruction > extracted from messages
        # Use 'is not None' check so dict values (including potentially empty ones)
        # are preserved rather than being swallowed by falsy coalescing.
        explicit_si = data.get("system_instruction")
        if explicit_si is not None:
            system_instruction = explicit_si
        elif extracted_system_text:
            system_instruction = extracted_system_text
        else:
            system_instruction = None

        return cls(
            model=data.get("model", ""),
            messages=parsed_messages,
            system_instruction=system_instruction,
            stream=data.get("stream", False),
            max_output_tokens=data.get("max_output_tokens"),
            temperature=data.get("temperature"),
            top_p=data.get("top_p"),
            top_k=data.get("top_k"),
            tools=data.get("tools", []),
            tool_choice=data.get("tool_choice"),
            parallel_tool_calls=data.get("parallel_tool_calls", True),
            reasoning_effort=data.get("reasoning_effort"),
            reasoning_summary=data.get("reasoning_summary"),
            thinking_level=data.get("thinking_level"),
            include_thoughts=data.get("include_thoughts"),
            thinking_budget=data.get("thinking_budget"),
            response_format=data.get("response_format"),
            stop_sequences=data.get("stop_sequences", []),
            store=data.get("store"),
            verbosity=data.get("verbosity"),
            internal_web_search=data.get("internal_web_search"),
            internal_url_context=data.get("internal_url_context"),
            size=data.get("size"),
            quality=data.get("quality"),
            count=data.get("count", 1),
            audio_voice=data.get("audio_voice"),
            audio_format=data.get("audio_format"),
            seconds=data.get("seconds"),
            fps=data.get("fps"),
            steps=data.get("steps"),
            seed=data.get("seed"),
            guidance_scale=data.get("guidance_scale"),
            output_quality=data.get("output_quality"),
            negative_prompt=data.get("negative_prompt"),
            output_format=data.get("output_format"),
            width=data.get("width"),
            height=data.get("height"),
            frame_images=data.get("frame_images"),
            reference_images=data.get("reference_images"),
            disable_safety_checker=data.get("disable_safety_checker"),
            custom_configs=data.get("custom_configs"),
            metadata=data.get("metadata", {}),
        )

    def _normalize_tool_choice(
        self, tool_choice: Any
    ) -> Literal["none", "auto", "required"] | None:
        if tool_choice in ["none", "auto", "required"]:
            return tool_choice
        elif tool_choice == "any":
            return "required"
        elif tool_choice == "ANY":
            return "required"
        elif tool_choice == "NONE":
            return "none"
        elif tool_choice == "AUTO":
            return "auto"
        elif isinstance(tool_choice, dict):
            return tool_choice["type"]
        elif isinstance(tool_choice, str):
            if tool_choice == "auto":
                return "auto"
            elif tool_choice == "required":
                return "required"
            elif tool_choice == "any":
                return "required"
            elif tool_choice == "none":
                return "none"
            else:
                return None
        elif tool_choice is None:
            return None
        else:
            vcprint(tool_choice, "WARNING: Unknown tool choice type", color="red")
            return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        result = {}

        for key, value in self.__dict__.items():
            if value is None:
                continue

            # Handle MessageList specially
            if isinstance(value, MessageList):
                result[key] = value.to_dict_list()
            elif isinstance(value, list) and value and hasattr(value[0], "to_dict"):
                result[key] = [item.to_dict() for item in value]
            elif hasattr(value, "to_dict"):
                result[key] = value.to_dict()
            else:
                result[key] = value

        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format matching the cx_conversation + cx_message schema.

        Returns dict with:
            - model: str (cx_conversation.model column)
            - system_instruction: str | None (cx_conversation.system_instruction column)
            - config: dict (cx_conversation.config JSONB)
            - messages: list[dict] (each dict is a cx_message row via UnifiedMessage.to_storage_dict)
        """

        message_storage_dicts = [msg.to_storage_dict() for msg in self.messages]
        # vcprint(message_storage_dicts, "[UnifiedConfig] Message Storage Dicts", color="yellow")

        # Top-level columns
        result: dict[str, Any] = {
            "model": self.model,
            "system_instruction": self.system_instruction,
            "messages": message_storage_dicts,
        }

        # Config JSONB -- only include non-default/non-None values
        config: dict[str, Any] = {}
        if self.temperature is not None:
            config["temperature"] = self.temperature
        if self.max_output_tokens is not None:
            config["max_output_tokens"] = self.max_output_tokens
        if self.top_p is not None:
            config["top_p"] = self.top_p
        if self.top_k is not None:
            config["top_k"] = self.top_k
        if self.tools:
            config["tools"] = self.tools
        if self.tool_choice is not None:
            config["tool_choice"] = self.tool_choice
        if not self.parallel_tool_calls:
            config["parallel_tool_calls"] = False
        if self.reasoning_effort is not None:
            config["reasoning_effort"] = self.reasoning_effort
        if self.reasoning_summary is not None:
            config["reasoning_summary"] = self.reasoning_summary
        if self.thinking_level is not None:
            config["thinking_level"] = self.thinking_level
        if self.include_thoughts is not None:
            config["include_thoughts"] = self.include_thoughts
        if self.thinking_budget is not None:
            config["thinking_budget"] = self.thinking_budget
        if self.response_format is not None:
            config["response_format"] = self.response_format
        if self.stop_sequences:
            config["stop_sequences"] = self.stop_sequences
        if self.stream:
            config["stream"] = True
        if self.internal_web_search is not None:
            config["internal_web_search"] = self.internal_web_search
        if self.internal_url_context is not None:
            config["internal_url_context"] = self.internal_url_context
        if self.store is not None:
            config["store"] = self.store
        if self.verbosity is not None:
            config["verbosity"] = self.verbosity

        result["config"] = config
        return result

    def append_user_message(self, text: str, **kwargs) -> None:
        """
        Append a user message to the conversation.

        Args:
            text: The message text
            **kwargs: Additional UnifiedMessage fields (id, name, timestamp, metadata)
        """
        self.messages.append_user_text(text, **kwargs)

    def append_or_extend_user_text(self, text: str, **kwargs) -> None:
        """
        Add user text to the message list.
        """
        self.messages.append_or_extend_user_text(text, **kwargs)

    def append_or_extend_user_input(
        self, user_input: str | list[dict[str, Any]]
    ) -> None:
        """
        Add user input items to the message list.
        """
        self.messages.append_or_extend_user_input(user_input)

    def replace_variables(self, variables: dict[str, Any]) -> None:
        """
        Replace variables throughout the config.
        Handles both system_instruction and all messages.

        Args:
            variables: dict mapping variable names to their values
        """
        # Replace in system_instruction
        if self.system_instruction:
            for var_name, var_value in variables.items():
                self.system_instruction = self.system_instruction.replace(
                    f"{{{{{var_name}}}}}", str(var_value)
                )

        # Replace in all messages
        self.messages.replace_variables(variables)

    def get_last_output(self) -> str:
        """Get the output of the last assistant message."""
        return self.messages.get_last_output()


@dataclass
class UnifiedResponse:
    """Pure LLM response - no AI Matrix specifics"""

    messages: list[UnifiedMessage]
    usage: TokenUsage | None = None
    stop_reason: str | None = None
    finish_reason: str | None = None
    raw_response: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate that usage data is present"""
        if self.usage is None:
            vcprint(
                "⚠️  WARNING: UnifiedResponse missing usage data. This means costs cannot be calculated.",
                color="red",
            )

    def to_dict(self) -> dict[str, Any]:
        result = {}

        for key, value in self.__dict__.items():
            if value is None:
                continue

            if isinstance(value, list) and value and hasattr(value[0], "to_dict"):
                result[key] = [item.to_dict() for item in value]
            elif hasattr(value, "to_dict"):
                result[key] = value.to_dict()
            else:
                result[key] = value

        return result
