import asyncio

from matrx_utils import clear_terminal, vcprint

from matrx_ai.db import _setup
from matrx_ai.db.custom.ai_models.ai_model_manager import AiModelManager

_setup()


async def local_test(test_type: str, **kwargs):
    manager = AiModelManager()

    if test_type == "id":
        data = await manager.load_model_by_id("548126f2-714a-4562-9001-0c31cbeea375")
        
    elif test_type == "name":
        data = await manager.load_model_by_name("gpt-4o")
    elif test_type == "provider":
        data = await manager.load_models_by_provider("XAI")
    elif test_type == "all_models":
        data = await manager.load_all_models()
    elif test_type == "list_providers":
        data = await manager.list_unique_model_providers()
    else:
        raise ValueError(f"Invalid test type: {test_type}")

    return data


# {
#     "id": "1aa00794-f43a-49e3-8ecf-169693f39f40",
#     "name": "claude-3-5-haiku-20241022",
#     "common_name": "Claude 3.5 Haiku",
#     "model_class": "claude-3-5-haiku",
#     "provider": "Anthropic",
#     "endpoints": [
#         "anthropic"
#     ],
#     "max_tokens": 8192,
#     "model_provider": "af5b5f1d-25dd-4c76-b84d-995e53fdf1f4",
#     "runtime": {},
#     "dto": {
#         "id": "1aa00794-f43a-49e3-8ecf-169693f39f40"
#     }
# }

if __name__ == "__main__":
    clear_terminal()
    
    test_type = "all_models"  # ["id", "name", "provider", "all_models", "list_providers"]

    data = asyncio.run(local_test(test_type))
    vcprint(data=data, title="AI Model", pretty=True, color="green")

    # dto = data.dto
    # vcprint(dto, title="DTO", pretty=True, color="blue")

