# File: db/managers/tools.py
from matrx_utils import vcprint


from matrx_orm import BaseManager, ModelView
from db.models import Tools
from typing import Optional, Type, Any


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