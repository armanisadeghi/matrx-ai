# File: db/managers/shortcut_categories.py
from matrx_utils import vcprint


from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from db.models import ShortcutCategories


# ---------------------------------------------------------------------------
# ModelView (new) — preferred projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# ---------------------------------------------------------------------------

class ShortcutCategoriesView(ModelView):
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

    prefetch: list = ['self_reference', 'content_blocks', 'prompt_shortcuts', 'system_prompts_new']
    exclude: list = []
    inline_fk: dict = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# BaseDTO (legacy) — kept for backward compatibility.
# Existing imports of ShortcutCategoriesDTO from this file continue to work.
# Migrate business logic to ShortcutCategoriesView when ready.
# ---------------------------------------------------------------------------

@dataclass
class ShortcutCategoriesDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, model):
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — uses ModelView by default.
# To revert to the legacy DTO path:
#   view_class = None
#   super().__init__(ShortcutCategories, dto_class=ShortcutCategoriesDTO)
# ---------------------------------------------------------------------------

class ShortcutCategoriesBase(BaseManager[ShortcutCategories]):
    view_class = ShortcutCategoriesView

    def __init__(self, view_class: type[Any] | None = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(ShortcutCategories)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: ShortcutCategories) -> None:
        pass

    async def create_shortcut_categories(self, **data):
        return await self.create_item(**data)

    async def delete_shortcut_categories(self, id):
        return await self.delete_item(id)

    async def get_shortcut_categories_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_shortcut_categories_by_id(self, id):
        return await self.load_by_id(id)

    async def load_shortcut_categories(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_shortcut_categories(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_shortcut_category(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_shortcut_category(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_shortcut_categories_with_self_reference(self, id):
        return await self.get_item_with_related(id, 'self_reference')

    async def get_shortcut_category_with_self_reference(self):
        return await self.get_items_with_related('self_reference')

    async def get_shortcut_categories_with_content_blocks(self, id):
        return await self.get_item_with_related(id, 'content_blocks')

    async def get_shortcut_category_with_content_blocks(self):
        return await self.get_items_with_related('content_blocks')

    async def get_shortcut_categories_with_prompt_shortcuts(self, id):
        return await self.get_item_with_related(id, 'prompt_shortcuts')

    async def get_shortcut_category_with_prompt_shortcuts(self):
        return await self.get_items_with_related('prompt_shortcuts')

    async def get_shortcut_categories_with_system_prompts_new(self, id):
        return await self.get_item_with_related(id, 'system_prompts_new')

    async def get_shortcut_category_with_system_prompts_new(self):
        return await self.get_items_with_related('system_prompts_new')

    async def load_shortcut_category_by_parent_category_id(self, parent_category_id):
        return await self.load_items(parent_category_id=parent_category_id)

    async def filter_shortcut_category_by_parent_category_id(self, parent_category_id):
        return await self.filter_items(parent_category_id=parent_category_id)

    async def load_shortcut_category_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_shortcut_categories_ids(self):
        return self.active_item_ids



class ShortcutCategoriesManager(ShortcutCategoriesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: ShortcutCategories) -> None:
        pass

shortcut_categories_manager_instance = ShortcutCategoriesManager()