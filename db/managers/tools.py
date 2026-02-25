# File: db/managers/tools.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO, ModelView
from db.models import Tools
from typing import Optional, Type, Any


# ---------------------------------------------------------------------------
# ModelView (new) — preferred projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# ---------------------------------------------------------------------------

class ToolsView(ModelView):
    """
    Declarative view for Tools.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Tools) -> str:
            return model.name.title()
    """

    prefetch: list = ['tool_test_samples', 'tool_ui_components']
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
# Existing imports of ToolsDTO from this file continue to work.
# Migrate business logic to ToolsView when ready.
# ---------------------------------------------------------------------------

@dataclass
class ToolsDTO(BaseDTO):
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
#   super().__init__(Tools, dto_class=ToolsDTO)
# ---------------------------------------------------------------------------

class ToolsBase(BaseManager[Tools]):
    view_class = ToolsView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Tools)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Tools) -> None:
        pass

    async def create_tools(self, **data):
        return await self.create_item(**data)

    async def delete_tools(self, id):
        return await self.delete_item(id)

    async def get_tools_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_tools_by_id(self, id):
        return await self.load_by_id(id)

    async def load_tools(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_tools(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_tool(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_tool(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_tools_with_tool_test_samples(self, id):
        return await self.get_item_with_related(id, 'tool_test_samples')

    async def get_tool_with_tool_test_samples(self):
        return await self.get_items_with_related('tool_test_samples')

    async def get_tools_with_tool_ui_components(self, id):
        return await self.get_item_with_related(id, 'tool_ui_components')

    async def get_tool_with_tool_ui_components(self):
        return await self.get_items_with_related('tool_ui_components')

    async def load_tool_by_tags(self, tags):
        return await self.load_items(tags=tags)

    async def filter_tool_by_tags(self, tags):
        return await self.filter_items(tags=tags)

    async def load_tool_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_tools_ids(self):
        return self.active_item_ids



class ToolsManager(ToolsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ToolsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: Tools) -> None:
        pass

tools_manager_instance = ToolsManager()