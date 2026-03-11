import json
from dataclasses import dataclass, field
from typing import Any, Literal, Optional

from google.genai.types import Part


@dataclass
class ToolCallContent:
    type: Literal["tool_call", "function_call"] = "tool_call"
    id: str = ""
    call_id: str = ""
    name: str = ""
    arguments: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    from openai.types.responses import (
        ResponseFunctionToolCall as OpenAIResponseFunctionToolCall,
    )

    def get_output(self) -> str:
        """Get the output of the tool call."""
        string_data = json.dumps(self)
        return string_data

    def to_google(self) -> dict[str, Any]:
        """Convert to Google Gemini format"""
        part = {
            "functionCall": {
                "name": self.name,
                "args": self.arguments,
            }
        }
        # thoughtSignature must be at Part level, not inside functionCall
        # Retrieve Google's thought signature from metadata if present
        if "google_thought_signature" in self.metadata:
            part["thoughtSignature"] = self.metadata["google_thought_signature"]
        return part

    def to_openai(self) -> dict[str, Any]:
        """Convert to OpenAI format"""
        return {
            "type": "function_call",
            "id": self.id,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": json.dumps(self.arguments),
        }

    def to_anthropic(self) -> dict[str, Any]:
        """Convert to Anthropic format"""
        return {
            "type": "tool_use",
            "id": self.id,
            "name": self.name,
            "input": self.arguments,
        }

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
            "id": self.id,
            "call_id": self.call_id,
            "name": self.name,
            "arguments": self.arguments,
            "metadata": self._sanitize_metadata(self.metadata),
        }

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format for database persistence (cx_message.content JSONB)."""
        result: dict[str, Any] = {
            "type": "tool_call",
            "name": self.name,
            "arguments": self.arguments,
        }
        if self.id:
            result["id"] = self.id
        if self.call_id:
            result["call_id"] = self.call_id
        return result

    def __repr__(self) -> str:
        """Override repr to show sanitized metadata instead of full encrypted content"""
        sanitized_metadata = self._sanitize_metadata(self.metadata)

        # Truncate arguments JSON if too long
        args_str = json.dumps(self.arguments)
        if len(args_str) > 70:
            args_preview = f"{args_str[:35]}...{args_str[-35:]}"
        else:
            args_preview = args_str

        return (
            f"ToolCallContent(type={self.type!r}, "
            f"id={self.id!r}, "
            f"call_id={self.call_id!r}, "
            f"name={self.name!r}, "
            f"arguments={args_preview}, "
            f"metadata={sanitized_metadata!r})"
        )

    @classmethod
    def from_google(cls, part: Part) -> Optional["ToolCallContent"]:
        """Create ToolCallContent from Google Part object"""
        if hasattr(part, "function_call") and part.function_call:
            metadata = {}
            # Store Google's thought signature in metadata if present
            if part.thought_signature:
                metadata["google_thought_signature"] = part.thought_signature
            return cls(
                id=f"gemini_{hash(part.function_call.name)}",
                name=part.function_call.name,
                arguments=part.function_call.args or {},
                metadata=metadata,
            )
        return None

    @classmethod
    def from_openai(
        cls, item: OpenAIResponseFunctionToolCall
    ) -> Optional["ToolCallContent"]:
        """Create ToolCallContent from OpenAI item"""
        # Ensure arguments is always a dict, not a JSON string
        args = item.arguments
        if isinstance(args, str):
            args = json.loads(args)

        return cls(
            id=item.id,
            call_id=item.call_id,
            name=item.name,
            arguments=args,
            metadata=item.model_dump(exclude={"id", "call_id", "name", "arguments"}),
        )

    @classmethod
    def from_anthropic(
        cls, content_block: dict[str, Any]
    ) -> Optional["ToolCallContent"]:
        """Create ToolCallContent from Anthropic content block"""
        return cls(
            id=content_block["id"],
            name=content_block["name"],
            arguments=content_block["input"],
        )


@dataclass
class ToolResultContent:
    type: Literal["tool_result"] = "tool_result"
    tool_use_id: str = ""
    call_id: str = ""  # OpenAI-specific call_id (different from tool_use_id)
    name: str = ""
    content: list[dict[str, Any]] = field(default_factory=list)
    is_error: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_output(self) -> str:
        """Get the output of the tool result."""
        string_data = json.dumps(self)
        return string_data

    def to_google(self) -> dict[str, Any]:
        """Convert to Google Gemini format.

        Google API requires functionResponse.response to be a dictionary.
        The content field can be various types due to backwards compatibility,
        so we normalize it here.
        """
        # Normalize content to a dictionary format for Google
        if isinstance(self.content, dict):
            # Already a dict - use directly
            response_data = self.content
        elif isinstance(self.content, str):
            # String content - wrap in result key
            response_data = {"result": self.content}
        elif isinstance(self.content, list):
            # list content - could be list of dicts or other data
            # Wrap it in a result key to make it a valid dict
            response_data = {"items": self.content} if self.content else {"result": ""}
        else:
            # Fallback for any other type
            response_data = {"result": str(self.content) if self.content else ""}

        return {
            "functionResponse": {
                "name": self.name,
                "response": response_data,
            }
        }

    def to_openai(self) -> dict[str, Any]:
        """Convert to OpenAI Responses API format (function_call_output)"""
        # OpenAI Responses API requires function_call_output items with JSON string output
        output_str = self.content
        if isinstance(output_str, (dict, list)):
            output_str = json.dumps(output_str)
        elif not isinstance(output_str, str):
            output_str = str(output_str)

        return {
            "type": "function_call_output",
            "call_id": self.call_id,
            "output": output_str,
        }

    def to_anthropic(self) -> dict[str, Any]:
        """Convert to Anthropic format"""
        result = {
            "type": "tool_result",
            "tool_use_id": self.tool_use_id,
            "content": json.dumps(self.content)
            if not isinstance(self.content, str)
            else self.content,
        }
        if self.is_error:
            result["is_error"] = True
        return result

    def to_storage_dict(self) -> dict[str, Any]:
        """Serialize to storage format for database persistence (cx_message.content JSONB)."""
        result: dict[str, Any] = {
            "type": "tool_result",
            "name": self.name,
            "content": self.content,
        }
        if self.tool_use_id:
            result["tool_use_id"] = self.tool_use_id
        if self.call_id:
            result["call_id"] = self.call_id
        if self.is_error:
            result["is_error"] = True
        return result

    @classmethod
    def from_google(cls, part: Part) -> Optional["ToolResultContent"]:
        """Create ToolResultContent from Google Part object"""
        if hasattr(part, "function_response") and part.function_response:
            return cls(
                tool_use_id="",
                name=part.function_response.name or "",
                content=part.function_response.response or [],
            )
        return None
