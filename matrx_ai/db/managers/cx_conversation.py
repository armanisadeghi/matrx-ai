# File: db/managers/cx_conversation.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from matrx_orm import BaseManager, BaseDTO, ModelView, build_output_schema
from matrx_utils import vcprint

from matrx_ai.db.models import CxConversation


# ---------------------------------------------------------------------------
# ModelView (new) — opt-in projection layer.
# Stores results flat on the model instance; no duplication, no nesting.
# To activate: set view_class = CxConversationView on your manager subclass,
# or pass view_class=CxConversationView to super().__init__().
# When active, the DTO path below is skipped automatically.
# ---------------------------------------------------------------------------

class CxConversationView(ModelView[CxConversation]):
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
#   - JSON Schema generation: CxConversationSchema.model_json_schema()
#   - Typed API responses: CxConversationSchema.model_validate(item.to_dict())
#
# Usage example:
#   @app.get("/{id}", response_model=CxConversationSchema)
#   async def get_cx_conversation(id: str):
#       item = await cx_conversation_manager_instance.load_by_id(id)
#       return item.to_dict()
# ---------------------------------------------------------------------------

try:
    CxConversationSchema = build_output_schema(CxConversation)
except ImportError:
    CxConversationSchema = None  # type: ignore[assignment]  # pydantic not installed


# ---------------------------------------------------------------------------
# BaseDTO (default) — active by default, fully backward compatible.
# Extend _process_core_data / _process_metadata with your business logic.
# When you are ready to migrate to the View above, set view_class on your
# manager subclass and this DTO will be bypassed automatically.
# ---------------------------------------------------------------------------

@dataclass
class CxConversationDTO(BaseDTO[CxConversation]):
    id: str

    async def _initialize_dto(self, model: CxConversation) -> None:
        '''Override to populate DTO fields from the model.'''
        self.id = str(model.id)
        await self._process_core_data(model)
        await self._process_metadata(model)
        await self._initial_validation(model)
        self.initialized = True

    async def _process_core_data(self, model: CxConversation) -> None:
        '''Process core data from the model item.'''
        pass

    async def _process_metadata(self, model: CxConversation) -> None:
        '''Process metadata from the model item.'''
        pass

    async def _initial_validation(self, model: CxConversation) -> None:
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
#   1. Quick: set view_class = CxConversationView  (replaces DTO automatically)
#   2. Explicit: super().__init__(CxConversation, view_class=CxConversationView)
# ---------------------------------------------------------------------------

