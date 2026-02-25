# File: db/managers/cx_media.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from db.models import CxMedia
from typing import Optional, Type, Any

@dataclass
class CxMediaDTO(BaseDTO):
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
            vcprint(dict_data, "[CxMediaDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class CxMediaBase(BaseManager[CxMedia]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or CxMediaDTO
        super().__init__(CxMedia, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, cx_media):
        pass

    async def create_cx_media(self, **data):
        return await self.create_item(**data)

    async def delete_cx_media(self, id):
        return await self.delete_item(id)

    async def get_cx_media_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_cx_media_by_id(self, id):
        return await self.load_by_id(id)

    async def load_cx_media(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_cx_media(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_cx_medias(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_cx_medias(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_cx_media_with_cx_conversation(self, id):
        return await self.get_item_with_related(id, 'cx_conversation')

    async def get_cx_medias_with_cx_conversation(self):
        return await self.get_items_with_related('cx_conversation')

    async def load_cx_medias_by_conversation_id(self, conversation_id):
        return await self.load_items(conversation_id=conversation_id)

    async def filter_cx_medias_by_conversation_id(self, conversation_id):
        return await self.filter_items(conversation_id=conversation_id)

    async def load_cx_medias_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_cx_medias_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_cx_medias_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_cx_media_ids(self):
        return self.active_item_ids



class CxMediaManager(CxMediaBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxMediaManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

cx_media_manager_instance = CxMediaManager()