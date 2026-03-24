# File: db/managers/org_hierarchy_levels.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from matrx_ai.db.models import OrgHierarchyLevels


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = OrgHierarchyLevelsView on your manager subclass,
# or pass view_class=OrgHierarchyLevelsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class OrgHierarchyLevelsView(ModelView[OrgHierarchyLevels]):
    """
    Declarative view for OrgHierarchyLevels.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: OrgHierarchyLevels) -> str:
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
#   - JSON Schema generation: OrgHierarchyLevelsSchema.model_json_schema()
#   - Typed API responses: OrgHierarchyLevelsSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=OrgHierarchyLevelsSchema)
#   async def get_org_hierarchy_levels(id: str):
#       item = await org_hierarchy_levels_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    OrgHierarchyLevelsSchema = build_output_schema(OrgHierarchyLevels)
except ImportError:
    OrgHierarchyLevelsSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class OrgHierarchyLevelsDTO(BaseDTO[OrgHierarchyLevels]):
    id: str

    async def _initialize_dto(self, model: OrgHierarchyLevels) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: OrgHierarchyLevels) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: OrgHierarchyLevels) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: OrgHierarchyLevels) -> None:
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
#   1. Quick: set view_class = OrgHierarchyLevelsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(OrgHierarchyLevels, view_class=OrgHierarchyLevelsView)
# ---------------------------------------------------------------------------

class OrgHierarchyLevelsBase(BaseManager[OrgHierarchyLevels]):
    view_class = None  # DTO is used by default; set to OrgHierarchyLevelsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(OrgHierarchyLevels, dto_class=dto_class or OrgHierarchyLevelsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: OrgHierarchyLevels) -> None:
        pass

    async def create_org_hierarchy_levels(self, **data: Any) -> OrgHierarchyLevels:
        return await self.create_item(**data)

    async def delete_org_hierarchy_levels(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_org_hierarchy_levels_with_all_related(self, id: Any) -> tuple[OrgHierarchyLevels, Any]:
        return await self.get_item_with_all_related(id)

    async def load_org_hierarchy_levels_by_id(self, id: Any) -> OrgHierarchyLevels:
        return await self.load_by_id(id)

    async def load_org_hierarchy_levels(self, use_cache: bool = True, **kwargs: Any) -> OrgHierarchyLevels:
        return await self.load_item(use_cache, **kwargs)

    async def update_org_hierarchy_levels(self, id: Any, **updates: Any) -> OrgHierarchyLevels:
        return await self.update_item(id, **updates)

    async def load_org_hierarchy_levels(self, **kwargs: Any) -> list[OrgHierarchyLevels]:
        return await self.load_items(**kwargs)

    async def filter_org_hierarchy_levels(self, **kwargs: Any) -> list[OrgHierarchyLevels]:
        return await self.filter_items(**kwargs)

    async def get_or_create_org_hierarchy_levels(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> OrgHierarchyLevels | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_org_hierarchy_levels_with_organizations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organizations')

    async def get_org_hierarchy_levels_with_organizations(self) -> list[Any]:
        return await self.get_items_with_related('organizations')

    async def get_org_hierarchy_levels_with_workspaces(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workspaces')

    async def get_org_hierarchy_levels_with_workspaces(self) -> list[Any]:
        return await self.get_items_with_related('workspaces')

    async def load_org_hierarchy_levels_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.load_items(organization_id=organization_id)

    async def filter_org_hierarchy_levels_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.filter_items(organization_id=organization_id)

    async def load_org_hierarchy_levels_by_default_variable_keys(self, default_variable_keys: Any) -> list[Any]:
        return await self.load_items(default_variable_keys=default_variable_keys)

    async def filter_org_hierarchy_levels_by_default_variable_keys(self, default_variable_keys: Any) -> list[Any]:
        return await self.filter_items(default_variable_keys=default_variable_keys)

    async def load_org_hierarchy_levels_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_org_hierarchy_levels_ids(self) -> set[Any]:
        return self.active_item_ids



class OrgHierarchyLevelsManager(OrgHierarchyLevelsBase):
    _instance: OrgHierarchyLevelsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> OrgHierarchyLevelsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: OrgHierarchyLevels) -> None:
        pass

org_hierarchy_levels_manager_instance = OrgHierarchyLevelsManager()