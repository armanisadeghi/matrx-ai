# File: database/main/managers/tools.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from database.main.models import Tools
from typing import Optional, Type, Any

@dataclass
class ToolsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, tools_item):
        '''Override the base initialization method.'''
        self.id = str(tools_item.id)
        await self._process_core_data(tools_item)
        await self._process_metadata(tools_item)
        await self._initial_validation(tools_item)
        self.initialized = True

    async def _process_core_data(self, tools_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, tools_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, tools_item):
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self):
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self):
        '''Get the validated dictionary.'''
        validated = await self._final_validation()
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[ToolsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class ToolsBase(BaseManager[Tools]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or ToolsDTO
        super().__init__(Tools, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, tools):
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

    async def exists(self, id):
        return await self.exists(id)

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

tools_manager_instance = ToolsManager()