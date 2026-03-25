from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from anthropic.types.usage import Usage as AnthropicUsage
from matrx_utils import vcprint
from openai.types.responses import ResponseUsage as OpenAIResponseUsage


@dataclass
class PricingTier:
    """Represents a pricing tier based on context length.

    Models can have tiered pricing where costs change based on the total
    number of input tokens (context length). Each tier defines the maximum
    token count it applies to and the prices for that tier.

    Attributes:
        max_tokens: Maximum tokens for this tier (None = unlimited/highest tier)
        input_price: Price per million input tokens at this tier
        output_price: Price per million output tokens at this tier
        cached_input_price: Price per million cached input tokens at this tier

    Example:
        # Tier for prompts <= 200k tokens
        PricingTier(max_tokens=200_000, input_price=2.00, output_price=12.00, cached_input_price=0.20)

        # Tier for prompts > 200k tokens (unlimited)
        PricingTier(max_tokens=None, input_price=4.00, output_price=18.00, cached_input_price=0.40)
    """

    max_tokens: int | None  # None means unlimited (highest tier)
    input_price: float  # price per million tokens
    output_price: float  # price per million tokens
    cached_input_price: float  # price per million tokens

    # Anthropic-specific cache pricing
    cache_write_5m_price: float | None = None  # 5-minute cache writes
    cache_write_1h_price: float | None = None  # 1-hour cache writes
    cache_hit_price: float | None = None  # Cache hits & refreshes

@dataclass
class ModelPricing:
    """Model pricing configuration.

    Stores pricing information for a specific model. Supports both simple
    flat-rate pricing and complex tiered pricing based on context length.

    Attributes:
        model_name: The model identifier (e.g., 'gemini-3-flash-preview')
        api: The API provider (e.g., 'google', 'openai', 'anthropic')
        tiers: List of pricing tiers, sorted by max_tokens ascending
               For simple flat-rate models, use a single tier with max_tokens=None

    Examples:
        # Simple flat-rate pricing
        ModelPricing(
            model_name="gemini-3-flash-preview",
            api="google",
            tiers=[
                PricingTier(max_tokens=None, input_price=0.50, output_price=3.00, cached_input_price=0.05)
            ]
        )

        # Tiered pricing based on context length
        ModelPricing(
            model_name="gemini-3-pro-preview",
            api="google",
            tiers=[
                PricingTier(max_tokens=200_000, input_price=2.00, output_price=12.00, cached_input_price=0.20),
                PricingTier(max_tokens=None, input_price=4.00, output_price=18.00, cached_input_price=0.40),
            ]
        )
    """

    model_name: str
    api: str
    tiers: list[PricingTier]

    def get_tier(self, total_input_tokens: int) -> PricingTier | None:
        """Get the appropriate pricing tier based on total input tokens.

        Args:
            total_input_tokens: Total input tokens (regular + cached) to determine tier

        Returns:
            The appropriate PricingTier, or None if no tiers defined
        """
        if not self.tiers:
            return None

        # Find the first tier where total_input_tokens <= max_tokens
        # Tiers should be sorted ascending by max_tokens
        for tier in self.tiers:
            if tier.max_tokens is None or total_input_tokens <= tier.max_tokens:
                return tier

        # If we get here, use the last tier (highest tier)
        return self.tiers[-1]

