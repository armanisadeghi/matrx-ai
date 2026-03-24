# File: db/managers/organizations.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from db.models import Organizations


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = OrganizationsView on your manager subclass,
# or pass view_class=OrganizationsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class OrganizationsView(ModelView[Organizations]):
    """
    Declarative view for Organizations.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Organizations) -> str:
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
#   - JSON Schema generation: OrganizationsSchema.model_json_schema()
#   - Typed API responses: OrganizationsSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=OrganizationsSchema)
#   async def get_organizations(id: str):
#       item = await organizations_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    OrganizationsSchema = build_output_schema(Organizations)
except ImportError:
    OrganizationsSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class OrganizationsDTO(BaseDTO[Organizations]):
    id: str

    async def _initialize_dto(self, model: Organizations) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: Organizations) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: Organizations) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: Organizations) -> None:
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
#   1. Quick: set view_class = OrganizationsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(Organizations, view_class=OrganizationsView)
# ---------------------------------------------------------------------------

class OrganizationsBase(BaseManager[Organizations]):
    view_class = None  # DTO is used by default; set to OrganizationsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Organizations, dto_class=dto_class or OrganizationsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Organizations) -> None:
        pass

    async def create_organizations(self, **data: Any) -> Organizations:
        return await self.create_item(**data)

    async def delete_organizations(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_organizations_with_all_related(self, id: Any) -> tuple[Organizations, Any]:
        return await self.get_item_with_all_related(id)

    async def load_organizations_by_id(self, id: Any) -> Organizations:
        return await self.load_by_id(id)

    async def load_organizations(self, use_cache: bool = True, **kwargs: Any) -> Organizations:
        return await self.load_item(use_cache, **kwargs)

    async def update_organizations(self, id: Any, **updates: Any) -> Organizations:
        return await self.update_item(id, **updates)

    async def load_organizations(self, **kwargs: Any) -> list[Organizations]:
        return await self.load_items(**kwargs)

    async def filter_organizations(self, **kwargs: Any) -> list[Organizations]:
        return await self.filter_items(**kwargs)

    async def get_or_create_organizations(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Organizations | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_organizations_with_workspaces(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workspaces')

    async def get_organizations_with_workspaces(self) -> list[Any]:
        return await self.get_items_with_related('workspaces')

    async def get_organizations_with_context_variables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_variables')

    async def get_organizations_with_context_variables(self) -> list[Any]:
        return await self.get_items_with_related('context_variables')

    async def get_organizations_with_permissions(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'permissions')

    async def get_organizations_with_permissions(self) -> list[Any]:
        return await self.get_items_with_related('permissions')

    async def get_organizations_with_organization_members(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organization_members')

    async def get_organizations_with_organization_members(self) -> list[Any]:
        return await self.get_items_with_related('organization_members')

    async def get_organizations_with_user_active_context(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_active_context')

    async def get_organizations_with_user_active_context(self) -> list[Any]:
        return await self.get_items_with_related('user_active_context')

    async def get_organizations_with_broker_values(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'broker_values')

    async def get_organizations_with_broker_values(self) -> list[Any]:
        return await self.get_items_with_related('broker_values')

    async def get_organizations_with_user_files(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_files')

    async def get_organizations_with_user_files(self) -> list[Any]:
        return await self.get_items_with_related('user_files')

    async def get_organizations_with_projects(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'projects')

    async def get_organizations_with_projects(self) -> list[Any]:
        return await self.get_items_with_related('projects')

    async def get_organizations_with_organization_invitations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organization_invitations')

    async def get_organizations_with_organization_invitations(self) -> list[Any]:
        return await self.get_items_with_related('organization_invitations')

    async def get_organizations_with_cx_conversation(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_conversation')

    async def get_organizations_with_cx_conversation(self) -> list[Any]:
        return await self.get_items_with_related('cx_conversation')

    async def get_organizations_with_sandbox_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'sandbox_instances')

    async def get_organizations_with_sandbox_instances(self) -> list[Any]:
        return await self.get_items_with_related('sandbox_instances')

    async def get_organizations_with_context_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_items')

    async def get_organizations_with_context_items(self) -> list[Any]:
        return await self.get_items_with_related('context_items')

    async def get_organizations_with_app_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'app_instances')

    async def get_organizations_with_app_instances(self) -> list[Any]:
        return await self.get_items_with_related('app_instances')

    async def get_organizations_with_notes(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'notes')

    async def get_organizations_with_notes(self) -> list[Any]:
        return await self.get_items_with_related('notes')

    async def get_organizations_with_user_tables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_tables')

    async def get_organizations_with_user_tables(self) -> list[Any]:
        return await self.get_items_with_related('user_tables')

    async def get_organizations_with_transcripts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'transcripts')

    async def get_organizations_with_transcripts(self) -> list[Any]:
        return await self.get_items_with_related('transcripts')

    async def get_organizations_with_workflow(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workflow')

    async def get_organizations_with_workflow(self) -> list[Any]:
        return await self.get_items_with_related('workflow')

    async def get_organizations_with_canvas_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'canvas_items')

    async def get_organizations_with_canvas_items(self) -> list[Any]:
        return await self.get_items_with_related('canvas_items')

    async def get_organizations_with_prompts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompts')

    async def get_organizations_with_prompts(self) -> list[Any]:
        return await self.get_items_with_related('prompts')

    async def load_organizations_by_created_by(self, created_by: Any) -> list[Any]:
        return await self.load_items(created_by=created_by)

    async def filter_organizations_by_created_by(self, created_by: Any) -> list[Any]:
        return await self.filter_items(created_by=created_by)

    async def load_organizations_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_organizations_ids(self) -> set[Any]:
        return self.active_item_ids



class OrganizationsManager(OrganizationsBase):
    _instance: OrganizationsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> OrganizationsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Organizations) -> None:
        pass

organizations_manager_instance = OrganizationsManager()