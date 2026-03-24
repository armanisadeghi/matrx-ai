# File: db/managers/prompt_builtins.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from db.models import PromptBuiltins


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = PromptBuiltinsView on your manager subclass,
# or pass view_class=PromptBuiltinsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class PromptBuiltinsView(ModelView[PromptBuiltins]):
    """
    Declarative view for PromptBuiltins.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: PromptBuiltins) -> str:
            return model.name.title()
    """

    prefetch: list[str] = []
    exclude: list[str] = []
    inline_fk: dict[str, str] = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# Pydantic output schema (optional, requires pydantic v2).
# Auto-generated from the model's field definitions.  Useful for:
#   - FastAPI response_model type annotation
#   - JSON Schema generation: PromptBuiltinsSchema.model_json_schema()
#   - Typed API responses: PromptBuiltinsSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=PromptBuiltinsSchema)
#   async def get_prompt_builtins(id: str):
#       item = await prompt_builtins_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    PromptBuiltinsSchema = build_output_schema(PromptBuiltins)
except ImportError:
    PromptBuiltinsSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class PromptBuiltinsDTO(BaseDTO[PromptBuiltins]):
    id: str

    async def _initialize_dto(self, model: PromptBuiltins) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: PromptBuiltins) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: PromptBuiltins) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: PromptBuiltins) -> None:
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self) -> bool:
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self) -> dict[str, Any]:
        '''Get the validated dictionary.'''
        await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = PromptBuiltinsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(PromptBuiltins, view_class=PromptBuiltinsView)
# ---------------------------------------------------------------------------

class PromptBuiltinsBase(BaseManager[PromptBuiltins]):
    view_class = None  # DTO is used by default; set to PromptBuiltinsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(PromptBuiltins, dto_class=dto_class or PromptBuiltinsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: PromptBuiltins) -> None:
        pass

    async def create_prompt_builtins(self, **data: Any) -> PromptBuiltins:
        return await self.create_item(**data)

    async def delete_prompt_builtins(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_prompt_builtins_with_all_related(self, id: Any) -> tuple[PromptBuiltins, Any]:
        return await self.get_item_with_all_related(id)

    async def load_prompt_builtins_by_id(self, id: Any) -> PromptBuiltins:
        return await self.load_by_id(id)

    async def load_prompt_builtins(self, use_cache: bool = True, **kwargs: Any) -> PromptBuiltins:
        return await self.load_item(use_cache, **kwargs)

    async def update_prompt_builtins(self, id: Any, **updates: Any) -> PromptBuiltins:
        return await self.update_item(id, **updates)

    async def load_prompt_builtins(self, **kwargs: Any) -> list[PromptBuiltins]:
        return await self.load_items(**kwargs)

    async def filter_prompt_builtins(self, **kwargs: Any) -> list[PromptBuiltins]:
        return await self.filter_items(**kwargs)

    async def get_or_create_prompt_builtins(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> PromptBuiltins | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_prompt_builtins_with_ai_model(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'ai_model')

    async def get_prompt_builtins_with_ai_model(self) -> list[Any]:
        return await self.get_items_with_related('ai_model')

    async def get_prompt_builtins_with_prompts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompts')

    async def get_prompt_builtins_with_prompts(self) -> list[Any]:
        return await self.get_items_with_related('prompts')

    async def get_prompt_builtins_with_prompt_shortcuts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_shortcuts')

    async def get_prompt_builtins_with_prompt_shortcuts(self) -> list[Any]:
        return await self.get_items_with_related('prompt_shortcuts')

    async def get_prompt_builtins_with_prompt_actions(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_actions')

    async def get_prompt_builtins_with_prompt_actions(self) -> list[Any]:
        return await self.get_items_with_related('prompt_actions')

    async def get_prompt_builtins_with_prompt_builtin_versions(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_builtin_versions')

    async def get_prompt_builtins_with_prompt_builtin_versions(self) -> list[Any]:
        return await self.get_items_with_related('prompt_builtin_versions')

    async def load_prompt_builtins_by_created_by_user_id(self, created_by_user_id: Any) -> list[Any]:
        return await self.load_items(created_by_user_id=created_by_user_id)

    async def filter_prompt_builtins_by_created_by_user_id(self, created_by_user_id: Any) -> list[Any]:
        return await self.filter_items(created_by_user_id=created_by_user_id)

    async def load_prompt_builtins_by_source_prompt_id(self, source_prompt_id: Any) -> list[Any]:
        return await self.load_items(source_prompt_id=source_prompt_id)

    async def filter_prompt_builtins_by_source_prompt_id(self, source_prompt_id: Any) -> list[Any]:
        return await self.filter_items(source_prompt_id=source_prompt_id)

    async def load_prompt_builtins_by_tags(self, tags: Any) -> list[Any]:
        return await self.load_items(tags=tags)

    async def filter_prompt_builtins_by_tags(self, tags: Any) -> list[Any]:
        return await self.filter_items(tags=tags)

    async def load_prompt_builtins_by_model_id(self, model_id: Any) -> list[Any]:
        return await self.load_items(model_id=model_id)

    async def filter_prompt_builtins_by_model_id(self, model_id: Any) -> list[Any]:
        return await self.filter_items(model_id=model_id)

    async def load_prompt_builtins_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_prompt_builtins_ids(self) -> set[Any]:
        return self.active_item_ids



class PromptBuiltinsManager(PromptBuiltinsBase):
    _instance: PromptBuiltinsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> PromptBuiltinsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: PromptBuiltins) -> None:
        pass

prompt_builtins_manager_instance = PromptBuiltinsManager()