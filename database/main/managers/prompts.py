# File: database/main/managers/prompts.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from database.main.models import Prompts
from typing import Optional, Type, Any

@dataclass
class PromptsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, prompts_item):
        '''Override the base initialization method.'''
        self.id = str(prompts_item.id)
        await self._process_core_data(prompts_item)
        await self._process_metadata(prompts_item)
        await self._initial_validation(prompts_item)
        self.initialized = True

    async def _process_core_data(self, prompts_item):
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, prompts_item):
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, prompts_item):
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
            vcprint(dict_data, "[PromptsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class PromptsBase(BaseManager[Prompts]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or PromptsDTO
        super().__init__(Prompts, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, prompts):
        pass

    async def create_prompts(self, **data):
        return await self.create_item(**data)

    async def delete_prompts(self, id):
        return await self.delete_item(id)

    async def get_prompts_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_prompts_by_id(self, id):
        return await self.load_by_id(id)

    async def load_prompts(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_prompts(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_prompt(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_prompt(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_prompts_with_prompt_apps(self, id):
        return await self.get_item_with_related(id, 'prompt_apps')

    async def get_prompt_with_prompt_apps(self):
        return await self.get_items_with_related('prompt_apps')

    async def get_prompts_with_system_prompts_new(self, id):
        return await self.get_item_with_related(id, 'system_prompts_new')

    async def get_prompt_with_system_prompts_new(self):
        return await self.get_items_with_related('system_prompts_new')

    async def get_prompts_with_prompt_builtins(self, id):
        return await self.get_item_with_related(id, 'prompt_builtins')

    async def get_prompt_with_prompt_builtins(self):
        return await self.get_items_with_related('prompt_builtins')

    async def get_prompts_with_prompt_actions(self, id):
        return await self.get_item_with_related(id, 'prompt_actions')

    async def get_prompt_with_prompt_actions(self):
        return await self.get_items_with_related('prompt_actions')

    async def get_prompts_with_system_prompts(self, id):
        return await self.get_item_with_related(id, 'system_prompts')

    async def get_prompt_with_system_prompts(self):
        return await self.get_items_with_related('system_prompts')

    async def load_prompt_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_prompt_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_prompt_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_prompts_ids(self):
        return self.active_item_ids



class PromptsManager(PromptsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PromptsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

prompts_manager_instance = PromptsManager()