# File: db/managers/cx_conversation.py
from matrx_utils import vcprint


from dataclasses import dataclass
from matrx_orm import BaseManager, BaseDTO, ModelView
from db.models import CxConversation
from typing import Optional, Type, Any


# ---------------------------------------------------------------------------
# ModelView (new) — preferred projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# ---------------------------------------------------------------------------

class CxConversationView(ModelView):
    """
    Declarative view for CxConversation.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: CxConversation) -> str:
            return model.name.title()
    """

    prefetch: list = ['ai_model', 'self_reference', 'cx_tool_call', 'cx_message', 'cx_media', 'cx_user_request', 'cx_request']
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
# Existing imports of CxConversationDTO from this file continue to work.
# Migrate business logic to CxConversationView when ready.
# ---------------------------------------------------------------------------

@dataclass
class CxConversationDTO(BaseDTO):
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
#   super().__init__(CxConversation, dto_class=CxConversationDTO)
# ---------------------------------------------------------------------------

class CxConversationBase(BaseManager[CxConversation]):
    view_class = CxConversationView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(CxConversation)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: CxConversation) -> None:
        pass

    async def create_cx_conversation(self, **data):
        return await self.create_item(**data)

    async def delete_cx_conversation(self, id):
        return await self.delete_item(id)

    async def get_cx_conversation_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_cx_conversation_by_id(self, id):
        return await self.load_by_id(id)

    async def load_cx_conversation(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_cx_conversation(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_cx_conversations(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_cx_conversations(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_cx_conversation_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_cx_conversations_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def get_cx_conversation_with_self_reference(self, id):
        return await self.get_item_with_related(id, 'self_reference')

    async def get_cx_conversations_with_self_reference(self):
        return await self.get_items_with_related('self_reference')

    async def get_cx_conversation_with_cx_tool_call(self, id):
        return await self.get_item_with_related(id, 'cx_tool_call')

    async def get_cx_conversations_with_cx_tool_call(self):
        return await self.get_items_with_related('cx_tool_call')

    async def get_cx_conversation_with_cx_message(self, id):
        return await self.get_item_with_related(id, 'cx_message')

    async def get_cx_conversations_with_cx_message(self):
        return await self.get_items_with_related('cx_message')

    async def get_cx_conversation_with_cx_media(self, id):
        return await self.get_item_with_related(id, 'cx_media')

    async def get_cx_conversations_with_cx_media(self):
        return await self.get_items_with_related('cx_media')

    async def get_cx_conversation_with_cx_user_request(self, id):
        return await self.get_item_with_related(id, 'cx_user_request')

    async def get_cx_conversations_with_cx_user_request(self):
        return await self.get_items_with_related('cx_user_request')

    async def get_cx_conversation_with_cx_request(self, id):
        return await self.get_item_with_related(id, 'cx_request')

    async def get_cx_conversations_with_cx_request(self):
        return await self.get_items_with_related('cx_request')

    async def load_cx_conversations_by_user_id(self, user_id):
        return await self.load_items(user_id=user_id)

    async def filter_cx_conversations_by_user_id(self, user_id):
        return await self.filter_items(user_id=user_id)

    async def load_cx_conversations_by_forked_from_id(self, forked_from_id):
        return await self.load_items(forked_from_id=forked_from_id)

    async def filter_cx_conversations_by_forked_from_id(self, forked_from_id):
        return await self.filter_items(forked_from_id=forked_from_id)

    async def load_cx_conversations_by_ai_model_id(self, ai_model_id):
        return await self.load_items(ai_model_id=ai_model_id)

    async def filter_cx_conversations_by_ai_model_id(self, ai_model_id):
        return await self.filter_items(ai_model_id=ai_model_id)

    async def load_cx_conversations_by_parent_conversation_id(self, parent_conversation_id):
        return await self.load_items(parent_conversation_id=parent_conversation_id)

    async def filter_cx_conversations_by_parent_conversation_id(self, parent_conversation_id):
        return await self.filter_items(parent_conversation_id=parent_conversation_id)

    async def load_cx_conversations_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_cx_conversation_ids(self):
        return self.active_item_ids



class CxConversationManager(CxConversationBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(CxConversationManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: CxConversation) -> None:
        pass

cx_conversation_manager_instance = CxConversationManager()