from __future__ import annotations

import uuid
from typing import Any

from matrx_ai.db.models import AiModel

from .ai_model_base import AiModelBase

info = True
debug = False
verbose = False

""" vcprint guidelines
verbose=verbose for things we do not want to see most of the time
verbose=debug for things we want to see during debugging
verbose=info for things that should almost ALWAYS print.
verbose=True for errors and things that should never be silenced.
Errors are always set to verbose = True, color = "red"
"""


class AiModelManager(AiModelBase):
    _instance: AiModelManager | None = None
    _api_cache: list[dict[str, Any]] | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> AiModelManager:
        if "_instance" not in cls.__dict__ or cls.__dict__["_instance"] is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        super().__init__()

    async def _initialize_runtime_data(self, item: AiModel) -> None:
        pass

    # ------------------------------------------------------------------
    # Client-mode: fetch all models from the API and cache in-process.
    # The cache is populated lazily on the first call and reused for
    # subsequent lookups so the API is only hit once per process.
    # ------------------------------------------------------------------

    async def _get_api_models(self) -> list[dict[str, Any]]:
        if self._api_cache is None:
            from matrx_ai.client_mode import get_api_client
            self.__class__._api_cache = await get_api_client().get_models()
        return self._api_cache or []

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    async def load_all_models(self) -> list[AiModel]:
        from matrx_ai.db import is_client_mode
        if is_client_mode():
            return await self._get_api_models()  # type: ignore[return-value]
        return await self.load_items()

    async def load_model(self, id_or_name: str) -> AiModel | None:
        return await self.load_model_by_id(id_or_name)

    async def load_model_get_string_uuid(self, id_or_name: str) -> str | None:
        from matrx_ai.db import is_client_mode
        if is_client_mode():
            rows = await self._get_api_models()
            for row in rows:
                if str(row.get("id", "")) == id_or_name or row.get("name") == id_or_name:
                    return str(row["id"])
            return None
        model: AiModel | None = await self.load_model_by_id(id_or_name)
        return model.id if model else None

    async def load_model_by_id(self, model_id: str) -> AiModel | None:
        """Load a model by UUID or name.

        If model_id is a valid UUID, it will be looked up by ID.
        Otherwise, it will be matched by name.
        """
        from matrx_ai.db import is_client_mode
        if is_client_mode():
            rows = await self._get_api_models()
            is_uuid = True
            try:
                uuid.UUID(model_id)
            except (ValueError, AttributeError):
                is_uuid = False
            for row in rows:
                if is_uuid and str(row.get("id", "")) == model_id:
                    return row  # type: ignore[return-value]
                if not is_uuid and row.get("name") == model_id:
                    return row  # type: ignore[return-value]
            return None

        try:
            uuid.UUID(model_id)
            return await self.load_ai_model_by_id(model_id)
        except (ValueError, AttributeError):
            models: list[AiModel] = await self.load_items(name=model_id)
            return models[0] if models else None

    async def load_models_by_name(self, model_name: str) -> list[AiModel]:
        from matrx_ai.db import is_client_mode
        if is_client_mode():
            rows = await self._get_api_models()
            return [r for r in rows if r.get("name") == model_name]  # type: ignore[return-value]
        return await self.load_items(name=model_name)

    async def load_models_by_provider(self, provider: str) -> list[AiModel]:
        from matrx_ai.db import is_client_mode
        if is_client_mode():
            rows = await self._get_api_models()
            return [r for r in rows if r.get("provider") == provider]  # type: ignore[return-value]
        return await self.load_items(provider=provider)


ai_model_manager_instance = AiModelManager()
