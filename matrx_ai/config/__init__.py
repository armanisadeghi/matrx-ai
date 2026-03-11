# ============================================================================
# ai/config — Public API
#
# Import strategy to prevent circular imports:
#
# Tier 1 (pure leaves — no local deps, safe to import anywhere):
#   enums, finish_reason, config_utils
#
# Tier 2 (external SDK deps only — safe unless those SDKs cause issues):
#   usage_config, thinking_config, extra_config, tools_config
#
# Tier 3 (imports from matrx_ai.media, ai.instructions, db.models — heavy):
#   media_config, unified_config
#
# Rule: import only the tier you need. If you only need Role or TokenUsage,
# import directly from the submodule to avoid loading the full unified_.
# ============================================================================

# --- Tier 1: Pure enums / constants / utilities ---
from .config_utils import truncate_base64_in_dict
from .enums import ContentType, Provider, Role
from .extra_config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    WebSearchCallContent,
)
from .finish_reason import FinishReason

# --- Tier 3: Media + unified config (heavy — loads db.models, ai.instructions, etc.) ---
# These are intentionally last. Anything that only needs Tier 1/2 types
# should import from the submodule directly to avoid this overhead.
from .media_config import (
    AudioContent,
    DocumentContent,
    ImageContent,
    MediaContent,
    MediaKind,
    VideoContent,
    YouTubeVideoContent,
    reconstruct_media_content,
)
from .message_config import MessageList, UnifiedMessage
from .thinking_config import ThinkingConfig
from .tools_config import ToolCallContent, ToolResultContent
from .unified_config import UnifiedConfig, UnifiedResponse
from .unified_content import TextContent, ThinkingContent, UnifiedContent, reconstruct_content

# --- Tier 2: Config dataclasses (external SDK deps only) ---
from .usage_config import (
    MODEL_PRICING,
    AggregatedUsage,
    ModelPricing,
    ModelUsageSummary,
    PricingTier,
    TokenUsage,
    UsageTotals,
)

__all__ = [
    # Tier 1
    "ContentType",
    "Provider",
    "Role",
    "FinishReason",
    "truncate_base64_in_dict",
    # Tier 2
    "AggregatedUsage",
    "ModelPricing",
    "ModelUsageSummary",
    "PricingTier",
    "TokenUsage",
    "UsageTotals",
    "MODEL_PRICING",
    "ThinkingConfig",
    "CodeExecutionContent",
    "CodeExecutionResultContent",
    "WebSearchCallContent",
    "ToolCallContent",
    "ToolResultContent",
    # Tier 3
    "AudioContent",
    "DocumentContent",
    "ImageContent",
    "MediaContent",
    "MediaKind",
    "VideoContent",
    "YouTubeVideoContent",
    "reconstruct_media_content",
    "MessageList",
    "TextContent",
    "ThinkingContent",
    "UnifiedConfig",
    "UnifiedContent",
    "UnifiedMessage",
    "UnifiedResponse",
    "reconstruct_content",
]
