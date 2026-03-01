# ============================================================================
# ENUMS AND CONSTANTS

# Tasks:
# - Content Type is unused - use it or remove it.
# - Provider is unused - use it or remove it.

# ============================================================================


from enum import Enum


class Role(str, Enum):
    SYSTEM = "system"
    DEVELOPER = "developer"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"  # For OpenAI tool results
    OUTPUT = "output"

    def __str__(self) -> str:
        return self.value


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"
    YOUTUBE_VIDEO = "youtube_video"
    MEDIA = "media"  # Unified storage format with kind discriminator
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    THINKING = "thinking"
    CODE_EXECUTION = "code_execution"
    CODE_EXECUTION_RESULT = "code_execution_result"
    EXECUTABLE_CODE = "executable_code"

    def __str__(self) -> str:
        return self.value


class Provider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    XAI = "xai"
    TOGETHER = "together"
    GROQ = "groq"
    CEREBRAS = "cerebras"
    OLLAMA = "ollama"

    def __str__(self) -> str:
        return self.value