class CxConversationBase(BaseManager[CxConversation]):
    view_class = None  # DTO is used by default; set to CxConversationView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(CxConversation, dto_class=dto_class or CxConversationDTO)

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: CxConversation) -> None:
        pass

    async def create_cx_conversation(self, **data: Any) -> CxConversation:
        return await self.create_item(**data)

    async def delete_cx_conversation(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_cx_conversation_with_all_related(self, id: Any) -> tuple[CxConversation, Any]:
        return await self.get_item_with_all_related(id)

    async def load_cx_conversation_by_id(self, id: Any) -> CxConversation:
        return await self.load_by_id(id)

    async def load_cx_conversation(self, use_cache: bool = True, **kwargs: Any) -> CxConversation:
        return await self.load_item(use_cache, **kwargs)

    async def update_cx_conversation(self, id: Any, **updates: Any) -> CxConversation:
        return await self.update_item(id, **updates)

    async def load_cx_conversations(self, **kwargs: Any) -> list[CxConversation]:
        return await self.load_items(**kwargs)

    async def filter_cx_conversations(self, **kwargs: Any) -> list[CxConversation]:
        return await self.filter_items(**kwargs)

    async def get_or_create_cx_conversation(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxConversation | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_cx_conversation_with_self_reference(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'self_reference')

    async def get_cx_conversations_with_self_reference(self) -> list[Any]:
        return await self.get_items_with_related('self_reference')

    async def get_cx_conversation_with_ai_model(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'ai_model')

    async def get_cx_conversations_with_ai_model(self) -> list[Any]:
        return await self.get_items_with_related('ai_model')

    async def get_cx_conversation_with_organizations(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'organizations')

    async def get_cx_conversations_with_organizations(self) -> list[Any]:
        return await self.get_items_with_related('organizations')

    async def get_cx_conversation_with_projects(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'projects')

    async def get_cx_conversations_with_projects(self) -> list[Any]:
        return await self.get_items_with_related('projects')

    async def get_cx_conversation_with_tasks(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'tasks')

    async def get_cx_conversations_with_tasks(self) -> list[Any]:
        return await self.get_items_with_related('tasks')

    async def get_cx_conversation_with_workspaces(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'workspaces')

    async def get_cx_conversations_with_workspaces(self) -> list[Any]:
        return await self.get_items_with_related('workspaces')

    async def get_cx_conversation_with_canvas_items(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'canvas_items')

    async def get_cx_conversations_with_canvas_items(self) -> list[Any]:
        return await self.get_items_with_related('canvas_items')

    async def get_cx_conversation_with_cx_media(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_media')

    async def get_cx_conversations_with_cx_media(self) -> list[Any]:
        return await self.get_items_with_related('cx_media')

    async def get_cx_conversation_with_cx_message(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_message')

    async def get_cx_conversations_with_cx_message(self) -> list[Any]:
        return await self.get_items_with_related('cx_message')

    async def get_cx_conversation_with_cx_request(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_request')

    async def get_cx_conversations_with_cx_request(self) -> list[Any]:
        return await self.get_items_with_related('cx_request')

    async def get_cx_conversation_with_cx_tool_call(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_tool_call')

    async def get_cx_conversations_with_cx_tool_call(self) -> list[Any]:
        return await self.get_items_with_related('cx_tool_call')

    async def get_cx_conversation_with_cx_user_request(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, 'cx_user_request')

    async def get_cx_conversations_with_cx_user_request(self) -> list[Any]:
        return await self.get_items_with_related('cx_user_request')

    async def load_cx_conversations_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.load_items(user_id=user_id)

    async def filter_cx_conversations_by_user_id(self, user_id: Any) -> list[Any]:
        return await self.filter_items(user_id=user_id)

    async def load_cx_conversations_by_forked_from_id(self, forked_from_id: Any) -> list[Any]:
        return await self.load_items(forked_from_id=forked_from_id)

    async def filter_cx_conversations_by_forked_from_id(self, forked_from_id: Any) -> list[Any]:
        return await self.filter_items(forked_from_id=forked_from_id)

    async def load_cx_conversations_by_last_model_id(self, last_model_id: Any) -> list[Any]:
        return await self.load_items(last_model_id=last_model_id)

    async def filter_cx_conversations_by_last_model_id(self, last_model_id: Any) -> list[Any]:
        return await self.filter_items(last_model_id=last_model_id)

    async def load_cx_conversations_by_parent_conversation_id(self, parent_conversation_id: Any) -> list[Any]:
        return await self.load_items(parent_conversation_id=parent_conversation_id)

    async def filter_cx_conversations_by_parent_conversation_id(self, parent_conversation_id: Any) -> list[Any]:
        return await self.filter_items(parent_conversation_id=parent_conversation_id)

    async def load_cx_conversations_by_keywords(self, keywords: Any) -> list[Any]:
        return await self.load_items(keywords=keywords)

    async def filter_cx_conversations_by_keywords(self, keywords: Any) -> list[Any]:
        return await self.filter_items(keywords=keywords)

    async def load_cx_conversations_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.load_items(organization_id=organization_id)

    async def filter_cx_conversations_by_organization_id(self, organization_id: Any) -> list[Any]:
        return await self.filter_items(organization_id=organization_id)

    async def load_cx_conversations_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.load_items(workspace_id=workspace_id)

    async def filter_cx_conversations_by_workspace_id(self, workspace_id: Any) -> list[Any]:
        return await self.filter_items(workspace_id=workspace_id)

    async def load_cx_conversations_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.load_items(project_id=project_id)

    async def filter_cx_conversations_by_project_id(self, project_id: Any) -> list[Any]:
        return await self.filter_items(project_id=project_id)

    async def load_cx_conversations_by_task_id(self, task_id: Any) -> list[Any]:
        return await self.load_items(task_id=task_id)

    async def filter_cx_conversations_by_task_id(self, task_id: Any) -> list[Any]:
        return await self.filter_items(task_id=task_id)

    async def load_cx_conversations_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_cx_conversation_ids(self) -> set[Any]:
        return self.active_item_ids



class CxConversationManager(CxConversationBase):
    _instance: CxConversationManager | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> CxConversationManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: CxConversation) -> None:
        pass

cx_conversation_manager_instance = CxConversationManager()