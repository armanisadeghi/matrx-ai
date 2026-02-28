from typing import Any

from matrx_orm import BaseManager

from db.custom.ai_models.ai_model_dto import AiModelDTO
from db.models import AiModel


class AiModelBase(BaseManager[AiModel]):
    view_class = None  # DTO is used by default; set to AiModelView to opt in

    def __init__(
        self,
        dto_class: type[Any] | None = None,
        view_class: type[Any] | None = None,
        fetch_on_init_limit: int = 200,
        fetch_on_init_with_warnings_off: str = "YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100",
    ):
        if view_class is not None:
            self.view_class = view_class
        super().__init__(
            AiModel,
            dto_class=dto_class or AiModelDTO,
            fetch_on_init_limit=fetch_on_init_limit,
            FETCH_ON_INIT_WITH_WARNINGS_OFF=fetch_on_init_with_warnings_off,
        )

    def _initialize_manager(self):
        super()._initialize_manager()

    async def _initialize_runtime_data(self, item: AiModel) -> None:
        pass

    async def create_ai_model(self, **data) -> AiModel:
        return await self.create_item(**data)

    async def delete_ai_model(self, id) -> None:
        return await self.delete_item(id)

    async def get_ai_model_with_all_related(self, id) -> AiModel:
        return await self.get_item_with_all_related(id)

    async def load_ai_model_by_id(self, id) -> AiModel | None:
        return await self.load_by_id(id)

    async def load_ai_model(self, use_cache=True, **kwargs) -> AiModel | None:
        return await self.load_item(use_cache, **kwargs)

    async def update_ai_model(self, id, **updates) -> AiModel:
        return await self.update_item(id, **updates)

    async def load_ai_models(self, **kwargs) -> list[AiModel]:
        return await self.load_items(**kwargs)

    async def filter_ai_models(self, **kwargs) -> list[AiModel]:
        return await self.filter_items(**kwargs)

    async def get_or_create(self, defaults=None, **kwargs) -> AiModel:
        return await self.get_or_create(defaults, **kwargs)

    async def get_ai_model_with_ai_provider(self, id):
        return await self.get_item_with_related(id, "model_provider")

    async def get_ai_models_with_ai_provider(self):
        return await self.get_items_with_related("model_provider")

    async def get_ai_model_with_ai_model_endpoint(self, id):
        return await self.get_item_with_related(id, "ai_model_endpoint")

    async def get_ai_models_with_ai_model_endpoint(self):
        return await self.get_items_with_related("ai_model_endpoint")

    async def get_ai_model_with_ai_settings(self, id):
        return await self.get_item_with_related(id, "ai_settings")

    async def get_ai_models_with_ai_settings(self):
        return await self.get_items_with_related("ai_settings")

    async def get_ai_model_with_recipe_model(self, id):
        return await self.get_item_with_related(id, "recipe_model")

    async def get_ai_models_with_recipe_model(self):
        return await self.get_items_with_related("recipe_model")

    async def load_ai_models_by_name(self, name):
        return await self.load_items(name=name)

    async def filter_ai_models_by_name(self, name):
        return await self.filter_items(name=name)

    async def load_ai_models_by_common_name(self, common_name):
        return await self.load_items(common_name=common_name)

    async def filter_ai_models_by_common_name(self, common_name):
        return await self.filter_items(common_name=common_name)

    async def load_ai_models_by_provider(self, provider):
        return await self.load_items(provider=provider)

    async def filter_ai_models_by_provider(self, provider):
        return await self.filter_items(provider=provider)

    async def load_ai_models_by_model_class(self, model_class):
        return await self.load_items(model_class=model_class)

    async def filter_ai_models_by_model_class(self, model_class):
        return await self.filter_items(model_class=model_class)

    async def load_ai_models_by_model_provider(self, model_provider):
        return await self.load_items(model_provider=model_provider)

    async def filter_ai_models_by_model_provider(self, model_provider):
        return await self.filter_items(model_provider=model_provider)

    async def load_ai_models_by_ids(self, ids):
        return await self.load_items_by_ids(ids)

    def add_computed_field(self, field):
        self.add_computed_field(field)

    def add_relation_field(self, field):
        self.add_relation_field(field)

    @property
    def active_ai_model_ids(self):
        return self.active_item_ids


if __name__ == "__main__":
    from matrx_utils import clear_terminal, vcprint
    clear_terminal()
    async def main():
        ai_model_base = AiModelBase()
        data = await ai_model_base.get_ai_model_with_ai_provider("548126f2-714a-4562-9001-0c31cbeea375")
        vcprint(data, title="AI Model", color="blue")

    import asyncio
    asyncio.run(main())