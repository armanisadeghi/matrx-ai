# File: db/managers/prompts.py
from matrx_utils import vcprint


from matrx_orm import BaseManager, ModelView
from db.models import Prompts
from typing import Optional, Type, Any


class PromptsView(ModelView):
    """
    Declarative view for Prompts.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Prompts) -> str:
            return model.name.title()
    """

    prefetch: list = ['prompt_apps', 'system_prompts_new', 'prompt_builtins', 'prompt_actions', 'system_prompts']
    exclude: list = []
    inline_fk: dict = {}

    # ------------------------------------------------------------------ #
    # Computed fields — add async methods below.                          #
    # Each method receives the model instance and returns a plain value.  #
    # Errors in computed fields are logged and stored as None —           #
    # they never abort the load.                                          #
    # ------------------------------------------------------------------ #


class PromptsBase(BaseManager[Prompts]):
    view_class = PromptsView

    def __init__(self, view_class: Optional[Type[Any]] = None):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Prompts)

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Prompts) -> None:
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

    async def _initialize_runtime_data(self, item: Prompts) -> None:
        pass

prompts_manager_instance = PromptsManager()