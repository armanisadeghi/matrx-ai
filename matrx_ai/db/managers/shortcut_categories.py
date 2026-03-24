# File: db/managers/shortcut_categories.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from matrx_ai.db.models import ShortcutCategories


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = ShortcutCategoriesView on your manager subclass,
# or pass view_class=ShortcutCategoriesView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class ShortcutCategoriesView(ModelView[ShortcutCategories]):
    """
    Declarative view for ShortcutCategories.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: ShortcutCategories) -> str:
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
#   - JSON Schema generation: ShortcutCategoriesSchema.model_json_schema()
#   - Typed API responses: ShortcutCategoriesSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=ShortcutCategoriesSchema)
#   async def get_shortcut_categories(id: str):
#       item = await shortcut_categories_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    ShortcutCategoriesSchema = build_output_schema(ShortcutCategories)
except ImportError:
    ShortcutCategoriesSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class ShortcutCategoriesDTO(BaseDTO[ShortcutCategories]):
    id: str

    async def _initialize_dto(self, model: ShortcutCategories) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: ShortcutCategories) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: ShortcutCategories) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: ShortcutCategories) -> None:
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
#   1. Quick: set view_class = ShortcutCategoriesView  (replaces DTO automatically)
#   2. Explicit: super().__init__(ShortcutCategories, view_class=ShortcutCategoriesView)
# ---------------------------------------------------------------------------

class ShortcutCategoriesBase(BaseManager[ShortcutCategories]):
    view_class = None  # DTO is used by default; set to ShortcutCategoriesView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(ShortcutCategories, dto_class=dto_class or ShortcutCategoriesDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: ShortcutCategories) -> None:
        pass

    async def create_shortcut_categories(self, **data: Any) -> ShortcutCategories:
        return await self.create_item(**data)

    async def delete_shortcut_categories(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_shortcut_categories_with_all_related(self, id: Any) -> tuple[ShortcutCategories, Any]:
        return await self.get_item_with_all_related(id)

    async def load_shortcut_categories_by_id(self, id: Any) -> ShortcutCategories:
        return await self.load_by_id(id)

    async def load_shortcut_categories(self, use_cache: bool = True, **kwargs: Any) -> ShortcutCategories:
        return await self.load_item(use_cache, **kwargs)

    async def update_shortcut_categories(self, id: Any, **updates: Any) -> ShortcutCategories:
        return await self.update_item(id, **updates)

    async def load_shortcut_categories(self, **kwargs: Any) -> list[ShortcutCategories]:
        return await self.load_items(**kwargs)

    async def filter_shortcut_categories(self, **kwargs: Any) -> list[ShortcutCategories]:
        return await self.filter_items(**kwargs)

    async def get_or_create_shortcut_categories(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ShortcutCategories | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_shortcut_categories_with_self_reference(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'self_reference')

    async def get_shortcut_categories_with_self_reference(self) -> list[Any]:
        return await self.get_items_with_related('self_reference')

    async def get_shortcut_categories_with_content_blocks(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'content_blocks')

    async def get_shortcut_categories_with_content_blocks(self) -> list[Any]:
        return await self.get_items_with_related('content_blocks')

    async def get_shortcut_categories_with_prompt_shortcuts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_shortcuts')

    async def get_shortcut_categories_with_prompt_shortcuts(self) -> list[Any]:
        return await self.get_items_with_related('prompt_shortcuts')

    async def get_shortcut_categories_with_system_prompts_new(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'system_prompts_new')

    async def get_shortcut_categories_with_system_prompts_new(self) -> list[Any]:
        return await self.get_items_with_related('system_prompts_new')

    async def load_shortcut_categories_by_parent_category_id(self, parent_category_id: Any) -> list[Any]:
        return await self.load_items(parent_category_id=parent_category_id)

    async def filter_shortcut_categories_by_parent_category_id(self, parent_category_id: Any) -> list[Any]:
        return await self.filter_items(parent_category_id=parent_category_id)

    async def load_shortcut_categories_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_shortcut_categories_ids(self) -> set[Any]:
        return self.active_item_ids



class ShortcutCategoriesManager(ShortcutCategoriesBase):
    _instance: ShortcutCategoriesManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> ShortcutCategoriesManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: ShortcutCategories) -> None:
        pass

shortcut_categories_manager_instance = ShortcutCategoriesManager()