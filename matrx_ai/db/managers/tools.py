# File: db/managers/tools.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView
from matrx_utils import vcprint

from db.models import Tools


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = ToolsView on your manager subclass,
# or pass view_class=ToolsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class ToolsView(ModelView[Tools]):
    """
    Declarative view for Tools.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Tools) -> str:
            return model.name.title()
    """

    prefetch: list[str] = []
    exclude: list[str] = []
    inline_fk: dict[str, str] = {}

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
class ToolsDTO(BaseDTO[Tools]):
    id: str

    async def _initialize_dto(self, model: Tools) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: Tools) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: Tools) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: Tools) -> None:
        '''Validate fields from the model item.'''
        pass

    async def _final_validation(self) -> bool:
        '''Final validation of the model item.'''
        return True

    async def get_validated_dict(self) -> dict[str, Any]:
        '''Get the validated dictionary.'''
        await self._final_validation()
        return self.to_dict()


# ---------------------------------------------------------------------------
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = ToolsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(Tools, view_class=ToolsView)
# ---------------------------------------------------------------------------

class ToolsBase(BaseManager[Tools]):
    view_class = None  # DTO is used by default; set to ToolsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Tools, dto_class=dto_class or ToolsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Tools) -> None:
        pass

    async def create_tools(self, **data: Any) -> Tools:
        return await self.create_item(**data)

    async def delete_tools(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_tools_with_all_related(self, id: Any) -> tuple[Tools, Any]:
        return await self.get_item_with_all_related(id)

    async def load_tools_by_id(self, id: Any) -> Tools:
        return await self.load_by_id(id)

    async def load_tools(self, use_cache: bool = True, **kwargs: Any) -> Tools:
        return await self.load_item(use_cache, **kwargs)

    async def update_tools(self, id: Any, **updates: Any) -> Tools:
        return await self.update_item(id, **updates)

    async def load_tool(self, **kwargs: Any) -> list[Tools]:
        return await self.load_items(**kwargs)

    async def filter_tool(self, **kwargs: Any) -> list[Tools]:
        return await self.filter_items(**kwargs)

    async def get_or_create_tools(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Tools | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_tools_with_tool_test_samples(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'tool_test_samples')

    async def get_tool_with_tool_test_samples(self) -> list[Any]:
        return await self.get_items_with_related('tool_test_samples')

    async def get_tools_with_tool_ui_components(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'tool_ui_components')

    async def get_tool_with_tool_ui_components(self) -> list[Any]:
        return await self.get_items_with_related('tool_ui_components')

    async def load_tool_by_tags(self, tags: Any) -> list[Any]:
        return await self.load_items(tags=tags)

    async def filter_tool_by_tags(self, tags: Any) -> list[Any]:
        return await self.filter_items(tags=tags)

    async def load_tool_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_tools_ids(self) -> set[Any]:
        return self.active_item_ids



class ToolsManager(ToolsBase):
    _instance: ToolsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> ToolsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Tools) -> None:
        pass

tools_manager_instance = ToolsManager()