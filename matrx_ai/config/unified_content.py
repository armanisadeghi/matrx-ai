from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from google.genai.types import Part
from matrx_utils import vcprint
from openai.types.responses import (
    ResponseOutputText as OpenAIResponseOutputText,
)
from openai.types.responses import (
    ResponseReasoningItem as OpenAIResponseReasoningItem,
)

from matrx_ai.config.extra_config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    WebSearchCallContent,
)
from matrx_ai.config.media_config import (
    AudioContent,
    DocumentContent,
    ImageContent,
    VideoContent,
    YouTubeVideoContent,
    reconstruct_media_content,
)

from .tools_config import ToolCallContent, ToolResultContent

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

    def to_openai(self, role: str | None = None) -> dict[str, Any]:
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
        metadata = content_item.model_dump(exclude={"text"})
        metadata["id"] = id

        return cls(
            id=id,
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
            text=part.text,
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
    provider: Literal["openai", "anthropic", "google", "cerebras"] | None = None
    signature: str | bytes | None = (
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
            "metadata": self.metadata,
        }

        if self.signature:
            # Signature can be bytes (from providers) — base64-encode for JSONB storage
            if isinstance(self.signature, bytes):
                result["signature"] = base64.b64encode(self.signature).decode("ascii")
                result["signature_encoding"] = "base64"
            else:
                result["signature"] = self.signature

        if self.summary:
            # summary items may be Pydantic models (e.g. OpenAI Summary) or plain dicts
            result["summary"] = [
                item.model_dump() if hasattr(item, "model_dump") else item
                for item in self.summary
            ]

        if self.id:
            result["metadata"]["id"] = self.id

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

    def to_google(self) -> dict[str, Any] | None:
        """Convert to Google Gemini format. Only includes signature if provider is Google."""
        # Only include signature if this content came from Google
        if self.provider != "google" or self.signature is None:
            return None

        part = {"text": self.text, "thought": True}
        part["thoughtSignature"] = self.signature
        return part

    def to_openai(self) -> dict[str, Any] | None:
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

    def to_anthropic(self) -> dict[str, Any] | None:
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
            summary=item.summary,
            id=item.id,
            provider="openai",
            signature=encrypted_content,
        )


# Union of all content types
UnifiedContent = (
    TextContent
    | ImageContent
    | AudioContent
    | VideoContent
    | YouTubeVideoContent
    | DocumentContent
    | ToolCallContent
    | ToolResultContent
    | ThinkingContent
    | CodeExecutionContent
    | CodeExecutionResultContent
    | WebSearchCallContent
)


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

        id_from_metadata = block.get("metadata", {}).get("id")
        return ThinkingContent(
            text=block.get("text", ""),
            provider=block.get("provider"),
            signature=sig,
            summary=block.get("summary", []),
            id=id_from_metadata or block.get("id", ""),
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
