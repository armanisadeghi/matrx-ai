# # File: db/managers/ai_model.py
# from __future__ import annotations

# from dataclasses import dataclass
# from typing import Any

# from matrx_orm import BaseDTO, BaseManager, ModelView

# from matrx_ai.db.models import AiModel

# # ---------------------------------------------------------------------------
# # ModelView (new) — opt-in projection layer.
# # Stores results flat on the model instance; no duplication, no nesting.
# # To activate: set view_class = AiModelView on your manager subclass,
# # or pass view_class=AiModelView to super().__init__().
# # When active, the DTO path below is skipped automatically.
# # ---------------------------------------------------------------------------

# class AiModelView(ModelView[AiModel]):
#     """
#     Declarative view for AiModel.

#     Configure what gets fetched and shaped automatically on every load:

#       prefetch    — relation names to fetch concurrently (FK / IFK / M2M)
#       exclude     — model field names to omit from to_dict() output
#       inline_fk   — replace FK id columns with the full related object
#                     e.g. {"customer_id": "customer"}

#     Add async methods (no leading underscore) for computed fields:

#         async def display_name(self, model: AiModel) -> str:
#             return model.name.title()
#     """

#     prefetch: list[str] = []
#     exclude: list[str] = []
#     inline_fk: dict[str, str] = {}

#     # ------------------------------------------------------------------ #
#     # Computed fields — add async methods below.                          #
#     # Each method receives the model instance and returns a plain value.  #
#     # Errors in computed fields are logged and stored as None —           #
#     # they never abort the load.                                          #
#     # ------------------------------------------------------------------ #


# # ---------------------------------------------------------------------------
# # BaseDTO (default) — active by default, fully backward compatible.
# # Extend _process_core_data / _process_metadata with your business logic.
# # When you are ready to migrate to the View above, set view_class on your
# # manager subclass and this DTO will be bypassed automatically.
# # ---------------------------------------------------------------------------

# @dataclass
# class AiModelDTO(BaseDTO[AiModel]):
#     id: str

#     async def _initialize_dto(self, model: AiModel) -> None:
#         '''Override to populate DTO fields from the model.'''
#         self.id = str(model.id)
#         await self._process_core_data(model)
#         await self._process_metadata(model)
#         await self._initial_validation(model)
#         self.initialized = True

#     async def _process_core_data(self, model: AiModel) -> None:
#         '''Process core data from the model item.'''
#         pass

#     async def _process_metadata(self, model: AiModel) -> None:
#         '''Process metadata from the model item.'''
#         pass

#     async def _initial_validation(self, model: AiModel) -> None:
#         '''Validate fields from the model item.'''
#         pass

#     async def _final_validation(self) -> bool:
#         '''Final validation of the model item.'''
#         return True

#     async def get_validated_dict(self) -> dict[str, Any]:
#         '''Get the validated dictionary.'''
#         await self._final_validation()
#         return self.to_dict()


# # ---------------------------------------------------------------------------
# # Manager — DTO is active by default for full backward compatibility.
# # To switch to the View (opt-in):
# #   1. Quick: set view_class = AiModelView  (replaces DTO automatically)
# #   2. Explicit: super().__init__(AiModel, view_class=AiModelView)
# # ---------------------------------------------------------------------------

# class AiModelBase(BaseManager[AiModel]):
#     view_class = None  # DTO is used by default; set to AiModelView to opt in

#     def __init__(
#         self,
#         dto_class: type[Any] | None = None,
#         view_class: type[Any] | None = None,
#     ) -> None:
#         if view_class is not None:
#             self.view_class = view_class
#         super().__init__(AiModel, dto_class=dto_class or AiModelDTO)

#     def _initialize_manager(self) -> None:
#         super()._initialize_manager()

#     async def _initialize_runtime_data(self, item: AiModel) -> None:
#         pass

#     async def create_ai_model(self, **data: Any) -> AiModel:
#         return await self.create_item(**data)

#     async def delete_ai_model(self, id: Any) -> bool:
#         return await self.delete_item(id)

#     async def get_ai_model_with_all_related(self, id: Any) -> tuple[AiModel, Any]:
#         return await self.get_item_with_all_related(id)