# Hard-coded pricing lookup for testing
# In production, this will come from the database
MODEL_PRICING: dict[str, ModelPricing] = {
    # --- Gemini TTS models ---
    # gemini-2.5-flash-preview-tts: text input $0.50/M, audio output $10.00/M
    "gemini-2.5-flash-preview-tts": ModelPricing(
        model_name="gemini-2.5-flash-preview-tts",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.50,   # text input per million tokens
                output_price=10.00,  # audio output per million tokens
                cached_input_price=0.05,
            )
        ],
    ),
    # gemini-2.5-pro-preview-tts: text input $1.00/M, audio output $20.00/M
    "gemini-2.5-pro-preview-tts": ModelPricing(
        model_name="gemini-2.5-pro-preview-tts",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.00,   # text input per million tokens
                output_price=20.00,  # audio output per million tokens
                cached_input_price=0.10,
            )
        ],
    ),
    # --- Gemini 3 series (preview) ---
    # gemini-3.1-flash-lite-preview: text/image/video input $0.25/M, audio input $0.50/M, output $1.50/M
    # Note: audio_input_price ($0.50/M) not captured in PricingTier; text rate used for input_price
    "gemini-3.1-flash-lite-preview": ModelPricing(
        model_name="gemini-3.1-flash-lite-preview",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.25,  # text, image, video input; audio input is $0.50/M
                output_price=1.50,
                cached_input_price=0.025,
            )
        ],
    ),
    # gemini-3.1-flash-image-preview: text input $0.25/M; image output price varies by resolution
    # output_price stores the base per-image price ($0.067) scaled to per-million-token equivalent
    # for cost tracking; actual billing is per-image and resolution-dependent
    "gemini-3.1-flash-image-preview": ModelPricing(
        model_name="gemini-3.1-flash-image-preview",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.25,  # text input per million tokens
                output_price=0.067,  # image output — price per image, resolution-dependent; see pricing page
                cached_input_price=0.025,
            )
        ],
    ),
    # gemini-3.1-pro-preview: tiered by context length, 1M context window
    "gemini-3.1-pro-preview": ModelPricing(
        model_name="gemini-3.1-pro-preview",
        api="google",
        tiers=[
            # Tier 1: prompts <= 200k tokens
            PricingTier(
                max_tokens=200_000,
                input_price=2.00,
                output_price=12.00,
                cached_input_price=0.20,
            ),
            # Tier 2: prompts > 200k tokens
            PricingTier(
                max_tokens=None,
                input_price=4.00,
                output_price=18.00,
                cached_input_price=0.40,
            ),
        ],
    ),
    "gemini-3-flash-preview": ModelPricing(
        model_name="gemini-3-flash-preview",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.50,
                output_price=3.00,
                cached_input_price=0.05,
            )
        ],
    ),
    # gemini-3-pro-image-preview (Nano Banana Pro): text input $2/M; image output price varies by resolution
    # output_price stores the base per-image price ($0.134); actual billing is per-image and resolution-dependent
    "gemini-3-pro-image-preview": ModelPricing(
        model_name="gemini-3-pro-image-preview",
        api="google",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=2.00,  # text input per million tokens
                output_price=0.134,  # image output — price per image, resolution-dependent; see pricing page
                cached_input_price=0.20,
            )
        ],
    ),
    # gemini-3-pro-preview: DEPRECATED — same pricing as gemini-3.1-pro-preview
    "gemini-3-pro-preview": ModelPricing(
        model_name="gemini-3-pro-preview",
        api="google",
        tiers=[
            # Tier 1: prompts <= 200k tokens
            PricingTier(
                max_tokens=200_000,
                input_price=2.00,
                output_price=12.00,
                cached_input_price=0.20,
            ),
            # Tier 2: prompts > 200k tokens
            PricingTier(
                max_tokens=None,  # Unlimited (highest tier)
                input_price=4.00,
                output_price=18.00,
                cached_input_price=0.40,
            ),
        ],
    ),
    # OpenAI models - use prefix matching (model names often have version suffixes)
    "gpt-5.2-pro": ModelPricing(
        model_name="gpt-5.2-pro",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=21.00,
                output_price=168.00,
                cached_input_price=21.00,  # Pro model doesn't advertise caching discount
            )
        ],
    ),
    "gpt-5.2": ModelPricing(
        model_name="gpt-5.2",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.75,
                output_price=14.00,
                cached_input_price=0.175,
            )
        ],
    ),
    "gpt-5.1": ModelPricing(
        model_name="gpt-5.1",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.25,
                output_price=10.00,
                cached_input_price=0.125,
            )
        ],
    ),
    "gpt-5-mini": ModelPricing(
        model_name="gpt-5-mini",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.25,
                output_price=2.00,
                cached_input_price=0.025,
            )
        ],
    ),
    "gpt-5-pro": ModelPricing(
        model_name="gpt-5-pro",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=15.00,
                output_price=120.00,
                cached_input_price=15.00,  # Pro model doesn't advertise caching discount
            )
        ],
    ),
    "gpt-5-nano": ModelPricing(
        model_name="gpt-5-nano",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.05,
                output_price=0.40,
                cached_input_price=0.005,
            )
        ],
    ),
    "gpt-5": ModelPricing(
        model_name="gpt-5",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.25,
                output_price=10.00,
                cached_input_price=0.125,
            )
        ],
    ),
    "gpt-4.1-mini": ModelPricing(
        model_name="gpt-4.1-mini",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.40,
                output_price=1.60,
                cached_input_price=0.10,
            )
        ],
    ),
    "gpt-4.1-nano": ModelPricing(
        model_name="gpt-4.1-nano",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.10,
                output_price=0.40,
                cached_input_price=0.025,
            )
        ],
    ),
    "gpt-4.1": ModelPricing(
        model_name="gpt-4.1",
        api="openai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=2.00,
                output_price=8.00,
                cached_input_price=0.50,
            )
        ],
    ),
    "claude-opus-4-6": ModelPricing(
        model_name="claude-opus-4-6",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=5.00,
                output_price=25.00,
                cached_input_price=6.25,
            )
        ],
    ),
    "claude-sonnet-4-6": ModelPricing(
        model_name="claude-sonnet-4-6",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=3.00,
                output_price=15.00,
                cached_input_price=3.75,
            )
        ],
    ),
    "claude-opus-4.5": ModelPricing(
        model_name="claude-opus-4.5",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=5.00,
                output_price=25.00,
                cached_input_price=6.25,  # 5m cache writes
            )
        ],
    ),
    "claude-opus-4.1": ModelPricing(
        model_name="claude-opus-4.1",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=15.00,
                output_price=75.00,
                cached_input_price=18.75,
            )
        ],
    ),
    "claude-opus-4": ModelPricing(
        model_name="claude-opus-4",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=15.00,
                output_price=75.00,
                cached_input_price=18.75,
            )
        ],
    ),
    "claude-sonnet-4.5": ModelPricing(
        model_name="claude-sonnet-4.5",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=3.00,
                output_price=15.00,
                cached_input_price=3.75,
            )
        ],
    ),
    "claude-sonnet-4": ModelPricing(
        model_name="claude-sonnet-4",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=3.00,
                output_price=15.00,
                cached_input_price=3.75,
            )
        ],
    ),
    "claude-sonnet-3.7": ModelPricing(
        model_name="claude-sonnet-3.7",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=3.00,
                output_price=15.00,
                cached_input_price=3.75,
            )
        ],
    ),
    "claude-haiku-4.5": ModelPricing(
        model_name="claude-haiku-4.5",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.00,
                output_price=5.00,
                cached_input_price=1.25,
            )
        ],
    ),
    "claude-haiku-3.5": ModelPricing(
        model_name="claude-haiku-3.5",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.80,
                output_price=4.00,
                cached_input_price=1.00,
            )
        ],
    ),
    "claude-opus-3": ModelPricing(
        model_name="claude-opus-3",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=15.00,
                output_price=75.00,
                cached_input_price=18.75,
            )
        ],
    ),
    "claude-haiku-3": ModelPricing(
        model_name="claude-haiku-3",
        api="anthropic",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.25,
                output_price=1.25,
                cached_input_price=0.30,
            )
        ],
    ),
    # Cerebras models - keys match what the API returns
    "llama-3.3-70b": ModelPricing(
        model_name="llama-3.3-70b",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.85,
                output_price=1.20,
                cached_input_price=0.85,  # Cerebras doesn't have cache pricing, use same as input
            )
        ],
    ),
    "llama-3.1-8b": ModelPricing(
        model_name="llama-3.1-8b",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.10,
                output_price=0.10,
                cached_input_price=0.10,
            )
        ],
    ),
    "qwen-3-235b-instruct": ModelPricing(
        model_name="qwen-3-235b-instruct",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.60,
                output_price=1.20,
                cached_input_price=0.60,
            )
        ],
    ),
    "qwen-3-32b": ModelPricing(
        model_name="qwen-3-32b",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.40,
                output_price=0.80,
                cached_input_price=0.40,
            )
        ],
    ),
    "glm-4.6": ModelPricing(
        model_name="glm-4.6",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=2.25,
                output_price=2.75,
                cached_input_price=2.25,
            )
        ],
    ),
    "gpt-oss-120b": ModelPricing(
        model_name="gpt-oss-120b",
        api="cerebras",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.35,
                output_price=0.75,
                cached_input_price=0.35,
            )
        ],
    ),
    # --- Groq models (https://console.groq.com/docs/models) ---
    "llama-3.1-8b-instant": ModelPricing(
        model_name="llama-3.1-8b-instant",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.05,
                output_price=0.08,
                cached_input_price=0.05,
            )
        ],
    ),
    "llama-3.3-70b-versatile": ModelPricing(
        model_name="llama-3.3-70b-versatile",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.59,
                output_price=0.79,
                cached_input_price=0.59,
            )
        ],
    ),
    "openai/gpt-oss-120b": ModelPricing(
        model_name="openai/gpt-oss-120b",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.15,
                output_price=0.60,
                cached_input_price=0.15,
            )
        ],
    ),
    "openai/gpt-oss-20b": ModelPricing(
        model_name="openai/gpt-oss-20b",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.075,
                output_price=0.30,
                cached_input_price=0.075,
            )
        ],
    ),
    "meta-llama/llama-4-scout-17b-16e-instruct": ModelPricing(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.11,
                output_price=0.34,
                cached_input_price=0.11,
            )
        ],
    ),
    "meta-llama/llama-prompt-guard-2-22m": ModelPricing(
        model_name="meta-llama/llama-prompt-guard-2-22m",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.03,
                output_price=0.03,
                cached_input_price=0.03,
            )
        ],
    ),
    "meta-llama/llama-prompt-guard-2-86m": ModelPricing(
        model_name="meta-llama/llama-prompt-guard-2-86m",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.04,
                output_price=0.04,
                cached_input_price=0.04,
            )
        ],
    ),
    "moonshotai/kimi-k2-instruct-0905": ModelPricing(
        model_name="moonshotai/kimi-k2-instruct-0905",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=1.00,
                output_price=3.00,
                cached_input_price=1.00,
            )
        ],
    ),
    "openai/gpt-oss-safeguard-20b": ModelPricing(
        model_name="openai/gpt-oss-safeguard-20b",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.075,
                output_price=0.30,
                cached_input_price=0.075,
            )
        ],
    ),
    "qwen/qwen3-32b": ModelPricing(
        model_name="qwen/qwen3-32b",
        api="groq",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.29,
                output_price=0.59,
                cached_input_price=0.29,
            )
        ],
    ),
    # xAI Grok models - ordered by specificity
    "grok-4-1-fast-reasoning": ModelPricing(
        model_name="grok-4-1-fast-reasoning",
        api="xai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.20,
                output_price=0.50,
                cached_input_price=0.05,
            )
        ],
    ),
    "grok-4-1-fast-non-reasoning": ModelPricing(
        model_name="grok-4-1-fast-non-reasoning",
        api="xai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.20,
                output_price=0.50,
                cached_input_price=0.05,
            )
        ],
    ),
    "grok-code-fast-1": ModelPricing(
        model_name="grok-code-fast-1",
        api="xai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.20,
                output_price=1.50,
                cached_input_price=0.02,
            )
        ],
    ),
    "grok-4-1": ModelPricing(
        model_name="grok-4-1",
        api="xai",
        tiers=[
            PricingTier(
                max_tokens=None,
                input_price=0.20,
                output_price=0.50,
                cached_input_price=0.05,
            )
        ],
    ),
}

