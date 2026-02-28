import uuid

from db.models import AiModel

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
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()

    async def load_all_models(self, update_data_in_code: bool = False):
        models = await self.load_items()
        if update_data_in_code:
            await self.update_data_in_code(models, "all_active_ai_models")
        return models

    async def load_model(self, id_or_name: str):
        return await self.load_model_by_id(id_or_name)

    async def load_model_get_string_uuid(self, id_or_name: str):
        model: AiModel = await self.load_model_by_id(id_or_name)        
        return model.id if model else None

    async def load_model_by_id(self, model_id: str):
        """
        Load a model by ID or name.

        If model_id is a valid UUID, it will be treated as an ID.
        Otherwise, it will be treated as a name and looked up in the cache.

        Args:
            model_id: Either a UUID string or a model name

        Returns:
            The model object if found, None otherwise
        """
        # Check if it's a valid UUID
        try:
            uuid.UUID(model_id)
            # It's a valid UUID, use the standard ID lookup
            return await self.load_ai_model_by_id(model_id)
        except (ValueError, AttributeError):
            # Not a valid UUID, try to find by name in the cache
            # Since all models are already fetched and cached on init,
            # we can search through the cache efficiently
            models = await self.load_items(name=model_id)
            if models:
                return models[0]  # Return the first match
            return None

    async def load_models_by_name(self, model_name: str):
        return await self.load_ai_models_by_name(model_name)

    async def load_models_by_provider(self, provider: str):
        return await self.load_ai_models_by_provider(provider)


# To get the single instance of AiModelManager
# ai_model_manager_instance = AiModelManager()

# Jatin added this
ai_model_manager_instance = None


def get_ai_model_manager():
    global ai_model_manager_instance
    if ai_model_manager_instance is None:
        ai_model_manager_instance = AiModelManager()
    return ai_model_manager_instance
