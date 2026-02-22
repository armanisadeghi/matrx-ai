# Placeholder: AiModelManager — the real implementation lives in the aidream project.
# This provides the singleton pattern expected by ai.unified_client and ai.db.persistence.
import uuid
from typing import Any

from models.ai_model_base import AiModelBase


class AiModelManager(AiModelBase):
    _instance = None

    def __new__(cls, *args: Any, **kwargs: Any) -> "AiModelManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def load_all_models(self, update_data_in_code: bool = False) -> list[dict[str, Any]]:
        return await self.load_items()

    async def load_model(self, id_or_name: str) -> dict[str, Any] | None:
        return await self.load_model_by_id(id_or_name)

    async def load_model_by_id(self, model_id: str) -> dict[str, Any] | None:
        try:
            uuid.UUID(model_id)
            return await self.load_ai_model_by_id(model_id)
        except (ValueError, AttributeError):
            models = await self.load_items(name=model_id)
            return models[0] if models else None


_ai_model_manager_instance: AiModelManager | None = None


def get_ai_model_manager() -> AiModelManager:
    global _ai_model_manager_instance
    if _ai_model_manager_instance is None:
        _ai_model_manager_instance = AiModelManager()
    return _ai_model_manager_instance
