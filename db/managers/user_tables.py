# File: db/managers/user_tables.py
from matrx_utils import vcprint


from matrx_orm import BaseManager, ModelView
from db.models import UserTables
from typing import Optional, Type, Any


class UserTablesView(ModelView):
    """
    Declarative view for UserTables.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: UserTables) -> str:
            return model.name.title()
    """

    prefetch: list = ['table_data', 'table_fields']
    exclude: list = []
    inline_fk: dict = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


class UserTablesBase(BaseManager[UserTables]):
    view_class = UserTablesView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(UserTables)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: UserTables) -> None:
        pass

    async def create_user_tables(self, **data):
        return await self.create_item(**data)

    async def delete_user_tables(self, id):
        return await self.delete_item(id)

    async def get_user_tables_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_user_tables_by_id(self, id):
        return await self.load_by_id(id)

    async def load_user_tables(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_user_tables(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_user_table(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_user_table(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_user_tables_with_table_data(self, id):
        return await self.get_item_with_related(id, 'table_data')

    async def get_user_table_with_table_data(self):
        return await self.get_items_with_related('table_data')

    async def get_user_tables_with_table_fields(self, id):
        return await self.get_item_with_related(id, 'table_fields')

    async def get_user_table_with_table_fields(self):
        return await self.get_items_with_related('table_fields')

    async def load_user_table_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_user_table_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_user_table_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_user_tables_ids(self):
        return self.active_item_ids



class UserTablesManager(UserTablesBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(UserTablesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: UserTables) -> None:
        pass

user_tables_manager_instance = UserTablesManager()