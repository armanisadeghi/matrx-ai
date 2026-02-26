"""
Unified AI API Configuration System for OpenAI, Anthropic, and Google Gemini
Preserves ALL content types and metadata from all providers
"""

from __future__ import annotations
from dataclasses import dataclass, field, fields
from typing import Any, Literal, Optional, Union, cast, TYPE_CHECKING

if TYPE_CHECKING:
    from db.models import CxMessage
from google.genai.types import Part
from matrx_utils import vcprint
from openai.types.responses import (
    ResponseOutputItem as OpenAIResponseOutputItem,
)
from openai.types.responses import (
    ResponseOutputText as OpenAIResponseOutputText,
)
from openai.types.responses import (
    ResponseReasoningItem as OpenAIResponseReasoningItem,
)
from openai.types.responses import (
    ResponseFunctionToolCall as OpenAIResponseFunctionToolCall,
)
from openai.types.responses import (
    ResponseFunctionWebSearch as OpenAIResponseFunctionWebSearch,
)
from openai.types.responses import (
    ResponseOutputMessage as OpenAIResponseOutputMessage,
)

from config.extra_config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    WebSearchCallContent,
)
from config.media_config import (
    AudioContent,
    DocumentContent,
    ImageContent,
    VideoContent,
    YouTubeVideoContent,
    reconstruct_media_content,
)
from config.enums import Role
from config.tools_config import ToolCallContent, ToolResultContent
from prompts.instructions.system_instructions import SystemInstruction
from prompts.instructions.pattern_parser import resolve_matrx_patterns
from client.usage import TokenUsage


# ============================================================================
# CORE UNIFIED TYPES (Provider-Agnostic - Pure/Reusable)
# These types are completely independent of AI Matrix
# ============================================================================


