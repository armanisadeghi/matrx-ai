# File: database/main/managers/cx_request.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from database.main.models import CxRequest
from typing import Optional, Type, Any

@dataclass
class CxRequestDTO(BaseDTO):
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
            vcprint(dict_data, "[CxRequestDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class CxRequestBase(BaseManager[CxRequest]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or CxRequestDTO
        super().__init__(CxRequest, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_request):
        pass

    async def create_cx_request(self, **data):
        return await self.create_item(**data)

    async def delete_cx_request(self, id):
        return await self.delete_item(id)

    async def get_cx_request_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_cx_request_by_id(self, id):
        return await self.load_by_id(id)

    async def load_cx_request(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_cx_request(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_cx_requests(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_cx_requests(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_cx_request_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_cx_requests_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def get_cx_request_with_cx_conversation(self, id):
        return await self.get_item_with_related(id, 'cx_conversation')

    async def get_cx_requests_with_cx_conversation(self):
        return await self.get_items_with_related('cx_conversation')

    async def get_cx_request_with_cx_user_request(self, id):
        return await self.get_item_with_related(id, 'cx_user_request')

    async def get_cx_requests_with_cx_user_request(self):
        return await self.get_items_with_related('cx_user_request')

    async def load_cx_requests_by_user_request_id(self, user_request_id):
        return await self.load_items(user_request_id=user_request_id)

    async def filter_cx_requests_by_user_request_id(self, user_request_id):
        return await self.filter_items(user_request_id=user_request_id)

    async def load_cx_requests_by_conversation_id(self, conversation_id):
        return await self.load_items(conversation_id=conversation_id)

    async def filter_cx_requests_by_conversation_id(self, conversation_id):
        return await self.filter_items(conversation_id=conversation_id)

    async def load_cx_requests_by_ai_model_id(self, ai_model_id):
        return await self.load_items(ai_model_id=ai_model_id)

    async def filter_cx_requests_by_ai_model_id(self, ai_model_id):
        return await self.filter_items(ai_model_id=ai_model_id)

    async def load_cx_requests_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_cx_request_ids(self):
        return self.active_item_ids



class CxRequestManager(CxRequestBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxRequestManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_request_manager_instance = CxRequestManager()