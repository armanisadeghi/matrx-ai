"""AI Model Resolution.

- AiModelBase: Base class for model operations
- AiModelManager: Singleton manager for AI model lookup
- get_ai_model_manager: Factory function
"""

from models.ai_model_manager import get_ai_model_manager

__all__ = [
    "get_ai_model_manager",
]
