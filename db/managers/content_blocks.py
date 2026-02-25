# File: db/managers/content_blocks.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO, ModelView
from db.models import ContentBlocks
from typing import Optional, Type, Any


# ---------------------------------------------------------------------------
# ModelView (new) — preferred projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# ---------------------------------------------------------------------------

class ContentBlocksView(ModelView):
    """
    Declarative view for ContentBlocks.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: ContentBlocks) -> str:
            return model.name.title()
    """

    prefetch: list = ['shortcut_categories']
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
# Existing imports of ContentBlocksDTO from this file continue to work.
# Migrate business logic to ContentBlocksView when ready.
# ---------------------------------------------------------------------------

@dataclass
class ContentBlocksDTO(BaseDTO):
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
#   super().__init__(ContentBlocks, dto_class=ContentBlocksDTO)
# ---------------------------------------------------------------------------

class ContentBlocksBase(BaseManager[ContentBlocks]):
    view_class = ContentBlocksView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(ContentBlocks)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: ContentBlocks) -> None:
        pass

    async def create_content_blocks(self, **data):
        return await self.create_item(**data)

    async def delete_content_blocks(self, id):
        return await self.delete_item(id)

    async def get_content_blocks_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_content_blocks_by_id(self, id):
        return await self.load_by_id(id)

    async def load_content_blocks(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_content_blocks(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_content_block(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_content_block(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_content_blocks_with_shortcut_categories(self, id):
        return await self.get_item_with_related(id, 'shortcut_categories')

    async def get_content_block_with_shortcut_categories(self):
        return await self.get_items_with_related('shortcut_categories')

    async def load_content_block_by_category_id(self, category_id):
        return await self.load_items(category_id=category_id)

    async def filter_content_block_by_category_id(self, category_id):
        return await self.filter_items(category_id=category_id)

    async def load_content_block_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_content_blocks_ids(self):
        return self.active_item_ids



class ContentBlocksManager(ContentBlocksBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ContentBlocksManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: ContentBlocks) -> None:
        pass

content_blocks_manager_instance = ContentBlocksManager()