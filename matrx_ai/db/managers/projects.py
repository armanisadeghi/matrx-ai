# File: db/managers/projects.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from db.models import Projects


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = ProjectsView on your manager subclass,
# or pass view_class=ProjectsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class ProjectsView(ModelView[Projects]):
    """
    Declarative view for Projects.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Projects) -> str:
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
#   - JSON Schema generation: ProjectsSchema.model_json_schema()
#   - Typed API responses: ProjectsSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=ProjectsSchema)
#   async def get_projects(id: str):
#       item = await projects_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    ProjectsSchema = build_output_schema(Projects)
except ImportError:
    ProjectsSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class ProjectsDTO(BaseDTO[Projects]):
    id: str

    async def _initialize_dto(self, model: Projects) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: Projects) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: Projects) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: Projects) -> None:
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
#   1. Quick: set view_class = ProjectsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(Projects, view_class=ProjectsView)
# ---------------------------------------------------------------------------

class ProjectsBase(BaseManager[Projects]):
    view_class = None  # DTO is used by default; set to ProjectsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Projects, dto_class=dto_class or ProjectsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Projects) -> None:
        pass

    async def create_projects(self, **data: Any) -> Projects:
        return await self.create_item(**data)

    async def delete_projects(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_projects_with_all_related(self, id: Any) -> tuple[Projects, Any]:
        return await self.get_item_with_all_related(id)

    async def load_projects_by_id(self, id: Any) -> Projects:
        return await self.load_by_id(id)

    async def load_projects(self, use_cache: bool = True, **kwargs: Any) -> Projects:
        return await self.load_item(use_cache, **kwargs)

    async def update_projects(self, id: Any, **updates: Any) -> Projects:
        return await self.update_item(id, **updates)

    async def load_projects(self, **kwargs: Any) -> list[Projects]:
        return await self.load_items(**kwargs)

    async def filter_projects(self, **kwargs: Any) -> list[Projects]:
        return await self.filter_items(**kwargs)

    async def get_or_create_projects(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Projects | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_projects_with_organizations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organizations')

    async def get_projects_with_organizations(self) -> list[Any]:
        return await self.get_items_with_related('organizations')

    async def get_projects_with_workspaces(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workspaces')

    async def get_projects_with_workspaces(self) -> list[Any]:
        return await self.get_items_with_related('workspaces')

    async def get_projects_with_app_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'app_instances')

    async def get_projects_with_app_instances(self) -> list[Any]:
        return await self.get_items_with_related('app_instances')

    async def get_projects_with_broker_values(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'broker_values')

    async def get_projects_with_broker_values(self) -> list[Any]:
        return await self.get_items_with_related('broker_values')

    async def get_projects_with_canvas_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'canvas_items')

    async def get_projects_with_canvas_items(self) -> list[Any]:
        return await self.get_items_with_related('canvas_items')

    async def get_projects_with_context_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_items')

    async def get_projects_with_context_items(self) -> list[Any]:
        return await self.get_items_with_related('context_items')

    async def get_projects_with_context_variables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_variables')

    async def get_projects_with_context_variables(self) -> list[Any]:
        return await self.get_items_with_related('context_variables')

    async def get_projects_with_cx_conversation(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_conversation')

    async def get_projects_with_cx_conversation(self) -> list[Any]:
        return await self.get_items_with_related('cx_conversation')

    async def get_projects_with_notes(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'notes')

    async def get_projects_with_notes(self) -> list[Any]:
        return await self.get_items_with_related('notes')

    async def get_projects_with_project_invitations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'project_invitations')

    async def get_projects_with_project_invitations(self) -> list[Any]:
        return await self.get_items_with_related('project_invitations')

    async def get_projects_with_project_members(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'project_members')

    async def get_projects_with_project_members(self) -> list[Any]:
        return await self.get_items_with_related('project_members')

    async def get_projects_with_prompts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompts')

    async def get_projects_with_prompts(self) -> list[Any]:
        return await self.get_items_with_related('prompts')

    async def get_projects_with_rs_topic(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'rs_topic')

    async def get_projects_with_rs_topic(self) -> list[Any]:
        return await self.get_items_with_related('rs_topic')

    async def get_projects_with_sandbox_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'sandbox_instances')

    async def get_projects_with_sandbox_instances(self) -> list[Any]:
        return await self.get_items_with_related('sandbox_instances')

    async def get_projects_with_tasks(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'tasks')

    async def get_projects_with_tasks(self) -> list[Any]:
        return await self.get_items_with_related('tasks')

    async def get_projects_with_transcripts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'transcripts')

    async def get_projects_with_transcripts(self) -> list[Any]:
        return await self.get_items_with_related('transcripts')

    async def get_projects_with_user_active_context(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_active_context')

    async def get_projects_with_user_active_context(self) -> list[Any]:
        return await self.get_items_with_related('user_active_context')

    async def get_projects_with_user_files(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_files')

    async def get_projects_with_user_files(self) -> list[Any]:
        return await self.get_items_with_related('user_files')

    async def get_projects_with_user_tables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_tables')

    async def get_projects_with_user_tables(self) -> list[Any]:
        return await self.get_items_with_related('user_tables')

    async def get_projects_with_workflow(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workflow')

    async def get_projects_with_workflow(self) -> list[Any]:
        return await self.get_items_with_related('workflow')

    async def load_projects_by_created_by(self, created_by: Any) -> list[Any]:
        return await self.load_items(created_by=created_by)

    async def filter_projects_by_created_by(self, created_by: Any) -> list[Any]:
        return await self.filter_items(created_by=created_by)

    async def load_projects_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.load_items(organization_id=organization_id)

    async def filter_projects_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.filter_items(organization_id=organization_id)

    async def load_projects_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.load_items(workspace_id=workspace_id)

    async def filter_projects_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.filter_items(workspace_id=workspace_id)

    async def load_projects_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_projects_ids(self) -> set[Any]:
        return self.active_item_ids



class ProjectsManager(ProjectsBase):
    _instance: ProjectsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> ProjectsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Projects) -> None:
        pass

projects_manager_instance = ProjectsManager()