@dataclass
class ModelUsageSummary:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    total_tokens: int = 0
    api: str = ""
    request_count: int = 0
    cost: float | None = 0.0

@dataclass
class UsageTotals:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    total_tokens: int = 0
    total_requests: int = 0
    unique_models: int = 0
    total_cost: float | None = None

@dataclass
class AggregatedUsage:
    by_model: dict[str, ModelUsageSummary] = field(default_factory=dict)
    total: UsageTotals = field(default_factory=UsageTotals)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class TokenUsage:
    """Unified token usage tracking across LLM providers.

    Tracks only what matters for cost calculation:
    - Input tokens (regular rate)
    - Output tokens (regular rate)
    - Cached input tokens (reduced/free rate)
    - Model name (for pricing lookup)
    - API provider (for provider-specific pricing)
    """

    input_tokens: int
    """Regular input tokens at standard rate"""

    output_tokens: int
    """All output tokens (includes reasoning/thinking/candidates)"""

    cached_input_tokens: int = 0
    """Input tokens served from cache (reduced/free cost)"""

    matrx_model_name: str = ""
    """AI Model ID (Truth) used for this request (for cost calculation)"""

    provider_model_name: str = ""
    """Model name used by the provider (could be different than requested model due to aliasing)"""

    api: str = ""
    """API provider (e.g., 'google', 'openai', 'anthropic')"""

    response_id: str = ""
    """Response ID from the API provider (for tracking and debugging)"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about the usage (e.g., transcription duration, file size)"""

    @property
    def total_tokens(self) -> int:
        """Total tokens processed (for informational purposes)"""
        return self.input_tokens + self.output_tokens + self.cached_input_tokens

    def calculate_cost(
        self, pricing_lookup: dict[str, ModelPricing] | None = None
    ) -> float | None:
        """Calculate the cost for this token usage based on model pricing.

        Args:
            pricing_lookup: Optional pricing lookup dictionary. If not provided,
                          uses the default MODEL_PRICING lookup.

        Returns:
            Total cost in USD, or None if pricing data is not available for this model.
            Returns None gracefully without raising errors.

        Example:
            >>> usage = TokenUsage(input_tokens=100_000, output_tokens=50_000,
            ...                    cached_input_tokens=25_000, model="gemini-3-flash-preview")
            >>> cost = usage.calculate_cost()
            >>> print(f"${cost:.4f}")
            $0.2025
        """
        if not self.matrx_model_name:
            return None

        # Use provided lookup or default
        lookup = pricing_lookup or MODEL_PRICING

        # Try exact match first
        model_pricing = lookup.get(self.matrx_model_name)

        # If no exact match and this is OpenAI, try prefix matching
        # OpenAI models often have version suffixes (e.g., gpt-5.2-2025-01-15)
        if not model_pricing and self.api == "openai":
            for model_key, pricing in lookup.items():
                if pricing.api == "openai" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        # If no exact match and this is Anthropic, try prefix matching
        # Anthropic models often have version suffixes (e.g., claude-sonnet-4-5-20250929)
        if not model_pricing and self.api == "anthropic":
            for model_key, pricing in lookup.items():
                if pricing.api == "anthropic" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        # If no exact match and this is Cerebras, try prefix matching
        # Cerebras models might have variations or versions
        if not model_pricing and self.api == "cerebras":
            for model_key, pricing in lookup.items():
                if pricing.api == "cerebras" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        # If no exact match and this is Together, try prefix matching
        if not model_pricing and self.api == "together":
            for model_key, pricing in lookup.items():
                if pricing.api == "together" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        # If no exact match and this is Groq, try prefix matching
        if not model_pricing and self.api == "groq":
            for model_key, pricing in lookup.items():
                if pricing.api == "groq" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        # If no exact match and this is xAI, try prefix matching
        if not model_pricing and self.api == "xai":
            for model_key, pricing in lookup.items():
                if pricing.api == "xai" and self.matrx_model_name.startswith(model_key):
                    model_pricing = pricing
                    break

        if not model_pricing:
            # No pricing data available for this model - return None gracefully
            vcprint(
                f"\n\n⚠️  Pricing not found for model: {self.matrx_model_name} (api: {self.api})\n\n",
                color="red",
            )
            return None

        # Calculate total input tokens (regular + cached) to determine tier
        total_input = self.input_tokens + self.cached_input_tokens

        # Get the appropriate pricing tier
        tier = model_pricing.get_tier(total_input)
        if not tier:
            vcprint(
                f"\n\n⚠️  Pricing tier not found for model: {self.matrx_model_name} (total_input: {total_input:,} tokens)\n\n",
                color="red",
            )
            return None

        # Calculate costs per token type (prices are per million tokens)
        input_cost = (self.input_tokens / 1_000_000) * tier.input_price
        output_cost = (self.output_tokens / 1_000_000) * tier.output_price
        cached_cost = (self.cached_input_tokens / 1_000_000) * tier.cached_input_price

        total_cost = input_cost + output_cost + cached_cost
        return total_cost

    def __add__(self, other: TokenUsage) -> TokenUsage:
        """Allow easy aggregation across multiple requests.

        Preserves model/API info if both operands use the same model.
        Sets model to 'mixed' if combining different models.
        Response ID is set to empty string when aggregating multiple responses.
        """
        # Preserve model/API if they match, otherwise mark as mixed
        model = self.matrx_model_name if self.matrx_model_name == other.matrx_model_name else "mixed"
        api = self.api if self.api == other.api else "mixed"

        return TokenUsage(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
            matrx_model_name=self.matrx_model_name,
            provider_model_name=self.provider_model_name,
            api=api,
            response_id="",  # Clear response_id when aggregating
        )

    @classmethod
    def from_gemini(
        cls, usage_metadata: dict[str, Any], matrx_model_name: str = "", provider_model_name: str = "", response_id: str = ""
    ) -> TokenUsage:
        """Create TokenUsage from Google Gemini usage metadata.

        Args:
            usage_metadata: The usageMetadata dict from Gemini response
            matrx_model_name: AI Model ID (Truth) used for this request
            provider_model_name: Model name used by the provider (could be different than requested model due to aliasing)
            response_id: Response ID from Gemini API
        """
        return cls(
            input_tokens=usage_metadata.prompt_token_count or 0,
            output_tokens=usage_metadata.candidates_token_count or 0,
            cached_input_tokens=usage_metadata.cached_content_token_count or 0,
            matrx_model_name=matrx_model_name,
            provider_model_name=provider_model_name,
            api="google",
            response_id=response_id,
        )

    @classmethod
    def from_openai(
        cls, usage: OpenAIResponseUsage, matrx_model_name: str, provider_model_name: str, response_id: str = ""
    ) -> TokenUsage:
        """Create TokenUsage from OpenAI usage object.

        Args:
            usage: The usage dict from OpenAI response
            matrx_model_name: AI Model ID (Truth) used for this request
            provider_model_name: Model name used by the provider (could be different than requested model due to aliasing)
            response_id: Response ID from OpenAI API
        """
        cached = (
            usage.input_tokens_details.cached_tokens
            if usage.input_tokens_details
            else 0
        )
        return cls(
            input_tokens=usage.input_tokens - cached,
            output_tokens=usage.output_tokens,
            cached_input_tokens=cached,
            matrx_model_name=matrx_model_name,
            provider_model_name=provider_model_name,
            api="openai",
            response_id=response_id,
        )

    @classmethod
    def from_anthropic(
        cls, usage: AnthropicUsage, matrx_model_name: str,  response_id: str = ""
    ) -> TokenUsage:
        """Create TokenUsage from Anthropic usage object.

        Args:
            usage: The usage dict from Anthropic response
            matrx_model_name: AI Model ID (Truth) used for this request
            response_id: Response ID from Anthropic API
        """
        cached = usage.get("cache_read_input_tokens", 0)
        return cls(
            input_tokens=usage["input_tokens"] - cached,
            output_tokens=usage["output_tokens"],
            cached_input_tokens=cached,
            matrx_model_name=matrx_model_name,
            provider_model_name=matrx_model_name,
            api="anthropic",
            response_id=response_id,
        )

    @staticmethod
    def aggregate_by_model(usage_list: list[TokenUsage]) -> AggregatedUsage:
        """Aggregate token usage by model for clean reporting.

        Takes a list of TokenUsage objects and returns total usage grouped by model.
        Useful for tracking usage across multiple requests with different models.
        """
        if not usage_list:
            return AggregatedUsage()

        model_usage: dict[str, ModelUsageSummary] = {}

        for usage in usage_list:
            model_key = usage.matrx_model_name or "unknown"

            if model_key not in model_usage:
                model_usage[model_key] = ModelUsageSummary(api=usage.api)

            summary = model_usage[model_key]
            summary.input_tokens += usage.input_tokens
            summary.output_tokens += usage.output_tokens
            summary.cached_input_tokens += usage.cached_input_tokens
            summary.total_tokens += usage.total_tokens
            summary.request_count += 1

            cost = usage.calculate_cost()
            if cost is not None:
                if summary.cost is not None:
                    summary.cost += cost
                else:
                    summary.cost = cost
            else:
                if summary.cost == 0.0:
                    summary.cost = None

        total_input = sum(m.input_tokens for m in model_usage.values())
        total_output = sum(m.output_tokens for m in model_usage.values())
        total_cached = sum(m.cached_input_tokens for m in model_usage.values())
        total_requests = sum(m.request_count for m in model_usage.values())

        total_cost = 0.0
        has_any_cost = False
        for model_data in model_usage.values():
            if model_data.cost is not None:
                total_cost += model_data.cost
                has_any_cost = True

        return AggregatedUsage(
            by_model=model_usage,
            total=UsageTotals(
                input_tokens=total_input,
                output_tokens=total_output,
                cached_input_tokens=total_cached,
                total_tokens=total_input + total_output + total_cached,
                total_requests=total_requests,
                unique_models=len(model_usage),
                total_cost=total_cost if has_any_cost else None,
            ),
        )