#     async def load_ai_model_by_id(self, id: Any) -> AiModel:
#         return await self.load_by_id(id)

#     async def load_ai_model(self, use_cache: bool = True, **kwargs: Any) -> AiModel:
#         return await self.load_item(use_cache, **kwargs)

#     async def update_ai_model(self, id: Any, **updates: Any) -> AiModel:
#         return await self.update_item(id, **updates)

#     async def load_ai_models(self, **kwargs: Any) -> list[AiModel]:
#         return await self.load_items(**kwargs)

#     async def filter_ai_models(self, **kwargs: Any) -> list[AiModel]:
#         return await self.filter_items(**kwargs)

#     async def get_or_create_ai_model(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> AiModel | None:
#         return await self.get_or_create(defaults, **kwargs)

#     async def get_ai_model_with_ai_provider(self, id: Any) -> tuple[Any, Any]:
#         return await self.get_item_with_related(id, 'ai_provider')

#     async def get_ai_models_with_ai_provider(self) -> list[Any]:
#         return await self.get_items_with_related('ai_provider')

#     async def get_ai_model_with_ai_model_endpoint(self, id: Any) -> tuple[Any, Any]:
#         return await self.get_item_with_related(id, 'ai_model_endpoint')

#     async def get_ai_models_with_ai_model_endpoint(self) -> list[Any]:
#         return await self.get_items_with_related('ai_model_endpoint')

#     async def get_ai_model_with_ai_settings(self, id: Any) -> tuple[Any, Any]:
#         return await self.get_item_with_related(id, 'ai_settings')

#     async def get_ai_models_with_ai_settings(self) -> list[Any]:
#         return await self.get_items_with_related('ai_settings')

#     async def get_ai_model_with_recipe_model(self, id: Any) -> tuple[Any, Any]:
#         return await self.get_item_with_related(id, 'recipe_model')

#     async def get_ai_models_with_recipe_model(self) -> list[Any]:
#         return await self.get_items_with_related('recipe_model')

#     async def load_ai_models_by_name(self, name: Any) -> list[Any]:
#         return await self.load_items(name=name)

#     async def filter_ai_models_by_name(self, name: Any) -> list[Any]:
#         return await self.filter_items(name=name)

#     async def load_ai_models_by_common_name(self, common_name: Any) -> list[Any]:
#         return await self.load_items(common_name=common_name)

#     async def filter_ai_models_by_common_name(self, common_name: Any) -> list[Any]:
#         return await self.filter_items(common_name=common_name)

#     async def load_ai_models_by_provider(self, provider: Any) -> list[Any]:
#         return await self.load_items(provider=provider)

#     async def filter_ai_models_by_provider(self, provider: Any) -> list[Any]:
#         return await self.filter_items(provider=provider)

#     async def load_ai_models_by_model_class(self, model_class: Any) -> list[Any]:
#         return await self.load_items(model_class=model_class)

#     async def filter_ai_models_by_model_class(self, model_class: Any) -> list[Any]:
#         return await self.filter_items(model_class=model_class)

#     async def load_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]:
#         return await self.load_items(model_provider=model_provider)

#     async def filter_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]:
#         return await self.filter_items(model_provider=model_provider)

#     async def load_ai_models_by_ids(self, ids: list[Any]) -> list[Any]:
#         return await self.load_items_by_ids(ids)

#     def add_computed_field(self, field: str) -> None:
#         super().add_computed_field(field)

#     def add_relation_field(self, field: str) -> None:
#         super().add_relation_field(field)

#     @property
#     def active_ai_model_ids(self) -> set[Any]:
#         return self.active_item_ids



# class AiModelManager(AiModelBase):
#     _instance: AiModelManager | None = None

#     def __new__(cls, *args: Any, **kwargs: Any) -> AiModelManager:
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance

#     def __init__(self) -> None:
#         super().__init__()

#     async def _initialize_runtime_data(self, item: AiModel) -> None:
#         pass

# _ai_model_manager_instance: AiModelManager | None = None


# def get_ai_model_manager() -> AiModelManager:
#     global _ai_model_manager_instance
#     if _ai_model_manager_instance is None:
#         _ai_model_manager_instance = AiModelManager()
#     return _ai_model_manager_instance