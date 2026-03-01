from typing import Any

from matrx_orm import BaseManager

from matrx_ai.db.custom.ai_models.ai_model_dto import AiModelDTO
from matrx_ai.db.models import AiModel

# ---------------------------------------------------------------------------
# Manager — DTO is active by default for full backward compatibility.
# To switch to the View (opt-in):
#   1. Quick: set view_class = AiModelView  (replaces DTO automatically)
#   2. Explicit: super().__init__(AiModel, view_class=AiModelView)
# ---------------------------------------------------------------------------


class AiModelBase(BaseManager[AiModel]):
    view_class = None  # DTO is used by default; set to AiModelView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
        fetch_on_init_limit: int = 200,
        fetch_on_init_with_warnings_off: str = "YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100",
    ) -> None:
        if view_class is not None:
            self.view_class = view_class
        super().__init__(
            AiModel,
            dto_class=dto_class or AiModelDTO,
            fetch_on_init_limit=fetch_on_init_limit,
            FETCH_ON_INIT_WITH_WARNINGS_OFF=fetch_on_init_with_warnings_off,
        )

    def _initialize_manager(self) -> None:
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: AiModel) -> None:
        pass

    async def create_ai_model(self, **data: Any) -> AiModel:
        return await self.create_item(**data)

    async def delete_ai_model(self, id: Any) -> bool:
        return await self.delete_item(id)

    async def get_ai_model_with_all_related(self, id: Any) -> tuple[AiModel, Any]:
        return await self.get_item_with_all_related(id)

    async def load_ai_model_by_id(self, id: Any) -> AiModel:
        return await self.load_by_id(id)

    async def load_ai_model(self, use_cache: bool = True, **kwargs: Any) -> AiModel:
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_model(self, id: Any, **updates: Any) -> AiModel:
        return await self.update_item(id, **updates)

    async def load_ai_models(self, **kwargs: Any) -> list[AiModel]:
        return await self.load_items(**kwargs)

    async def filter_ai_models(self, **kwargs: Any) -> list[AiModel]:
        return await self.filter_items(**kwargs)

    async def get_or_create_ai_model(
        self, defaults: dict[str, Any] | None = None, **kwargs: Any
    ) -> AiModel | None:
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_model_with_ai_provider(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, "ai_provider")

    async def get_ai_models_with_ai_provider(self) -> list[Any]:
        return await self.get_items_with_related("ai_provider")

    async def get_ai_model_with_ai_model_endpoint(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, "ai_model_endpoint")

    async def get_ai_models_with_ai_model_endpoint(self) -> list[Any]:
        return await self.get_items_with_related("ai_model_endpoint")

    async def get_ai_model_with_ai_settings(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, "ai_settings")

    async def get_ai_models_with_ai_settings(self) -> list[Any]:
        return await self.get_items_with_related("ai_settings")

    async def get_ai_model_with_recipe_model(self, id: Any) -> tuple[Any, Any]:
        return await self.get_item_with_related(id, "recipe_model")

    async def get_ai_models_with_recipe_model(self) -> list[Any]:
        return await self.get_items_with_related("recipe_model")

    async def load_ai_models_by_name(self, name: Any) -> list[Any]:
        return await self.load_items(name=name)

    async def filter_ai_models_by_name(self, name: Any) -> list[Any]:
        return await self.filter_items(name=name)

    async def load_ai_models_by_common_name(self, common_name: Any) -> list[Any]:
        return await self.load_items(common_name=common_name)

    async def filter_ai_models_by_common_name(self, common_name: Any) -> list[Any]:
        return await self.filter_items(common_name=common_name)

    async def load_ai_models_by_provider(self, provider: Any) -> list[Any]:
        return await self.load_items(provider=provider)

    async def filter_ai_models_by_provider(self, provider: Any) -> list[Any]:
        return await self.filter_items(provider=provider)

    async def load_ai_models_by_model_class(self, model_class: Any) -> list[Any]:
        return await self.load_items(model_class=model_class)

    async def filter_ai_models_by_model_class(self, model_class: Any) -> list[Any]:
        return await self.filter_items(model_class=model_class)

    async def load_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]:
        return await self.load_items(model_provider=model_provider)

    async def filter_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]:
        return await self.filter_items(model_provider=model_provider)

    async def load_ai_models_by_ids(self, ids: list[Any]) -> list[Any]:
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field: str) -> None:
        super().add_computed_field(field)

    def add_relation_field(self, field: str) -> None:
        super().add_relation_field(field)

    @property
    def active_ai_model_ids(self) -> set[Any]:
        return self.active_item_ids


if __name__ == "__main__":
    from matrx_utils import clear_terminal, vcprint

    clear_terminal()

    async def main():
        ai_model_base = AiModelBase()
        data = await ai_model_base.get_ai_model_with_ai_provider(
            "548126f2-714a-4562-9001-0c31cbeea375"
        )
        vcprint(data, title="AI Model", color="blue")

    import asyncio

    asyncio.run(main())
