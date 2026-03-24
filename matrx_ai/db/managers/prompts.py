# File: db/managers/prompts.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from db.models import Prompts


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = PromptsView on your manager subclass,
# or pass view_class=PromptsView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class PromptsView(ModelView[Prompts]):
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
#   - JSON Schema generation: PromptsSchema.model_json_schema()
#   - Typed API responses: PromptsSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=PromptsSchema)
#   async def get_prompts(id: str):
#       item = await prompts_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    PromptsSchema = build_output_schema(Prompts)
except ImportError:
    PromptsSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class PromptsDTO(BaseDTO[Prompts]):
    id: str

    async def _initialize_dto(self, model: Prompts) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: Prompts) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: Prompts) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: Prompts) -> None:
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
#   1. Quick: set view_class = PromptsView  (replaces DTO automatically)
#   2. Explicit: super().__init__(Prompts, view_class=PromptsView)
# ---------------------------------------------------------------------------

class PromptsBase(BaseManager[Prompts]):
    view_class = None  # DTO is used by default; set to PromptsView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Prompts, dto_class=dto_class or PromptsDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Prompts) -> None:
        pass

    async def create_prompts(self, **data: Any) -> Prompts:
        return await self.create_item(**data)

    async def delete_prompts(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_prompts_with_all_related(self, id: Any) -> tuple[Prompts, Any]:
        return await self.get_item_with_all_related(id)

    async def load_prompts_by_id(self, id: Any) -> Prompts:
        return await self.load_by_id(id)

    async def load_prompts(self, use_cache: bool = True, **kwargs: Any) -> Prompts:
        return await self.load_item(use_cache, **kwargs)

    async def update_prompts(self, id: Any, **updates: Any) -> Prompts:
        return await self.update_item(id, **updates)

    async def load_prompts(self, **kwargs: Any) -> list[Prompts]:
        return await self.load_items(**kwargs)

    async def filter_prompts(self, **kwargs: Any) -> list[Prompts]:
        return await self.filter_items(**kwargs)

    async def get_or_create_prompts(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Prompts | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_prompts_with_ai_model(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'ai_model')

    async def get_prompts_with_ai_model(self) -> list[Any]:
        return await self.get_items_with_related('ai_model')

    async def get_prompts_with_organizations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organizations')

    async def get_prompts_with_organizations(self) -> list[Any]:
        return await self.get_items_with_related('organizations')

    async def get_prompts_with_projects(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'projects')

    async def get_prompts_with_projects(self) -> list[Any]:
        return await self.get_items_with_related('projects')

    async def get_prompts_with_tasks(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'tasks')

    async def get_prompts_with_tasks(self) -> list[Any]:
        return await self.get_items_with_related('tasks')

    async def get_prompts_with_workspaces(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workspaces')

    async def get_prompts_with_workspaces(self) -> list[Any]:
        return await self.get_items_with_related('workspaces')

    async def get_prompts_with_system_prompts_new(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'system_prompts_new')

    async def get_prompts_with_system_prompts_new(self) -> list[Any]:
        return await self.get_items_with_related('system_prompts_new')

    async def get_prompts_with_prompt_actions(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_actions')

    async def get_prompts_with_prompt_actions(self) -> list[Any]:
        return await self.get_items_with_related('prompt_actions')

    async def get_prompts_with_system_prompts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'system_prompts')

    async def get_prompts_with_system_prompts(self) -> list[Any]:
        return await self.get_items_with_related('system_prompts')

    async def get_prompts_with_prompt_versions(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_versions')

    async def get_prompts_with_prompt_versions(self) -> list[Any]:
        return await self.get_items_with_related('prompt_versions')

    async def get_prompts_with_prompt_builtins(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_builtins')

    async def get_prompts_with_prompt_builtins(self) -> list[Any]:
        return await self.get_items_with_related('prompt_builtins')

    async def get_prompts_with_prompt_apps(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompt_apps')

    async def get_prompts_with_prompt_apps(self) -> list[Any]:
        return await self.get_items_with_related('prompt_apps')

    async def load_prompts_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_prompts_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_prompts_by_tags(self, tags: Any) -> list[Any]:
        return await self.load_items(tags=tags)

    async def filter_prompts_by_tags(self, tags: Any) -> list[Any]:
        return await self.filter_items(tags=tags)

    async def load_prompts_by_model_id(self, model_id: Any) -> list[Any]:
        return await self.load_items(model_id=model_id)

    async def filter_prompts_by_model_id(self, model_id: Any) -> list[Any]:
        return await self.filter_items(model_id=model_id)

    async def load_prompts_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.load_items(organization_id=organization_id)

    async def filter_prompts_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.filter_items(organization_id=organization_id)

    async def load_prompts_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.load_items(workspace_id=workspace_id)

    async def filter_prompts_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.filter_items(workspace_id=workspace_id)

    async def load_prompts_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.load_items(project_id=project_id)

    async def filter_prompts_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.filter_items(project_id=project_id)

    async def load_prompts_by_task_id(self, task_id: Any) -> list[Any]:
        return await self.load_items(task_id=task_id)

    async def filter_prompts_by_task_id(self, task_id: Any) -> list[Any]:
        return await self.filter_items(task_id=task_id)

    async def load_prompts_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_prompts_ids(self) -> set[Any]:
        return self.active_item_ids



class PromptsManager(PromptsBase):
    _instance: PromptsManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> PromptsManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Prompts) -> None:
        pass

prompts_manager_instance = PromptsManager()