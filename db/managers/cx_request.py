# File: db/managers/cx_request.py
from matrx_utils import vcprint


from matrx_orm import BaseManager, ModelView
from db.models import CxRequest
from typing import Optional, Type, Any


class CxRequestView(ModelView):
    """
    Declarative view for CxRequest.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: CxRequest) -> str:
            return model.name.title()
    """

    prefetch: list = ['ai_model', 'cx_conversation', 'cx_user_request']
    exclude: list = []
    inline_fk: dict = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


class CxRequestBase(BaseManager[CxRequest]):
    view_class = CxRequestView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(CxRequest)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: CxRequest) -> None:
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

    async def _initialize_runtime_data(self, item: CxRequest) -> None:
        pass

cx_request_manager_instance = CxRequestManager()