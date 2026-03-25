from __future__ import annotations

import time
from enum import StrEnum
from typing import Any

from matrx_ai.db.managers.prompt_builtins import PromptBuiltinsBase
from matrx_ai.db.managers.prompts import PromptsBase
from matrx_ai.db.models import PromptBuiltins, Prompts
from matrx_utils import vcprint

from matrx_ai.agents.types import AgentConfig
from matrx_ai.agents.variables import AgentVariable
from matrx_ai.config.unified_config import UnifiedConfig


class PromptType(StrEnum):
    PROMPT = "prompt"
    BUILTIN = "builtin"


class PromptsManager(PromptsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def to_config(self, prompt_id: str) -> AgentConfig:
        prompt: Prompts = await self.load_prompts_by_id(prompt_id)

        settings: dict[str, Any] = (
            prompt.settings if isinstance(prompt.settings, dict) else {}
        )
        config_dict = {
            "messages": prompt.messages,
            "model": settings.get("model_id", ""),
            **settings,
        }

        if "tools" not in config_dict and prompt.tools:
            config_dict["tools"] = prompt.tools

        config = UnifiedConfig.from_dict(config_dict)
        variable_defaults = AgentVariable.from_list(prompt.variable_defaults)

        return AgentConfig(
            name=prompt.name,
            config=config,
            variable_defaults=variable_defaults,
        )


class PromptBuiltinsManager(PromptBuiltinsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def to_config(self, builtin_id: str) -> AgentConfig:
        builtin: PromptBuiltins = await self.load_prompt_builtins_by_id(builtin_id)

        settings: dict[str, Any] = (
            builtin.settings if isinstance(builtin.settings, dict) else {}
        )
        config_dict = {
            "messages": builtin.messages,
            "model": settings.get("model_id", "") or settings.get("ai_model", ""),
            **settings,
        }

        if "tools" not in config_dict and builtin.tools:
            config_dict["tools"] = builtin.tools

        config = UnifiedConfig.from_dict(config_dict)
        variable_defaults = AgentVariable.from_list(builtin.variable_defaults)

        return AgentConfig(
            name=builtin.name,
            config=config,
            variable_defaults=variable_defaults,
        )


# ---------------------------------------------------------------------------
# Singleton instances (internal — use pm for all access)
# ---------------------------------------------------------------------------
_prompts_mgr = PromptsManager()
_builtins_mgr = PromptBuiltinsManager()

# ---------------------------------------------------------------------------
# Aggregator — single access point for all prompt/builtin operations
# ---------------------------------------------------------------------------
class PromptManagers:
    _instance: PromptManagers | None = None

    def __new__(cls) -> PromptManagers:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._prompt: PromptsManager = _prompts_mgr
        self._builtin: PromptBuiltinsManager = _builtins_mgr
        self._type_cache: dict[str, PromptType] = {}

    # -- Cache operations ---------------------------------------------------

    def _cache(self, item_id: str, ptype: PromptType) -> None:
        self._type_cache[str(item_id)] = ptype

    def get_type(self, prompt_id: str) -> PromptType | None:
        return self._type_cache.get(prompt_id)

    @property
    def cache_size(self) -> int:
        return len(self._type_cache)

    # -- Hydration ----------------------------------------------------------

    async def hydrate_builtins(self) -> int:
        start = time.perf_counter()
        builtins = await self._builtin.load_items()
        for item in builtins:
            if item and hasattr(item, "id"):
                self._cache(item.id, PromptType.BUILTIN)
        elapsed = time.perf_counter() - start
        count = len(builtins)
        time_str = f"{elapsed * 1000:.2f}ms" if elapsed < 1.0 else f"{elapsed:.3f}s"
        vcprint(
            f"[PromptManagers] Hydrated {count} builtins in {time_str}",
            color="blue",
        )
        return count

    def hydrate_builtins_sync(self) -> int:
        start = time.perf_counter()
        builtins = self._builtin.load_items_sync()
        for item in builtins:
            if item and hasattr(item, "id"):
                self._cache(item.id, PromptType.BUILTIN)
        elapsed = time.perf_counter() - start
        count = len(builtins)
        time_str = f"{elapsed * 1000:.2f}ms" if elapsed < 1.0 else f"{elapsed:.3f}s"
        vcprint(
            f"[PromptManagers] Hydrated {count} builtins in {time_str}",
            color="blue",
        )
        return count

    # -- Unified config fetching (for Agent creation) -----------------------

    async def get_config(self, prompt_id: str) -> AgentConfig:
        cached_type = self._type_cache.get(prompt_id)

        if cached_type == PromptType.PROMPT:
            return await self._prompt_config(prompt_id)
        if cached_type == PromptType.BUILTIN:
            return await self._builtin_config(prompt_id)

        item = await self._prompt.load_item_or_none(id=prompt_id)
        if item:
            self._cache(prompt_id, PromptType.PROMPT)
            return await self._prompt_config(prompt_id)

        builtin_item = await self._builtin.load_item_or_none(id=prompt_id)
        if builtin_item:
            self._cache(prompt_id, PromptType.BUILTIN)
            return await self._builtin_config(prompt_id)

        raise ValueError(f"No prompt or builtin found with id: {prompt_id!r}")

    async def get_prompt_config(self, prompt_id: str) -> AgentConfig:
        return await self._prompt_config(prompt_id)

    async def get_builtin_config(self, builtin_id: str) -> AgentConfig:
        return await self._builtin_config(builtin_id)

    async def _prompt_config(self, prompt_id: str) -> AgentConfig:
        config = await self._prompt.to_config(prompt_id)
        self._cache(prompt_id, PromptType.PROMPT)
        return config

    async def _builtin_config(self, builtin_id: str) -> AgentConfig:
        config = await self._builtin.to_config(builtin_id)
        self._cache(builtin_id, PromptType.BUILTIN)
        return config

    # -- Prompt CRUD (caches type on every operation) -----------------------

    async def load_prompt(self, prompt_id: str) -> Prompts:
        item = await self._prompt.load_prompts_by_id(prompt_id)
        self._cache(prompt_id, PromptType.PROMPT)
        return item

    async def load_prompt_or_none(self, prompt_id: str) -> Prompts | None:
        item = await self._prompt.load_item_or_none(id=prompt_id)
        if item:
            self._cache(prompt_id, PromptType.PROMPT)
        return item

    async def find_prompts(self, **kwargs: Any) -> list[Prompts]:
        items = await self._prompt.filter_items(**kwargs)
        for item in items:
            if item and hasattr(item, "id"):
                self._cache(item.id, PromptType.PROMPT)
        return items

    async def create_prompt(self, **data: Any) -> Prompts:
        item = await self._prompt.create_item(**data)
        if item and hasattr(item, "id"):
            self._cache(item.id, PromptType.PROMPT)
        return item

    # -- Builtin CRUD (caches type on every operation) ----------------------

    async def load_builtin(self, builtin_id: str) -> PromptBuiltins:
        item = await self._builtin.load_prompt_builtins_by_id(builtin_id)
        self._cache(builtin_id, PromptType.BUILTIN)
        return item

    async def load_builtin_or_none(self, builtin_id: str) -> PromptBuiltins | None:
        item = await self._builtin.load_item_or_none(id=builtin_id)
        if item:
            self._cache(builtin_id, PromptType.BUILTIN)
        return item

    async def find_builtins(self, **kwargs: Any) -> list[PromptBuiltins]:
        items = await self._builtin.filter_items(**kwargs)
        for item in items:
            if item and hasattr(item, "id"):
                self._cache(item.id, PromptType.BUILTIN)
        return items

    async def create_builtin(self, **data: Any) -> PromptBuiltins:
        item = await self._builtin.create_item(**data)
        if item and hasattr(item, "id"):
            self._cache(item.id, PromptType.BUILTIN)
        return item

    async def update_prompt(self, prompt_id: str, **updates: Any) -> Prompts:
        return await self._prompt.update_item(prompt_id, **updates)

    async def update_builtin(self, builtin_id: str, **updates: Any) -> PromptBuiltins:
        return await self._builtin.update_item(builtin_id, **updates)

    async def update_by_id(self, item_id: str, **updates: Any) -> Prompts | PromptBuiltins:
        cached_type = self._type_cache.get(item_id)
        if cached_type == PromptType.BUILTIN:
            return await self.update_builtin(item_id, **updates)
        return await self.update_prompt(item_id, **updates)

    # -- Unified load (don't know the type) ---------------------------------

    async def load_by_id(self, item_id: str) -> Prompts | PromptBuiltins:
        cached_type = self._type_cache.get(item_id)

        if cached_type == PromptType.PROMPT:
            return await self.load_prompt(item_id)
        if cached_type == PromptType.BUILTIN:
            return await self.load_builtin(item_id)

        item = await self._prompt.load_item_or_none(id=item_id)
        if item:
            self._cache(item_id, PromptType.PROMPT)
            return item

        item = await self._builtin.load_by_id(item_id)
        self._cache(item_id, PromptType.BUILTIN)
        return item

    async def load_without_cache(self, item_id: str) -> Prompts | PromptBuiltins:
        cached_type = self._type_cache.get(item_id)
        if cached_type == PromptType.PROMPT:
            return await self._prompt.load_item(use_cache=False, id=item_id)
        if cached_type == PromptType.BUILTIN:
            return await self._builtin.load_item(use_cache=False, id=item_id)
        return await self._prompt.load_item(use_cache=False, id=item_id)


    async def load_by_id_or_none(self, item_id: str) -> Prompts | PromptBuiltins | None:
        cached_type = self._type_cache.get(item_id)

        if cached_type == PromptType.PROMPT:
            return await self.load_prompt_or_none(item_id)
        if cached_type == PromptType.BUILTIN:
            return await self.load_builtin_or_none(item_id)

        item = await self._prompt.load_item_or_none(id=item_id)
        if item:
            self._cache(item_id, PromptType.PROMPT)
            return item

        item = await self._builtin.load_item_or_none(id=item_id)
        if item:
            self._cache(item_id, PromptType.BUILTIN)
        return item


pm = PromptManagers()
