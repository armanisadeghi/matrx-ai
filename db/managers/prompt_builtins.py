# File: db/managers/prompt_builtins.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from db.models import PromptBuiltins
from typing import Optional, Type, Any

@dataclass
class PromptBuiltinsDTO(BaseDTO):
    id: str

    async def _initialize_dto(self, model):
        '''Override the base initialization method.'''
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
        dict_data = self.to_dict()
        if not validated:
            vcprint(dict_data, "[PromptBuiltinsDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class PromptBuiltinsBase(BaseManager[PromptBuiltins]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or PromptBuiltinsDTO
        super().__init__(PromptBuiltins, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: PromptBuiltins) -> None:
        pass

    async def create_prompt_builtins(self, **data):
        return await self.create_item(**data)

    async def delete_prompt_builtins(self, id):
        return await self.delete_item(id)

    async def get_prompt_builtins_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_prompt_builtins_by_id(self, id):
        return await self.load_by_id(id)

    async def load_prompt_builtins(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_prompt_builtins(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_prompt_builtin(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_prompt_builtin(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_prompt_builtins_with_prompts(self, id):
        return await self.get_item_with_related(id, 'prompts')

    async def get_prompt_builtin_with_prompts(self):
        return await self.get_items_with_related('prompts')

    async def get_prompt_builtins_with_prompt_shortcuts(self, id):
        return await self.get_item_with_related(id, 'prompt_shortcuts')

    async def get_prompt_builtin_with_prompt_shortcuts(self):
        return await self.get_items_with_related('prompt_shortcuts')

    async def get_prompt_builtins_with_prompt_actions(self, id):
        return await self.get_item_with_related(id, 'prompt_actions')

    async def get_prompt_builtin_with_prompt_actions(self):
        return await self.get_items_with_related('prompt_actions')

    async def load_prompt_builtin_by_created_by_user_id(self, created_by_user_id):
        return await self.load_items(created_by_user_id=created_by_user_id)

    async def filter_prompt_builtin_by_created_by_user_id(self, created_by_user_id):
        return await self.filter_items(created_by_user_id=created_by_user_id)

    async def load_prompt_builtin_by_source_prompt_id(self, source_prompt_id):
        return await self.load_items(source_prompt_id=source_prompt_id)

    async def filter_prompt_builtin_by_source_prompt_id(self, source_prompt_id):
        return await self.filter_items(source_prompt_id=source_prompt_id)

    async def load_prompt_builtin_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_prompt_builtins_ids(self):
        return self.active_item_ids



class PromptBuiltinsManager(PromptBuiltinsBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PromptBuiltinsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

prompt_builtins_manager_instance = PromptBuiltinsManager()