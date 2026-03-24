# File: db/managers/tasks.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from db.models import Tasks


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = TasksView on your manager subclass,
# or pass view_class=TasksView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class TasksView(ModelView[Tasks]):
    """
    Declarative view for Tasks.

    Configure what gets fetched and shaped automatically on every load:

      prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
      exclude     — model field names to omit from to_dict() output
      inline_fk   — replace FK id columns with the full related object
                    e.g. {"customer_id": "customer"}

    Add async methods (no leading underscore) for computed fields:

        async def display_name(self, model: Tasks) -> str:
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
#   - JSON Schema generation: TasksSchema.model_json_schema()
#   - Typed API responses: TasksSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=TasksSchema)
#   async def get_tasks(id: str):
#       item = await tasks_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    TasksSchema = build_output_schema(Tasks)
except ImportError:
    TasksSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class TasksDTO(BaseDTO[Tasks]):
    id: str

    async def _initialize_dto(self, model: Tasks) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: Tasks) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: Tasks) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: Tasks) -> None:
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
#   1. Quick: set view_class = TasksView  (replaces DTO automatically)
#   2. Explicit: super().__init__(Tasks, view_class=TasksView)
# ---------------------------------------------------------------------------

class TasksBase(BaseManager[Tasks]):
    view_class = None  # DTO is used by default; set to TasksView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(Tasks, dto_class=dto_class or TasksDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: Tasks) -> None:
        pass

    async def create_tasks(self, **data: Any) -> Tasks:
        return await self.create_item(**data)

    async def delete_tasks(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_tasks_with_all_related(self, id: Any) -> tuple[Tasks, Any]:
        return await self.get_item_with_all_related(id)

    async def load_tasks_by_id(self, id: Any) -> Tasks:
        return await self.load_by_id(id)

    async def load_tasks(self, use_cache: bool = True, **kwargs: Any) -> Tasks:
        return await self.load_item(use_cache, **kwargs)

    async def update_tasks(self, id: Any, **updates: Any) -> Tasks:
        return await self.update_item(id, **updates)

    async def load_tasks(self, **kwargs: Any) -> list[Tasks]:
        return await self.load_items(**kwargs)

    async def filter_tasks(self, **kwargs: Any) -> list[Tasks]:
        return await self.filter_items(**kwargs)

    async def get_or_create_tasks(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Tasks | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_tasks_with_self_reference(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'self_reference')

    async def get_tasks_with_self_reference(self) -> list[Any]:
        return await self.get_items_with_related('self_reference')

    async def get_tasks_with_projects(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'projects')

    async def get_tasks_with_projects(self) -> list[Any]:
        return await self.get_items_with_related('projects')

    async def get_tasks_with_task_assignments(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'task_assignments')

    async def get_tasks_with_task_assignments(self) -> list[Any]:
        return await self.get_items_with_related('task_assignments')

    async def get_tasks_with_task_attachments(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'task_attachments')

    async def get_tasks_with_task_attachments(self) -> list[Any]:
        return await self.get_items_with_related('task_attachments')

    async def get_tasks_with_context_variables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_variables')

    async def get_tasks_with_context_variables(self) -> list[Any]:
        return await self.get_items_with_related('context_variables')

    async def get_tasks_with_task_comments(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'task_comments')

    async def get_tasks_with_task_comments(self) -> list[Any]:
        return await self.get_items_with_related('task_comments')

    async def get_tasks_with_user_active_context(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_active_context')

    async def get_tasks_with_user_active_context(self) -> list[Any]:
        return await self.get_items_with_related('user_active_context')

    async def get_tasks_with_broker_values(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'broker_values')

    async def get_tasks_with_broker_values(self) -> list[Any]:
        return await self.get_items_with_related('broker_values')

    async def get_tasks_with_user_files(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_files')

    async def get_tasks_with_user_files(self) -> list[Any]:
        return await self.get_items_with_related('user_files')

    async def get_tasks_with_cx_conversation(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_conversation')

    async def get_tasks_with_cx_conversation(self) -> list[Any]:
        return await self.get_items_with_related('cx_conversation')

    async def get_tasks_with_sandbox_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'sandbox_instances')

    async def get_tasks_with_sandbox_instances(self) -> list[Any]:
        return await self.get_items_with_related('sandbox_instances')

    async def get_tasks_with_context_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'context_items')

    async def get_tasks_with_context_items(self) -> list[Any]:
        return await self.get_items_with_related('context_items')

    async def get_tasks_with_app_instances(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'app_instances')

    async def get_tasks_with_app_instances(self) -> list[Any]:
        return await self.get_items_with_related('app_instances')

    async def get_tasks_with_notes(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'notes')

    async def get_tasks_with_notes(self) -> list[Any]:
        return await self.get_items_with_related('notes')

    async def get_tasks_with_user_tables(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'user_tables')

    async def get_tasks_with_user_tables(self) -> list[Any]:
        return await self.get_items_with_related('user_tables')

    async def get_tasks_with_transcripts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'transcripts')

    async def get_tasks_with_transcripts(self) -> list[Any]:
        return await self.get_items_with_related('transcripts')

    async def get_tasks_with_workflow(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workflow')

    async def get_tasks_with_workflow(self) -> list[Any]:
        return await self.get_items_with_related('workflow')

    async def get_tasks_with_prompts(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'prompts')

    async def get_tasks_with_prompts(self) -> list[Any]:
        return await self.get_items_with_related('prompts')

    async def load_tasks_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.load_items(project_id=project_id)

    async def filter_tasks_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.filter_items(project_id=project_id)

    async def load_tasks_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_tasks_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_tasks_by_parent_task_id(self, parent_task_id: Any) -> list[Any]:
        return await self.load_items(parent_task_id=parent_task_id)

    async def filter_tasks_by_parent_task_id(self, parent_task_id: Any) -> list[Any]:
        return await self.filter_items(parent_task_id=parent_task_id)

    async def load_tasks_by_priority(self, priority: Any) -> list[Any]:
        return await self.load_items(priority=priority)

    async def filter_tasks_by_priority(self, priority: Any) -> list[Any]:
        return await self.filter_items(priority=priority)

    async def load_tasks_by_assignee_id(self, assignee_id: Any) -> list[Any]:
        return await self.load_items(assignee_id=assignee_id)

    async def filter_tasks_by_assignee_id(self, assignee_id: Any) -> list[Any]:
        return await self.filter_items(assignee_id=assignee_id)

    async def load_tasks_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_tasks_ids(self) -> set[Any]:
        return self.active_item_ids



class TasksManager(TasksBase):
    _instance: TasksManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> TasksManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: Tasks) -> None:
        pass

tasks_manager_instance = TasksManager()