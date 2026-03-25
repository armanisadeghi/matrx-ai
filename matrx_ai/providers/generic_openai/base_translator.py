"""Base class for all provider translators.

All provider-specific translators should inherit from this. It centralizes
any logic that is shared across providers at the translation boundary — in
particular, system instruction resolution.

Design rule
-----------
Translators must NEVER call str(config.system_instruction) directly.
They must NEVER access config.resolved_system_instruction directly either.
Instead, call self.get_system_text(config), which is the single, versioned
point where that resolution happens. If the resolution logic ever changes
(caching, fallback, logging, etc.), it changes here and nowhere else.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from matrx_ai.config.unified_config import UnifiedConfig


class BaseTranslator:
    """Minimal shared behaviour for all provider translators."""

    debug: bool

    def __init__(self, debug: bool = False):
        self.debug = debug

    def get_system_text(self, config: "UnifiedConfig") -> str | None:
        """Return the resolved system instruction string, or None if absent.

        This is the only place in the codebase where UnifiedConfig.system_instruction
        is resolved to a plain string for use in an API request. All translators
        must call this method instead of accessing resolved_system_instruction directly.
        """
        return config.resolved_system_instruction
