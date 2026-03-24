# File: db/managers/table_data.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from matrx_ai.db.models import TableData


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = TableDataView on your manager subclass,
# or pass view_class=TableDataView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class TableDataView(ModelView[TableData]):
    """
    Declarative view for TableData.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: TableData) -> str:
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
# Pydantic output schema (optional, requires pydantic v2).
# Auto-generated from the model's field definitions.  Useful for:
#   - FastAPI response_model type annotation
#   - JSON Schema generation: TableDataSchema.model_json_schema()
#   - Typed API responses: TableDataSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=TableDataSchema)
#   async def get_table_data(id: str):
#       item = await table_data_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    TableDataSchema = build_output_schema(TableData)
except ImportError:
    TableDataSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class TableDataDTO(BaseDTO[TableData]):
    id: str

    async def _initialize_dto(self, model: TableData) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: TableData) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: TableData) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: TableData) -> None:
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
#   1. Quick: set view_class = TableDataView  (replaces DTO automatically)
#   2. Explicit: super().__init__(TableData, view_class=TableDataView)
# ---------------------------------------------------------------------------

class TableDataBase(BaseManager[TableData]):
    view_class = None  # DTO is used by default; set to TableDataView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(TableData, dto_class=dto_class or TableDataDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: TableData) -> None:
        pass

    async def create_table_data(self, **data: Any) -> TableData:
        return await self.create_item(**data)

    async def delete_table_data(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_table_data_with_all_related(self, id: Any) -> tuple[TableData, Any]:
        return await self.get_item_with_all_related(id)

    async def load_table_data_by_id(self, id: Any) -> TableData:
        return await self.load_by_id(id)

    async def load_table_data(self, use_cache: bool = True, **kwargs: Any) -> TableData:
        return await self.load_item(use_cache, **kwargs)

    async def update_table_data(self, id: Any, **updates: Any) -> TableData:
        return await self.update_item(id, **updates)

    async def load_table_data(self, **kwargs: Any) -> list[TableData]:
        return await self.load_items(**kwargs)

    async def filter_table_data(self, **kwargs: Any) -> list[TableData]:
        return await self.filter_items(**kwargs)

    async def get_or_create_table_data(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> TableData | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_table_data_with_user_tables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_tables')

    async def get_table_data_with_user_tables(self) -> list[Any]:
        return await self.get_items_with_related('user_tables')

    async def load_table_data_by_table_id(self, table_id: Any) -> list[Any]:
        return await self.load_items(table_id=table_id)

    async def filter_table_data_by_table_id(self, table_id: Any) -> list[Any]:
        return await self.filter_items(table_id=table_id)

    async def load_table_data_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_table_data_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_table_data_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_table_data_ids(self) -> set[Any]:
        return self.active_item_ids



class TableDataManager(TableDataBase):
    _instance: TableDataManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> TableDataManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: TableData) -> None:
        pass

table_data_manager_instance = TableDataManager()