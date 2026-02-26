# File: db/managers/ai_provider.py

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from db.models import AiProvider


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = AiProviderView on your manager subclass,
# or pass view_class=AiProviderView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class AiProviderView(ModelView):
    """
    Declarative view for AiProvider.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: AiProvider) -> str:
            return model.name.title()
    """

    prefetch: list = []
    exclude: list = []
    inline_fk: dict = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class AiProviderDTO(BaseDTO):
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
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = AiProviderView  (replaces DTO automatically)
#   2. Explicit: super().__init__(AiProvider, view_class=AiProviderView)
# ---------------------------------------------------------------------------

class AiProviderBase(BaseManager[AiProvider]):
    view_class = None  # DTO is used by default; set to AiProviderView to opt in

    def __init__(self, view_class: type[Any] | None = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(AiProvider, dto_class=AiProviderDTO)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: AiProvider) -> None:
        pass

    async def create_ai_provider(self, **data):
        return await self.create_item(**data)

    async def delete_ai_provider(self, id):
        return await self.delete_item(id)

    async def get_ai_provider_with_all_related(self, id):
        return await self.get_item_with_all_related(id)

    async def load_ai_provider_by_id(self, id):
        return await self.load_by_id(id)

    async def load_ai_provider(self, use_cache=True, **kwargs):
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_provider(self, id, **updates):
        return await self.update_item(id, **updates)

    async def load_ai_providers(self, **kwargs):
        return await self.load_items(**kwargs)

    async def filter_ai_providers(self, **kwargs):
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs):
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_provider_with_ai_settings(self, id):
        return await self.get_item_with_related(id, 'ai_settings')

    async def get_ai_providers_with_ai_settings(self):
        return await self.get_items_with_related('ai_settings')

    async def get_ai_provider_with_ai_model(self, id):
        return await self.get_item_with_related(id, 'ai_model')

    async def get_ai_providers_with_ai_model(self):
        return await self.get_items_with_related('ai_model')

    async def load_ai_providers_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_provider_ids(self):
        return self.active_item_ids



class AiProviderManager(AiProviderBase):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def _initialize_runtime_data(self, item: AiProvider) -> None:
        pass

ai_provider_manager_instance = AiProviderManager()