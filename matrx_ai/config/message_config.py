from dataclasses import dataclass, field
from typing import Any, Optional, Union

from db.models import CxMessage
from matrx_utils import vcprint
from openai.types.responses import (
    ResponseOutputItem as OpenAIResponseOutputItem,
)

from .enums import Role
from .extra_config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    WebSearchCallContent,
)
from .media_config import (
    AudioContent,
    DocumentContent,
    ImageContent,
    VideoContent,
    YouTubeVideoContent,
    reconstruct_media_content,
)
from .tools_config import ToolCallContent, ToolResultContent
from .unified_content import (
    TextContent,
    ThinkingContent,
    UnifiedContent,
    reconstruct_content,
)


@dataclass
class UnifiedMessage:
    """Pure message - no AI Matrix specifics"""

    role: str
    content: list[UnifiedContent] = field(default_factory=list)
    id: str | None = None
    name: str | None = None
    timestamp: int | None = None
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def parse_content(content_data: str | list[Any]) -> list[UnifiedContent]:
        """Parse content data (string or list) into a list of UnifiedContent objects.

        Can be used standalone or by from_dict and other methods.
        """
        parsed_content: list[UnifiedContent] = []

        if isinstance(content_data, str):
            # Simple string content
            parsed_content = [TextContent(text=content_data)]
        elif isinstance(content_data, list):
            # Array of content objects
            for item in content_data:
                # vcprint(item, "--Item", color="green")
                if isinstance(item, str):
                    parsed_content.append(TextContent(text=item))
                elif isinstance(item, dict):
                    content_type = item.get("type", "text")
                    if (
                        content_type == "text"
                        or content_type == "input_text"
                        or content_type == "output_text"
                    ):
                        parsed_content.append(TextContent(**item))
                    elif (
                        content_type == "image"
                        or content_type == "input_image"
                        or content_type == "output_image"
                    ):
                        # Normalize image_url to url if present
                        if "image_url" in item and "url" not in item:
                            item = {**item, "url": item["image_url"]}
                            item.pop("image_url", None)
                        parsed_content.append(ImageContent(**item))
                    elif (
                        content_type == "audio"
                        or content_type == "input_audio"
                        or content_type == "output_audio"
                    ):
                        if "audio_url" in item and "url" not in item:
                            item = {**item, "url": item["audio_url"]}
                            item.pop("audio_url", None)
                        parsed_content.append(AudioContent(**item))
                    elif (
                        content_type == "video"
                        or content_type == "input_video"
                        or content_type == "output_video"
                    ):
                        if "video_url" in item and "url" not in item:
                            item = {**item, "url": item["video_url"]}
                            item.pop("video_url", None)
                        parsed_content.append(VideoContent(**item))
                    elif content_type == "youtube_video":
                        if "youtube_url" in item and "url" not in item:
                            item = {**item, "url": item["youtube_url"]}
                            item.pop("youtube_url", None)
                        parsed_content.append(YouTubeVideoContent(**item))
                    elif (
                        content_type == "document"
                        or content_type == "input_document"
                        or content_type == "input_file"
                        or content_type == "output_document"
                    ):
                        if "file_url" in item and "url" not in item:
                            item = {**item, "url": item["file_url"]}
                            item.pop("file_url", None)
                        elif "document_url" in item and "url" not in item:
                            item = {**item, "url": item["document_url"]}
                            item.pop("document_url", None)
                        parsed_content.append(DocumentContent(**item))
                    elif content_type == "media":
                        # Unified storage format: dispatch by kind
                        reconstructed = reconstruct_media_content(item)
                        if reconstructed is not None:
                            parsed_content.append(reconstructed)
                    elif content_type == "tool_call" or content_type == "function_call":
                        parsed_content.append(ToolCallContent(**item))
                    elif (
                        content_type == "tool_result"
                        or content_type == "function_result"
                        or content_type == "tool_call_result"
                    ):
                        parsed_content.append(ToolResultContent(**item))
                    elif content_type == "thinking" or content_type == "reasoning":
                        parsed_content.append(ThinkingContent(**item))
                    elif content_type == "code_execution":
                        parsed_content.append(CodeExecutionContent(**item))
                    elif content_type == "code_execution_result":
                        parsed_content.append(CodeExecutionResultContent(**item))
                    elif content_type in [
                        "input_webpage",
                        "input_notes",
                        "input_task",
                        "input_table",
                    ]:
                        print("\n\n" + "=" * 100)
                        vcprint(
                            item,
                            f"!!!!!! {content_type} !!!!!!! Not implemented yet!",
                            color="red",
                        )
                        print("\n\n" + "=" * 100)
                    else:
                        vcprint(
                            item,
                            f"WARNING: Unknown content type: {content_type}",
                            color="red",
                        )

        return parsed_content

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "UnifiedMessage":
        """Create UnifiedMessage from dictionary (e.g., from API)"""
        content_data = data.get("content", [])
        parsed_content = cls.parse_content(content_data)

        return cls(
            role=data.get("role", "user"),
            content=parsed_content,
            id=data.get("id"),
            name=data.get("name"),
            timestamp=data.get("timestamp"),
            status=data.get("status", "active"),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_cx_message(cls, message: CxMessage) -> "UnifiedMessage":
        """Create UnifiedMessage from CxMessage"""
        content = [reconstruct_content(item) for item in (message.content or [])]

        return cls(
            role=message.role,
            content=content,
            id=message.id,
            timestamp=message.created_at.isoformat() if message.created_at else None,
            status=message.status,
            metadata=message.metadata,
        )

    @classmethod
    def from_openai_item(
        cls, item: OpenAIResponseOutputItem
    ) -> Optional["UnifiedMessage"]:
        content = []
        assigned_role = "output"

        item_type = item.type
        if item_type == "message":
            assigned_role = "assistant"
            for content_item in (item.content or []):
                content_type = content_item.type
                if content_type == "output_text":
                    content.append(TextContent.from_openai(content_item, item.id))
                else:
                    vcprint(
                        content_item,
                        f"WARNING: Unknown OpenAI content item type: {content_type}",
                        color="yellow",
                    )
        elif item_type == "reasoning":
            content.append(ThinkingContent.from_openai(item))
        elif item_type == "function_call":
            assigned_role = "tool"
            content.append(ToolCallContent.from_openai(item))
        elif item_type == "web_search_call":
            assigned_role = "tool"
            content.append(WebSearchCallContent.from_openai(item))
        else:
            vcprint(
                item, f"WARNING: Unknown OpenAI item type: {item_type}", color="red"
            )

        return cls(
            id=item.id,
            role=assigned_role,
            content=content,
        )

    @classmethod
    def from_anthropic_content(
        cls, role: str, content: list[dict[str, Any]], id: str
    ) -> Optional["UnifiedMessage"]:
        """Create UnifiedMessage from Anthropic content blocks"""
        content_blocks = []

        for block in content:
            block_type = block.get("type")
            if block_type == "text":
                content_blocks.append(TextContent.from_anthropic(block))
            elif block_type == "tool_use":
                content_blocks.append(ToolCallContent.from_anthropic(block))
            elif block_type == "thinking":
                content_blocks.append(ThinkingContent.from_anthropic(block))
            else:
                vcprint(
                    block,
                    "WARNING: Unknown Anthropic content block type",
                    color="yellow",
                )

        return cls(role=role, content=content_blocks, id=id)

    def to_google_content(self) -> dict[str, Any] | None:
        """Convert message to Google Gemini content format.

        Returns dict with 'role' and 'parts', or None if no valid parts.
        """
        # Convert all content items using their to_google() methods
        parts = []
        for content in self.content:
            part = content.to_google()
            if part:  # Only add if conversion succeeded
                parts.append(part)

        if not parts:
            return None

        # Map role to Google's expected values
        if self.role == "assistant":
            google_role = "model"
        elif self.role in ("user", "tool"):
            google_role = "user"
        else:
            raise ValueError(
                f"Unknown role '{self.role}'. Valid roles are: 'user', 'assistant', 'tool'"
            )

        return {
            "role": google_role,
            "parts": parts,
        }

    def to_openai_items(
        self,
    ) -> list[dict[str, Any]] | dict[str, Any] | None:
        """
        Convert message to OpenAI Responses API format items.

        Returns a list because:
        - Tool calls become separate function_call items
        - Thinking becomes separate reasoning items
        - Tool results become function_call_output items
        - Regular messages stay as message items

        Assistant messages that originated from the Responses API (i.e. have an id
        like "msg_...") must be serialized as raw output-objects:
            {"type": "message", "role": "assistant", "id": "...", "content": [...]}
        rather than the chat-style wrapper {"role": "assistant", "content": [...]}.
        This is required so that a preceding "reasoning" item and its paired
        "message" item are both flat output-objects, satisfying OpenAI's rule that
        a reasoning item must be immediately followed by its associated output item.
        """

        converted = []
        text_content_id = None
        for content in self.content:
            result = None
            if isinstance(content, TextContent):
                result = content.to_openai(role=self.role)
                text_content_id = content.id
            else:
                result = content.to_openai()

            if result is not None:
                converted.append(result)

        if converted and self.role in (Role.OUTPUT, Role.TOOL):
            vcprint(
                converted,
                "[UNIFIED MESSAGE] to_openai_items converted output or tool role",
                color="yellow",
                verbose=True,
            )
            return converted  # Returns list: [item1, item2, item3] & without role, etc.

        elif converted and self.role == Role.ASSISTANT and text_content_id:
            # Prior Responses API output — must be a raw output-object so it is
            # adjacent to any preceding reasoning item in the input array.
            return [
                {
                    "type": "message",
                    "role": "assistant",
                    "id": text_content_id,
                    "content": converted,
                }
            ]

        elif converted:
            return {"role": self.role, "content": converted}
        else:
            vcprint(
                converted,
                "[UNIFIED MESSAGE] to_openai_items converted None role",
                color="red",
                verbose=True,
            )
            return None

    def to_anthropic_blocks(self) -> list[dict[str, Any]]:
        """
        Convert message content to Anthropic format blocks.

        Returns list of content blocks for Anthropic messages.
        """
        # Sanity check - should never happen in UnifiedConfig
        if self.role in (Role.SYSTEM, Role.DEVELOPER, "system", "developer"):
            vcprint(
                "[WARNING] System/developer message found in UnifiedMessage.to_anthropic_blocks(). This should not happen!",
                color="red",
            )
            return []

        content_blocks = []
        for content in self.content:
            converted = content.to_anthropic()
            if converted:
                content_blocks.append(converted)

        return content_blocks

    def replace_variables(self, variables: dict[str, Any]) -> None:
        """
        Replace variables in all TextContent items within this message.

        Args:
            variables: dict mapping variable names to their values
        """
        for content in self.content:
            if isinstance(content, TextContent):
                content.replace_variables(variables)

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format for database persistence (cx_message row).

        Returns dict with 'role', 'status', and 'content' (list of storage-format blocks).
        Content blocks use each item's to_storage_dict() for the cx_message.content JSONB.
        """
        content_storage_dicts = [c.to_storage_dict() for c in self.content]
        # vcprint(
        #     content_storage_dicts,
        #     "[UnifiedMessage] Content Storage Dicts",
        #     color="yellow",
        # )
        result: dict[str, Any] = {
            "role": self.role.value if hasattr(self.role, "value") else self.role,
            "content": content_storage_dicts,
        }
        if self.status != "active":
            result["status"] = self.status
        return result

    def get_output(self) -> str:
        """Get the output of the message."""
        output = ""
        for content in self.content:
            output += content.get_output()
        return output


@dataclass
class MessageList:
    """
    Wrapper for list[UnifiedMessage] that encapsulates message-related logic.

    Provides list-like interface for backward compatibility while adding
    helper methods for common message operations.

    Core Principle:
    - System/Developer messages are NEVER stored here in UnifiedConfig
    - System instructions live in UnifiedConfig.system_instruction field
    - Only during API conversion do we create system/developer messages
    """

    _messages: list["UnifiedMessage"] = field(default_factory=list)

    def __post_init__(self):
        """Normalize messages - convert dicts to UnifiedMessage objects."""
        normalized = []
        for msg in self._messages:
            if isinstance(msg, dict):
                normalized.append(UnifiedMessage.from_dict(msg))
            elif isinstance(msg, UnifiedMessage):
                normalized.append(msg)
            else:
                raise TypeError(f"Invalid message type: {type(msg)}")
        self._messages = normalized

    # ========================================================================
    # List Protocol Methods (for backward compatibility)
    # ========================================================================

    def __iter__(self):
        """Allow iteration: for msg in message_list"""
        return iter(self._messages)

    def __len__(self):
        """Allow len(): len(message_list)"""
        return len(self._messages)

    def __getitem__(self, index):
        """Allow indexing: message_list[0]"""
        return self._messages[index]

    def __setitem__(self, index, value):
        """Allow item assignment: message_list[0] = msg"""
        if isinstance(value, dict):
            value = UnifiedMessage.from_dict(value)
        self._messages[index] = value

    def append(self, message: Union["UnifiedMessage", dict[str, Any]]) -> None:
        """Append a message to the list"""
        if isinstance(message, dict):
            message = UnifiedMessage.from_dict(message)
        self._messages.append(message)

    def extend(self, messages: Union[list["UnifiedMessage"], "MessageList"]) -> None:
        """Extend with multiple messages"""
        if isinstance(messages, MessageList):
            self._messages.extend(messages._messages)
        else:
            for msg in messages:
                self.append(msg)

    def insert(
        self, index: int, message: Union["UnifiedMessage", dict[str, Any]]
    ) -> None:
        """Insert a message at a specific position"""
        if isinstance(message, dict):
            message = UnifiedMessage.from_dict(message)
        self._messages.insert(index, message)

    def pop(self, index: int = -1) -> "UnifiedMessage":
        """Remove and return a message at index (default last)"""
        return self._messages.pop(index)

    def remove(self, message: "UnifiedMessage") -> None:
        """Remove first occurrence of message"""
        self._messages.remove(message)

    def clear(self) -> None:
        """Remove all messages"""
        self._messages.clear()

    # ========================================================================
    # Helper Methods (new functionality)
    # ========================================================================

    def filter_by_role(self, *roles: str) -> "MessageList":
        """Return new MessageList with only messages matching the given roles."""
        filtered = [msg for msg in self._messages if msg.role in roles]
        return MessageList(_messages=filtered)

    def exclude_roles(self, *roles: str) -> "MessageList":
        """Return new MessageList excluding messages with given roles."""
        filtered = [msg for msg in self._messages if msg.role not in roles]
        return MessageList(_messages=filtered)

    def has_role(self, role: str) -> bool:
        """Check if any message has the given role."""
        return any(msg.role == role for msg in self._messages)

    def get_last_by_role(self, role: str) -> Optional["UnifiedMessage"]:
        """Get the last message with the given role, or None."""
        for msg in reversed(self._messages):
            if msg.role == role:
                return msg
        return None

    def get_last_output(self) -> str:
        """Get the output of the last assistant message."""
        last_assistant_message = self.get_last_by_role(Role.ASSISTANT)
        if last_assistant_message:
            return last_assistant_message.get_output()
        return ""

    def count_by_role(self, role: str) -> int:
        """Count messages with the given role."""
        return sum(1 for msg in self._messages if msg.role == role)

    def append_user_text(self, text: str, **kwargs) -> None:
        """
        Helper to append a simple user text message.

        Args:
            text: The text content
            **kwargs: Additional UnifiedMessage fields (id, name, timestamp, metadata)
        """
        user_message = UnifiedMessage(
            role=Role.USER, content=[TextContent(text=text)], **kwargs
        )
        self.append(user_message)

    def append_or_extend_user_text(self, text: str, **kwargs) -> None:
        """
        Add user text to the message list.

        If the last message is already a user message (not yet sent), append the text
        to the existing message with a line break.

        If the last message is not a user message, create a new user message.

        Args:
            text: The text content to add
            **kwargs: Additional UnifiedMessage fields (only used when creating new message)
        """
        if self._is_last_message_user():
            # Last message is user - append to existing text
            last_message = self._messages[-1]

            # Find the text content block and append
            for content in last_message.content:
                if isinstance(content, TextContent):
                    content.append_text(text)
                    break
        else:
            # Last message is not user (or no messages) - create new user message
            self.append_user_text(text, **kwargs)

    def append_or_extend_user_items(self, items: list[dict[str, Any]]) -> None:
        """
        items ex:
        [
            { "type": "input_text", "text": "what is in this image?" },
            { "type": "input_image", "image_url": "https://..." }
        ]

        """
        vcprint(items, "append_or_extend_user_input items", color="magenta")

        if self._is_last_message_user():
            # Last message is user - append to existing text
            last_message = self._messages[-1]
            text = ""
            items_without_text = []
            for item in items:
                if item["type"] == "input_text":
                    text += item["text"] + "\n"
                else:
                    items_without_text.append(item)
            if text:
                for content in last_message.content:
                    if isinstance(content, TextContent):
                        content.append_text(text)
                        break
            if items_without_text:
                last_message.content.extend(
                    UnifiedMessage.parse_content(items_without_text)
                )
        else:
            user_message = UnifiedMessage.from_dict(
                {
                    "role": Role.USER,
                    "content": items,
                }
            )
            self.append(user_message)

    def append_or_extend_user_input(
        self, user_input: str | list[dict[str, Any]]
    ) -> None:
        """
        Add user input to the message list.
        """
        if isinstance(user_input, str):
            self.append_or_extend_user_text(user_input)
        elif isinstance(user_input, list):
            self.append_or_extend_user_items(user_input)
        else:
            raise ValueError(f"Invalid user input type: {type(user_input)}")

    def _is_last_message_user(self) -> bool:
        """Check if the last message in the list is from a user."""
        if not self._messages:
            return False
        return self._messages[-1].role == Role.USER

    def append_assistant_text(self, text: str, **kwargs) -> None:
        """
        Helper to append a simple assistant text message.

        Args:
            text: The text content
            **kwargs: Additional UnifiedMessage fields (id, name, timestamp, metadata)
        """
        assistant_message = UnifiedMessage(
            role=Role.ASSISTANT, content=[TextContent(text=text)], **kwargs
        )
        self.append(assistant_message)

    def to_list(self) -> list["UnifiedMessage"]:
        """
        Get underlying list (for operations that need a raw list).
        Useful for spread operations: *message_list.to_list()
        """
        return self._messages

    def to_dict_list(self) -> list[dict[str, Any]]:
        """Convert all messages to dictionaries."""
        return [
            {
                "role": msg.role,
                "content": [
                    # Convert each content item to dict
                    {
                        k: v
                        for k, v in content.__dict__.items()
                        if v is not None and v != {} and v != []
                    }
                    for content in msg.content
                ],
                **({"id": msg.id} if msg.id else {}),
                **({"name": msg.name} if msg.name else {}),
                **({"timestamp": msg.timestamp} if msg.timestamp else {}),
                **({"metadata": msg.metadata} if msg.metadata else {}),
            }
            for msg in self._messages
        ]

    def replace_variables(self, variables: dict[str, Any]) -> None:
        """
        Replace variables in all messages.

        Args:
            variables: dict mapping variable names to their values
        """
        for message in self._messages:
            message.replace_variables(variables)
