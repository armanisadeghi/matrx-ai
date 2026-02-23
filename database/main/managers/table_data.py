# File: database/main/managers/table_data.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO
from database.main.models import TableData
from typing import Optional, Type, Any

@dataclass
class TableDataDTO(BaseDTO):
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
            vcprint(dict_data, "[TableDataDTO] Validation Failed", verbose=True, pretty=True, color="red")
        return dict_data



class TableDataBase(BaseManager[TableData]):
    def __init__(self, dto_class: Optional[Type[Any]] = None):
        self.dto_class = dto_class or TableDataDTO
        super().__init__(TableData, self.dto_class)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, table_data):
        pass

    async def create_table_data(self, **data):
        return await self.create_item(**data)

    async def delete_table_data(self, id):
        return await self.delete_item(id)

    async def get_table_data_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_table_data_by_id(self, id):
        return await self.load_by_id(id)

    async def load_table_data(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_table_data(self, id, **updates):
        return await self.update_item(id, **updates)

    async def exists(self, id):
        return await self.exists(id)

    async def load_table_datas(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_table_datas(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_table_data_with_user_tables(self, id):
        return await self.get_item_with_related(id, 'user_tables')

    async def get_table_datas_with_user_tables(self):
        return await self.get_items_with_related('user_tables')

    async def load_table_datas_by_table_id(self, table_id):
        return await self.load_items(table_id=table_id)

    async def filter_table_datas_by_table_id(self, table_id):
        return await self.filter_items(table_id=table_id)

    async def load_table_datas_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_table_datas_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_table_datas_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_table_data_ids(self):
        return self.active_item_ids



class TableDataManager(TableDataBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(TableDataManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

table_data_manager_instance = TableDataManager()