@dataclass
class TextContent:
    type: Literal["text"] = "text"
    text: str = ""
    id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_output(self) -> str:
        """Get the output text of the content."""
        return self.text

    def replace_variables(self, variables: dict[str, Any]) -> None:
        """
        Replace variables in text content.
        Variables are in format {{variable_name}} in the text.

        Args:
            variables: dict mapping variable names to their values
        """
        for var_name, var_value in variables.items():
            self.text = self.text.replace(f"{{{{{var_name}}}}}", str(var_value))

    def append_text(self, text: str, separator: str = "\n") -> None:
        """
        Append text to existing content.

        Args:
            text: The text to append
            separator: Separator between existing and new text (default: newline)
        """
        self.text += f"{separator}{text}"

    def to_google(self) -> dict[str, Any]:
        """Convert to Google Gemini format"""
        part = {"text": self.text}
        # Retrieve Google's thought signature from metadata if present
        if "google_thought_signature" in self.metadata:
            part["thoughtSignature"] = self.metadata["google_thought_signature"]
        return part

    def to_openai(self, role: Optional[str] = None) -> dict[str, Any]:
        """Convert to OpenAI format"""
        # Assistant messages use output_text, all others use input_text
        text_type = "output_text" if role == "assistant" else "input_text"
        return {"type": text_type, "text": self.text}

    def to_anthropic(self) -> dict[str, Any]:
        """Convert to Anthropic format"""
        return {"type": "text", "text": self.text}

    def _sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Sanitize metadata by replacing sensitive encrypted content with length information.

        Replaces these fields with their lengths:
        - anthropic_signature: str
        - google_thought_signature: bytes
        - encrypted_content: bytes
        """
        sanitized = metadata.copy()

        # Replace sensitive fields with length info
        if "anthropic_signature" in sanitized:
            sanitized["anthropic_signature"] = (
                f"<str length={len(sanitized['anthropic_signature'])}>"
            )

        if "google_thought_signature" in sanitized:
            sanitized["google_thought_signature"] = (
                f"<bytes length={len(sanitized['google_thought_signature'])}>"
            )

        if "encrypted_content" in sanitized:
            sanitized["encrypted_content"] = (
                f"<bytes length={len(sanitized['encrypted_content'])}>"
            )

        return sanitized

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary with sanitized metadata.
        Use this instead of dataclasses.asdict() to avoid printing sensitive encrypted content.
        """
        return {
            "type": self.type,
            "text": self.text,
            "id": self.id,
            "metadata": self._sanitize_metadata(self.metadata),
        }

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format for database persistence (cx_message.content JSONB)."""
        result: dict[str, Any] = {"type": "text", "text": self.text}
        if self.id:
            result["id"] = self.id
        citations = self.metadata.get("citations")
        if citations:
            result["citations"] = citations
        return result

    def __repr__(self) -> str:
        """Override repr to show sanitized metadata instead of full encrypted content"""
        sanitized_metadata = self._sanitize_metadata(self.metadata)

        # Show first 35 and last 35 characters with ... in the middle
        if len(self.text) > 70:
            text_preview = f"{self.text[:35]}...{self.text[-35:]}"
        else:
            text_preview = self.text

        return (
            f"TextContent(type={self.type!r}, "
            f"text={text_preview!r}, "
            f"id={self.id!r}, "
            f"metadata={sanitized_metadata!r})"
        )

    @classmethod
    def from_openai(
        cls, content_item: OpenAIResponseOutputText, id: str
    ) -> Optional["TextContent"]:
        text = content_item.text
        metadata = content_item.model_dump(exclude={"text", "id"})

        return cls(
            text=text,
            metadata=metadata,
        )

    @classmethod
    def from_google(cls, part: Part) -> Optional["TextContent"]:
        """Create TextContent from Google Part object"""
        metadata = {}
        # Store Google's thought signature in metadata if present
        if part.thought_signature:
            metadata["google_thought_signature"] = part.thought_signature
        return cls(
            text=part.text if part.text is not None else "",
            metadata=metadata,
        )

    @classmethod
    def from_anthropic(cls, content_block: dict[str, Any]) -> Optional["TextContent"]:
        """Create TextContent from Anthropic content block"""
        metadata = {}
        citations = content_block.get("citations", [])
        if citations:
            metadata["citations"] = citations
        return cls(
            text=content_block["text"],
            metadata=metadata,
        )


@dataclass
class ThinkingContent:
    """
    Extended thinking content with normalized provider identification.

    Normalization:
    - provider: Explicitly identifies which AI provider generated this content
    - signature: Unified field for provider-specific encrypted/signature data
      (OpenAI's encrypted_content, Anthropic's signature, Google's thought_signature)

    Each provider can only process its own signature data. The to_* methods
    check the provider field and only include signature if it matches.
    """

    type: Literal["thinking"] = "thinking"
    text: str = ""
    id: str = ""
    summary: list[dict[str, Any]] = field(default_factory=list)

    # Normalized fields for database storage
    provider: Optional[Literal["openai", "anthropic", "google", "cerebras"]] = None
    signature: Optional[Union[str, bytes]] = (
        None  # Provider-specific encrypted/signature data
    )

    # metadata for truly optional/non-essential data only
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_output(self) -> str:
        text_output = ""
        if self.text:
            text_output += self.text
        if self.summary:
            text_output += "\n".join([item["text"] for item in self.summary])
        return text_output

    def _sanitize_signature(self) -> str:
        """Return a sanitized representation of the signature for display."""
        if self.signature is None:
            return "None"
        if isinstance(self.signature, bytes):
            return f"<bytes length={len(self.signature)}>"
        return f"<str length={len(self.signature)}>"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary with sanitized signature.
        Use this instead of dataclasses.asdict() to avoid printing sensitive encrypted content.
        """
        result = {
            "type": self.type,
            "text": self.text,
            "id": self.id,
            "summary": self.summary,
            "provider": self.provider,
            "signature": self.signature,
        }
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format for database persistence (cx_message.content JSONB)."""
        import base64

        result: dict[str, Any] = {
            "type": "thinking",
            "text": self.text,
            "provider": self.provider,
        }
        if self.signature:
            # Signature can be bytes (from providers) — base64-encode for JSONB storage
            if isinstance(self.signature, bytes):
                result["signature"] = base64.b64encode(self.signature).decode("ascii")
                result["signature_encoding"] = "base64"
            else:
                result["signature"] = self.signature
        if self.summary:
            result["summary"] = self.summary
        if self.id:
            result["id"] = self.id
        return result

    def __repr__(self) -> str:
        """Override repr to show sanitized signature instead of full encrypted content"""
        # Show first 35 and last 35 characters with ... in the middle
        if len(self.text) > 70:
            text_preview = f"{self.text[:35]}...{self.text[-35:]}"
        else:
            text_preview = self.text

        return (
            f"ThinkingContent(type={self.type!r}, "
            f"text={text_preview!r}, "
            f"id={self.id!r}, "
            f"summary={self.summary!r}, "
            f"provider={self.provider!r}, "
            f"signature={self._sanitize_signature()})"
        )

    def to_google(self) -> Optional[dict[str, Any]]:
        """Convert to Google Gemini format. Only includes signature if provider is Google."""
        # Only include signature if this content came from Google
        if self.provider != "google" or self.signature is None:
            return None

        part = {"text": self.text, "thought": True}
        part["thoughtSignature"] = self.signature
        return part

    def to_openai(self) -> Optional[dict[str, Any]]:
        """Convert to OpenAI format. Only includes signature if provider is OpenAI."""
        # Only include encrypted_content if this content came from OpenAI
        if self.provider != "openai" or self.signature is None:
            return None

        return {
            "id": self.id,
            "summary": self.summary,
            "type": "reasoning",
            "encrypted_content": self.signature,
        }

    def to_anthropic(self) -> Optional[dict[str, Any]]:
        """
        Convert to Anthropic format. Only includes signature if provider is Anthropic.
        Returns None if signature is missing (Anthropic requires signature for thinking).
        """
        # Only include signature if this content came from Anthropic
        if self.provider != "anthropic" or self.signature is None:
            return None

        result = {
            "type": "thinking",
            "thinking": self.text,
            "signature": self.signature,
        }

        if self.summary:
            result["summary"] = self.summary

        return result

    @classmethod
    def from_google(cls, part: Part) -> Optional["ThinkingContent"]:
        """Create ThinkingContent from Google Part object"""
        # vcprint(part, "Google Part", color="yellow")
        return cls(
            text=part.text or "",
            provider="google",
            signature=part.thought_signature if part.thought_signature else None,
        )

    @classmethod
    def from_anthropic(
        cls, content_block: dict[str, Any]
    ) -> Optional["ThinkingContent"]:
        """Create ThinkingContent from Anthropic content block"""
        return cls(
            text=content_block["thinking"],
            provider="anthropic",
            signature=content_block.get("signature"),
        )

    @classmethod
    def from_openai(
        cls, item: OpenAIResponseReasoningItem
    ) -> Optional["ThinkingContent"]:
        """Create ThinkingContent from OpenAI reasoning item"""
        # Extract encrypted_content from the item
        encrypted_content = getattr(item, "encrypted_content", None)

        return cls(
            summary=[s.model_dump() for s in item.summary],
            id=item.id,
            provider="openai",
            signature=encrypted_content,
        )


# Union of all content types
UnifiedContent = Union[
    TextContent,
    ImageContent,
    AudioContent,
    VideoContent,
    YouTubeVideoContent,
    DocumentContent,
    ToolCallContent,
    ToolResultContent,
    ThinkingContent,
    CodeExecutionContent,
    CodeExecutionResultContent,
    WebSearchCallContent,
]


def reconstruct_content(block: dict[str, Any]) -> UnifiedContent:
    """
    Reconstruct a content object from a stored JSONB block (cx_message.content).

    This is the deserialization counterpart to each content class's to_storage_dict() method.
    Handles all storage block types: text, thinking, media, tool_call, tool_result,
    code_exec, code_result, web_search.

    Args:
        block: A dict from the cx_message.content JSONB array with a 'type' discriminator.

    Returns:
        The appropriate UnifiedContent instance.
    """
    block_type = block.get("type", "text")

    if block_type == "text":
        metadata: dict[str, Any] = {}
        citations = block.get("citations")
        if citations:
            metadata["citations"] = citations
        return TextContent(
            text=block.get("text", ""),
            id=block.get("id", ""),
            metadata=metadata,
        )

    elif block_type == "thinking":
        import base64

        sig = block.get("signature")
        if sig and block.get("signature_encoding") == "base64":
            sig = base64.b64decode(sig)
        return ThinkingContent(
            text=block.get("text", ""),
            provider=block.get("provider"),
            signature=sig,
            summary=block.get("summary", []),
            id=block.get("id", ""),
        )

    elif block_type == "media":
        result = reconstruct_media_content(block)
        if result is not None:
            return result
        return TextContent(text=f"[Unknown media kind: {block.get('kind')}]")

    elif block_type == "tool_call":
        return ToolCallContent(
            id=block.get("id", ""),
            call_id=block.get("call_id", ""),
            name=block.get("name", ""),
            arguments=block.get("arguments", {}),
        )

    elif block_type == "tool_result":
        return ToolResultContent(
            tool_use_id=block.get("tool_use_id", ""),
            call_id=block.get("call_id", ""),
            name=block.get("name", ""),
            content=block.get("content", ""),
            is_error=block.get("is_error", False),
        )

    elif block_type == "code_exec":
        return CodeExecutionContent(
            language=block.get("language", ""),
            code=block.get("code", ""),
        )

    elif block_type == "code_result":
        return CodeExecutionResultContent(
            output=block.get("output", ""),
            outcome=block.get("outcome", ""),
        )

    elif block_type == "web_search":
        meta = block.get("metadata", {})
        return WebSearchCallContent(
            id=block.get("id", ""),
            status=block.get("status", ""),
            action=meta.get("action", {}),
        )

    # Fallback: return as TextContent with warning
    vcprint(block, f"WARNING: Unknown storage block type: {block_type}", color="red")
    return TextContent(text=f"[Unknown block type: {block_type}]")


@dataclass
class UnifiedMessage:
    """Pure message - no AI Matrix specifics"""

    role: str
    content: list[UnifiedContent] = field(default_factory=list)
    id: Optional[str] = None
    name: Optional[str] = None
    timestamp: Optional[int] = None
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
    def from_cx_message(cls, message: "CxMessage") -> "UnifiedMessage":
        content = []
        for item in message.content:
            item = reconstruct_content(item)
            content.append(item)

        return cls(
            role=message.role,
            content=content,
            id=message.id,
            timestamp=message.created_at.isoformat(),
            status=message.status,
            metadata=message.metadata,
        )

    @classmethod
    def from_openai_item(
        cls, item: OpenAIResponseOutputItem
    ) -> Optional["UnifiedMessage"]:
        content: list[UnifiedContent] = []
        assigned_role = "output"

        item_type = item.type
        if item_type == "message":
            assigned_role = "assistant"
            message_item = cast(OpenAIResponseOutputMessage, item)
            for content_item in message_item.content:
                content_type = content_item.type
                if content_type == "output_text":
                    text_content = TextContent.from_openai(cast(OpenAIResponseOutputText, content_item), message_item.id)
                    if text_content is not None:
                        content.append(text_content)
                else:
                    vcprint(
                        content_item,
                        f"WARNING: Unknown OpenAI content item type: {content_type}",
                        color="yellow",
                    )
        elif item_type == "reasoning":
            thinking_content = ThinkingContent.from_openai(cast(OpenAIResponseReasoningItem, item))
            if thinking_content is not None:
                content.append(thinking_content)
        elif item_type == "function_call":
            assigned_role = "tool"
            tool_content = ToolCallContent.from_openai(cast(OpenAIResponseFunctionToolCall, item))
            if tool_content is not None:
                content.append(tool_content)
        elif item_type == "web_search_call":
            assigned_role = "tool"
            web_content = WebSearchCallContent.from_openai(cast(OpenAIResponseFunctionWebSearch, item))
            if web_content is not None:
                content.append(web_content)
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
        content_blocks: list[UnifiedContent] = []

        for block in content:
            block_type = block.get("type")
            if block_type == "text":
                text_content = TextContent.from_anthropic(block)
                if text_content is not None:
                    content_blocks.append(text_content)
            elif block_type == "tool_use":
                tool_content = ToolCallContent.from_anthropic(block)
                if tool_content is not None:
                    content_blocks.append(tool_content)
            elif block_type == "thinking":
                thinking_content = ThinkingContent.from_anthropic(block)
                if thinking_content is not None:
                    content_blocks.append(thinking_content)
            else:
                vcprint(
                    block,
                    "WARNING: Unknown Anthropic content block type",
                    color="yellow",
                )

        return cls(role=role, content=content_blocks, id=id)

    def to_google_content(self) -> Optional[dict[str, Any]]:
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

    def to_openai_items(self) -> list[dict[str, Any]] | dict[str, Any] | None:
        """
        Convert message to OpenAI Responses API format items.

        Returns a list because:
        - Tool calls become separate function_call items
        - Thinking becomes separate reasoning items
        - Tool results become function_call_output items
        - Regular messages stay as message items
        """

        converted = []
        for content in self.content:
            result = None
            if isinstance(content, TextContent):
                result = content.to_openai(role=self.role)
            else:
                result = content.to_openai()

            if result is not None:
                converted.append(result)

        if converted and self.role in (Role.OUTPUT, Role.TOOL):
            return converted  # Returns list: [item1, item2, item3] & without role, etc.

        elif converted:
            return {"role": self.role, "content": converted}
        else:
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
        result: dict[str, Any] = {
            "role": getattr(self.role, "value", self.role),
            "content": [c.to_storage_dict() for c in self.content],
        }
        if self.status != "active":
            result["status"] = self.status
        return result

    def get_output(self) -> str:
        """Get the output of the message."""
        output = ""
        for content in self.content:
            output += getattr(content, "get_output", lambda: "")()
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
    messages: Union[MessageList, list[UnifiedMessage], list[dict[str, Any]]]
    system_instruction: Optional[Union[str, dict, SystemInstruction]] = None
    stream: bool = False

    max_output_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None

    tools: list = field(default_factory=list)
    # Literal["none", "auto", "required"]
    tool_choice: Optional[Literal["none", "auto", "required"]] = None
    parallel_tool_calls: bool = True

    # OpenAI thinking format
    reasoning_effort: Optional[
        Literal["auto", "none", "minimal", "low", "medium", "high", "xhigh"]
    ] = None
    reasoning_summary: Optional[Literal["concise", "detailed", "never", "auto", "always"]] = None

    # Google Gemini 3 thinking format
    thinking_level: Optional[Literal["minimal", "low", "medium", "high"]] = None
    include_thoughts: Optional[bool] = None

    # Anthropic thinking & legacy Google Gemini 2 thinking format
    thinking_budget: Optional[int] = None

    response_format: Optional[dict[str, Any]] = None
    stop_sequences: list = field(default_factory=list)

    store: Optional[bool] = None
    verbosity: Optional[str] = None

    # Media/attachment settings
    internal_web_search: Optional[bool] = None
    internal_url_context: Optional[bool] = None

    # Image generation settings
    size: Optional[str] = None
    quality: Optional[str] = None
    count: int = 1

    # Audio settings
    audio_voice: Optional[str] = None
    audio_format: Optional[str] = None

    # Video generation settings
    seconds: Optional[str] = None
    fps: Optional[int] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    guidance_scale: Optional[int] = None
    output_quality: Optional[int] = None
    negative_prompt: Optional[str] = None
    output_format: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    frame_images: Optional[list] = None
    reference_images: Optional[list] = None
    disable_safety_checker: Optional[bool] = None

    custom_configs: Optional[dict[str, Any]] = None
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
                self.messages = MessageList(_messages=cast(list[UnifiedMessage], self.messages))
            else:
                raise TypeError(
                    f"messages must be MessageList or list, got {type(self.messages)}"
                )

        self.tool_choice = self._normalize_tool_choice(self.tool_choice)
        self.system_instruction = self._resolve_system_instruction(self.system_instruction)
        self._resolve_message_patterns()

    @property
    def _message_list(self) -> MessageList:
        """Type-narrowed accessor for self.messages post __post_init__ conversion."""
        return cast(MessageList, self.messages)

    def _resolve_message_patterns(self) -> None:
        """Resolve <<MATRX>> data-fetch patterns in all TextContent across messages."""
        for message in self._message_list:
            for content in message.content:
                if isinstance(content, TextContent) and content.text:
                    content.text = resolve_matrx_patterns(content.text)

    @staticmethod
    def _resolve_system_instruction(
        raw: Optional[Union[str, dict, SystemInstruction]],
    ) -> Optional[str]:
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
                unrecognized_keys, "Unrecognized keys in UnifiedConfig (likely expected, but confirm if update is needed on client side or our server side code)", color="red"
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
    ) -> Optional[Literal["none", "auto", "required"]]:
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
                result[key] = [getattr(item, "to_dict")() for item in value]
            elif hasattr(value, "to_dict"):
                result[key] = getattr(value, "to_dict")()
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
        # Top-level columns
        result: dict[str, Any] = {
            "model": self.model,
            "system_instruction": self.system_instruction,
            "messages": [msg.to_storage_dict() for msg in self._message_list],
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
        self._message_list.append_user_text(text, **kwargs)

    def append_or_extend_user_text(self, text: str, **kwargs) -> None:
        """
        Add user text to the message list.
        """
        self._message_list.append_or_extend_user_text(text, **kwargs)

    def append_or_extend_user_input(
        self, user_input: str | list[dict[str, Any]]
    ) -> None:
        """
        Add user input items to the message list.
        """
        self._message_list.append_or_extend_user_input(user_input)

    def replace_variables(self, variables: dict[str, Any]) -> None:
        """
        Replace variables throughout the config.
        Handles both system_instruction and all messages.

        Args:
            variables: dict mapping variable names to their values
        """
        # Replace in system_instruction
        if isinstance(self.system_instruction, str):
            for var_name, var_value in variables.items():
                self.system_instruction = self.system_instruction.replace(
                    f"{{{{{var_name}}}}}", str(var_value)
                )

        # Replace in all messages
        self._message_list.replace_variables(variables)

    def get_last_output(self) -> str:
        """Get the output of the last assistant message."""
        return self._message_list.get_last_output()


@dataclass
class UnifiedResponse:
    """Pure LLM response - no AI Matrix specifics"""

    messages: list[UnifiedMessage]
    usage: Optional[TokenUsage] = None
    stop_reason: Optional[str] = None
    finish_reason: Optional[str] = None
    raw_response: Optional[dict[str, Any]] = None
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
                result[key] = [getattr(item, "to_dict")() for item in value]
            elif hasattr(value, "to_dict"):
                result[key] = getattr(value, "to_dict")()
            else:
                result[key] = value

        return result
