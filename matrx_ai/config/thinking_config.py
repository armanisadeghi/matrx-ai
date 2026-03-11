from dataclasses import dataclass
from typing import Any, Literal

from matrx_utils import vcprint
from openai.types.shared.reasoning_effort import ReasoningEffort
from openai.types.shared_params import Reasoning


@dataclass
class ThinkingConfig:
    """
    Unified thinking/reasoning configuration for all AI APIs.

    All possible thinking-related parameters are stored here, then
    converted to API-specific formats via to_* methods.
    """

    # Primary controls (NEW STANDARD)
    reasoning_effort: Literal["auto", "none", "minimal", "low", "medium", "high", "xhigh"] | None = None
    reasoning_summary: Literal["concise", "detailed", "never", "auto", "always"] | None = None

    # Legacy controls (BACKWARD COMPATIBILITY)
    thinking_budget: int | None = None
    thinking_level: Literal["minimal", "low", "medium", "high"] | None = None
    include_thoughts: bool | None = None

    def to_openai_reasoning(self) -> Reasoning:
        """
        Convert to OpenAI Reasoning API format.

        Returns:
            Reasoning TypedDict with optional 'effort' and 'summary' fields.
            Example: Reasoning(effort="medium", summary="detailed")
        """
        # Build config with explicit type
        config: Reasoning = {}
        
        # Determine effort level with proper type annotation
        effort: ReasoningEffort | None = None
        
        if self.reasoning_effort:
            # Map our internal values to OpenAI's valid ReasoningEffort values
            effort_mapping: dict[str, ReasoningEffort | None] = {
                "auto": None,  # "auto" = let the API decide, so omit the field
                "none": "none",
                "minimal": "minimal",
                "low": "low",
                "medium": "medium",
                "high": "high",
                "xhigh": "xhigh",
            }
            effort = effort_mapping.get(self.reasoning_effort)
        elif self.thinking_budget is not None:
            tokens = int(self.thinking_budget)
            if tokens < 1:
                effort = "none"
            elif tokens < 2000:
                effort = "low"
            elif tokens < 10000:
                effort = "medium"
            elif tokens < 20000:
                effort = "high"
            else:
                effort = "xhigh"

        if effort is not None:
            config["effort"] = effort

        # Add summary if specified with proper type annotation
        if self.reasoning_summary:
            # OpenAI only supports "auto" | "concise" | "detailed" — "never" omits the field,
            # "always" has no direct equivalent so maps to "detailed" (strongest always-on option).
            summary_mapping: dict[
                str, Literal["auto", "concise", "detailed"] | None
            ] = {
                "auto": "auto",
                "concise": "concise",
                "detailed": "detailed",
                "never": None,
                "always": "detailed",
            }

            summary: Literal["auto", "concise", "detailed"] | None = summary_mapping.get(self.reasoning_summary)
            if summary is not None:
                config["summary"] = summary

        return config

    def to_google_thinking_legacy(self) -> dict[str, Any]:
        """
        Convert to Google legacy thinking format (thinking_budget).

        Returns:
            {
                "include_thoughts": bool,
                "thinking_budget": int
            }
        """
        config = {}

        if self.include_thoughts is False:
            config["include_thoughts"] = False
            config["thinking_budget"] = -1
        else:
            if self.include_thoughts is not None:
                config["include_thoughts"] = self.include_thoughts

            thinking_budget = None
            if self.thinking_budget is not None:
                thinking_budget = int(self.thinking_budget)
            elif self.reasoning_effort:
                effort_to_budget = {
                    "none": 0,
                    "minimal": 512,
                    "low": 1024,
                    "medium": 4096,
                    "high": 8192,
                    "xhigh": 24576,
                }
                thinking_budget = effort_to_budget.get(self.reasoning_effort, 1024)

            if thinking_budget is not None and thinking_budget > 0:
                config["thinking_budget"] = thinking_budget

        return config

    def to_google_thinking_3(self, model_name: str | None = None) -> dict[str, Any]:
        """
        Convert to Google Gemini 3 thinking format (thinking_level).

        Args:
            model_name: Model name to determine flash vs pro mapping

        Returns:
            {
                "thinking_level": "minimal" | "low" | "medium" | "high",
                "include_thoughts": bool
            }
        """
        config = {}

        thinking_level = None
        include_thoughts = None

        # Priority 1: reasoning_effort -> thinking_level (NEW STANDARD)
        if self.reasoning_effort:
            effort_to_level_flash = {
                "auto": None,
                "none": "minimal",
                "minimal": "minimal",
                "low": "low",
                "medium": "medium",
                "high": "high",
                "xhigh": "high",
            }
            effort_to_level_pro = {
                "auto": "low",
                "none": "low",
                "minimal": "low",
                "low": "low",
                "medium": "low",
                "high": "high",
                "xhigh": "high",
            }

            if model_name and model_name.startswith("gemini-3-flash"):
                thinking_level = effort_to_level_flash.get(self.reasoning_effort)
            else:
                thinking_level = effort_to_level_pro.get(self.reasoning_effort)

        # Priority 2: reasoning_summary -> include_thoughts (NEW STANDARD)
        if self.reasoning_summary:
            summary_to_include = {
                "concise": True,
                "always": True,
                "detailed": True,
                "never": False,
                "auto": None,
            }
            include_thoughts = summary_to_include.get(self.reasoning_summary)

        # Backward compatibility: thinking_budget -> thinking_level
        if thinking_level is None and self.thinking_budget is not None:
            budget = int(self.thinking_budget)
            if budget <= 0:
                thinking_level = None
            elif budget <= 512:
                thinking_level = "minimal"
            elif budget <= 1024:
                thinking_level = "low"
            elif budget <= 4096:
                thinking_level = "medium"
            else:
                thinking_level = "high"

        # Backward compatibility: include_thoughts override
        if self.include_thoughts is not None:
            include_thoughts = self.include_thoughts

        # Build config
        if thinking_level is not None:
            config["thinking_level"] = thinking_level
        if include_thoughts is not None:
            config["include_thoughts"] = include_thoughts

        return config

    def to_anthropic_thinking(
        self, current_max_tokens: int | None = None
    ) -> dict[str, Any] | None:
        """
        Convert to Anthropic thinking format with max_tokens validation.
        
        Anthropic requires max_tokens > thinking.budget_tokens.
        This method validates and adjusts max_tokens if needed.

        Args:
            current_max_tokens: The currently configured max_tokens (if any)

        Returns:
            {
                "thinking": {
                    "type": "enabled",
                    "budget_tokens": int
                },
                "max_tokens": int  # Validated/adjusted value
            }
            or None if no thinking requested
        """
        thinking_budget = None

        if self.thinking_budget is not None:
            thinking_budget = int(self.thinking_budget)
        elif self.reasoning_effort:
            # Convert effort to Anthropic budget_tokens
            effort_to_budget = {
                "none": 0,
                "minimal": 512,
                "low": 1024,
                "medium": 4096,
                "high": 8192,
                "xhigh": 24576,
            }

            thinking_budget = effort_to_budget.get(self.reasoning_effort)

        if thinking_budget:
            thinking_config = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }
            
            # Validate max_tokens vs thinking_budget
            if current_max_tokens is None:
                # If no max_tokens provided, set a reasonable value
                # Must be greater than thinking_budget
                validated_max_tokens = thinking_budget + 2048
                vcprint(
                    f"⚠️  Anthropic thinking enabled (budget: {thinking_budget}) but no max_tokens set. Setting max_tokens to {validated_max_tokens}",
                    color="yellow"
                )
            elif current_max_tokens <= thinking_budget:
                # max_tokens too small - adjust it
                validated_max_tokens = thinking_budget + 2048
                vcprint(
                    f"⚠️  Anthropic requires max_tokens ({current_max_tokens}) > thinking.budget_tokens ({thinking_budget}). Automatically adjusting max_tokens to {validated_max_tokens}",
                    color="yellow"
                )
            else:
                # max_tokens is valid
                validated_max_tokens = current_max_tokens
            
            return {
                "thinking": thinking_config,
                "max_tokens": validated_max_tokens
            }

        return None

    def to_anthropic_adaptive_thinking(
        self, current_max_tokens: int | None = None
    ) -> dict[str, Any] | None:
        """
        Convert to Anthropic adaptive thinking format (claude-opus-4-6, claude-sonnet-4-6).

        Adaptive thinking lets the model self-allocate its thinking token budget based on
        task complexity. The caller controls depth/cost through an effort level rather
        than a fixed budget_tokens integer.

        Wire format produced:
            {
                "thinking": {"type": "adaptive"},
                "output_config": {"effort": "low" | "medium" | "high"},
                "max_tokens": int
            }
        Returns None if thinking should be omitted entirely (reasoning_effort="none",
        thinking_budget <= 0, or include_thoughts=False).

        Input priority chain (mirrors to_google_thinking_3 pattern):
            1. reasoning_effort  → effort level (primary, new standard)
            2. thinking_budget   → effort level (backward compat, token ranges)
            3. thinking_level    → effort level (backward compat, named levels)
            4. include_thoughts=False → omit thinking block entirely
        """
        effort: str | None = None

        # Priority 1: reasoning_effort -> effort (NEW STANDARD)
        if self.reasoning_effort is not None:
            effort_mapping: dict[str, str | None] = {
                "auto": "high",      # Sonnet 4.6 defaults to high; be explicit
                "none": None,        # Omit thinking entirely
                "minimal": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
                "xhigh": "high",
            }
            effort = effort_mapping.get(self.reasoning_effort)
            # reasoning_effort="none" is an explicit signal to disable thinking
            if self.reasoning_effort == "none":
                return None

        # Priority 2: thinking_budget -> effort (BACKWARD COMPATIBILITY)
        if effort is None and self.thinking_budget is not None:
            budget = int(self.thinking_budget)
            if budget <= 0:
                return None
            elif budget <= 1024:
                effort = "low"
            elif budget <= 8192:
                effort = "medium"
            else:
                effort = "high"

        # Priority 3: thinking_level -> effort (BACKWARD COMPATIBILITY)
        if effort is None and self.thinking_level is not None:
            level_mapping: dict[str, str] = {
                "minimal": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
            }
            effort = level_mapping.get(self.thinking_level)

        # Priority 4: include_thoughts=False -> disable thinking
        if self.include_thoughts is False:
            return None

        if effort is None:
            return None

        # Adaptive thinking has no budget_tokens constraint on max_tokens,
        # so we just ensure max_tokens is set to a reasonable value.
        max_tokens = current_max_tokens if current_max_tokens is not None else 8000

        return {
            "thinking": {"type": "adaptive"},
            "output_config": {"effort": effort},
            "max_tokens": max_tokens,
        }

    def to_cerebras_reasoning(self) -> str | None:
        """
        Convert to Cerebras reasoning_effort format.

        Returns:
            "low" | "medium" | "high" or None
        """
        reasoning_effort = None

        # Priority 1: reasoning_effort (NEW STANDARD)
        if self.reasoning_effort is not None:
            effort_mapping = {
                "auto": "medium",
                "none": None,
                "minimal": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
                "xhigh": "high",
            }
            reasoning_effort = effort_mapping.get(self.reasoning_effort)

        # Priority 2: thinking_budget (BACKWARD COMPATIBILITY)
        if reasoning_effort is None and self.thinking_budget is not None:
            budget = int(self.thinking_budget)
            if budget <= 0:
                reasoning_effort = None
            elif budget <= 1024:
                reasoning_effort = "low"
            elif budget <= 4096:
                reasoning_effort = "medium"
            else:
                reasoning_effort = "high"

        # Priority 3: thinking_level (BACKWARD COMPATIBILITY)
        if reasoning_effort is None and self.thinking_level is not None:
            level_mapping = {
                "minimal": "low",
                "low": "low",
                "medium": "medium",
                "high": "high",
            }
            reasoning_effort = level_mapping.get(self.thinking_level)

        return reasoning_effort

    @classmethod
    def from_settings(cls, settings: Any) -> "ThinkingConfig":
        """
        Factory method to create ThinkingConfig from AISettingsData.

        Args:
            settings: AISettingsData instance

        Returns:
            ThinkingConfig instance with all relevant fields populated
        """
        return cls(
            reasoning_effort=getattr(settings, "reasoning_effort", None),
            reasoning_summary=getattr(settings, "reasoning_summary", None),
            thinking_budget=getattr(settings, "thinking_budget", None),
            thinking_level=getattr(settings, "thinking_level", None),
            include_thoughts=getattr(settings, "include_thoughts", None),
        )
