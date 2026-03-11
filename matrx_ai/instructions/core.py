from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from .content_blocks_manager import get_content_blocks_manager
from .pattern_parser import resolve_matrx_patterns


@dataclass
class SystemInstruction:
    """
    Flexible system instruction builder with optional components.
    Always returns a string when converted.
    """

    base_instruction: str
    intro: str = field(default_factory=str)
    outro: str = field(default_factory=str)
    append_sections: list[str] = field(default_factory=list)
    prepend_sections: list[str] = field(default_factory=list)
    content_blocks: list[str] = field(default_factory=list)
    tools_list: list[str] = field(default_factory=list)

    # Optional flags for built-in sections
    include_date: bool = True
    include_code_guidelines: bool = False
    include_safety_guidelines: bool = False

    # Custom metadata (not rendered, just for tracking)
    version: str | None = None
    category: str | None = None

    # Internal cache for fetched content blocks
    _content_blocks_cache: list[str] = field(
        default_factory=list, init=False, repr=False
    )

    async def load_content_blocks(self) -> SystemInstruction:
        """
        Fetch and cache content blocks from database.
        Call this before converting to string if you need content blocks.
        Returns self for chaining.
        """
        if self.content_blocks and not self._content_blocks_cache:
            manager = get_content_blocks_manager()
            for block_id in self.content_blocks:
                block_text = await manager.get_template_text(block_id)
                if block_text:
                    self._content_blocks_cache.append(block_text)
        return self

    def __str__(self) -> str:
        """Convert to final system instruction string"""
        parts = []

        # Always at the start
        if self.intro:
            parts.append(self.intro)

        # Date
        if self.include_date:
            parts.append(f"Current date: {datetime.now().strftime('%Y-%m-%d')}")

        # Prepended sections first
        if self.prepend_sections:
            parts.extend(self.prepend_sections)

        # Base instruction (required)
        parts.append(self.base_instruction)

        # Optional built-in sections (after base)
        if self.tools_list:
            parts.append(self._tools_available(self.tools_list))

        if self.include_code_guidelines:
            parts.append(self._code_guidelines())

        if self.include_safety_guidelines:
            parts.append(self._safety_guidelines())

        # Add cached content blocks (if loaded)
        if self._content_blocks_cache:
            parts.extend(self._content_blocks_cache)

        # Appended sections last
        if self.append_sections:
            parts.extend(self.append_sections)

        if self.outro:
            parts.append(self.outro)

        result = "\n\n".join(filter(None, parts))

        # Resolve any <<MATRX>> data-fetch patterns in the final string
        return resolve_matrx_patterns(result)

    @staticmethod
    def _tools_available(tools_list: list[str]) -> str:
        tools_List_string = "\n  * ".join(tools_list) if tools_list else ""
        return f"""## Tools/Functions Available
- You have the following tools available to you:
  * {tools_List_string}
  
- Utilize these tools ONLY if they will help you better handle the user's request.
- If a tool repeatedly fails to give you the expected result, stop using it and move to a different approach."""

    @staticmethod
    def _code_guidelines() -> str:
        return """## Code Guidelines
- Use TypeScript with strict typing
- Follow React 19 best practices
- Prefer functional components with hooks"""

    @staticmethod
    def _safety_guidelines() -> str:
        return """## Safety Guidelines
- Never expose sensitive credentials
- Validate all user inputs
- Follow security best practices"""

    def to_string(self) -> str:
        """Explicit conversion method (alternative to __str__)"""
        return str(self)

    @classmethod
    def from_value(cls, value: str | dict | SystemInstruction) -> SystemInstruction:
        """
        Single entry point to create a SystemInstruction from any supported input.

        - str: Treated as base_instruction. All defaults apply (include_date=True, etc.).
        - dict: Keys map to constructor args. "content" is accepted as an alias for
          "base_instruction". All unrecognized keys are ignored.
        - SystemInstruction: Returned as-is.

        This is the sync path used by UnifiedConfig.__post_init__. For async
        content_blocks loading, use from_dict() instead.
        """
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            return cls(base_instruction=value)

        if isinstance(value, dict):
            base_instruction = value.get("base_instruction", "")
            content = value.get("content", "")
            if content:
                if base_instruction:
                    base_instruction = f"{base_instruction}\n\n{content}"
                else:
                    base_instruction = content

            return cls(
                base_instruction=base_instruction,
                intro=value.get("intro", ""),
                outro=value.get("outro", ""),
                append_sections=value.get("append_sections", []),
                prepend_sections=value.get("prepend_sections", []),
                content_blocks=value.get("content_blocks", []),
                tools_list=value.get("tools_list", []),
                include_date=value.get("include_date", True),
                include_code_guidelines=value.get("include_code_guidelines", False),
                include_safety_guidelines=value.get("include_safety_guidelines", False),
                version=value.get("version"),
                category=value.get("category"),
            )

        raise TypeError(f"Cannot create SystemInstruction from {type(value)}")

    @classmethod
    async def from_dict(cls, data: dict) -> SystemInstruction:
        """
        Create a SystemInstruction from a dict and load content blocks (async).

        Delegates dict parsing to from_value(), then awaits content_blocks loading.
        Use this when the dict may contain content_blocks that require DB fetches.
        """
        # Handle legacy traditional format: {"role": "system", "content": "..."}
        if "role" in data and "content" in data and "base_instruction" not in data:
            if "intro" in data:
                data = {**data, "base_instruction": data["content"]}
            else:
                data = {**data, "base_instruction": "", "intro": data["content"]}
            data.pop("role", None)

        instance = cls.from_value(data)
        await instance.load_content_blocks()
        return instance

    @classmethod
    def for_code_review(cls, language: str = "TypeScript") -> SystemInstruction:
        return cls(
            base_instruction=f"You are an expert {language} code reviewer",
            include_code_guidelines=True,
            include_safety_guidelines=True,
            category="code-review",
        )

    @classmethod
    def for_ai_matrix(cls, additional_context: str = "") -> SystemInstruction:
        return cls(
            intro="You are 'AI MATRX Assistant'. The most advanced & intelligent assistant in the universe.",
            base_instruction="You are able to solve any problem, answer any question, and help with any task. Even though your knowledge cutoff may be months or years ago, you know today's date.",
            append_sections=[additional_context] if additional_context else [],
            outro="Always think about the user's request carefully and identify what they really want and then think through the best possible response.",
        )
