# Placeholder: AiModelBase — the real implementation lives in the aidream project.
# This provides the interface that AiModelManager extends.
from typing import Any


class AiModelBase:
    async def load_items(self, **kwargs: Any) -> list[dict[str, Any]]:
        return []

    async def load_ai_model_by_id(self, model_id: str) -> dict[str, Any] | None:
        return None

    async def update_data_in_code(self, models: list[Any], name: str) -> None:
        pass
