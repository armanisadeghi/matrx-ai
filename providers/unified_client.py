"""
Unified AI API System for OpenAI, Anthropic, and Google Gemini
Preserves ALL content types and metadata from all providers
"""

from typing import Any, Literal

from matrx_utils import vcprint

from config import UnifiedResponse
from db.custom.ai_model_manager import get_ai_model_manager
from orchestrator.requests import AIMatrixRequest

# ============================================================================
# UNIFIED CLIENT
# ============================================================================

# Maps api_class to endpoint name for routing
API_CLASS_TO_ENDPOINT = {
    "openai_standard": "openai_chat",
    "openai_reasoning": "openai_chat",
    "google_standard": "google_chat",
    "google_thinking": "google_chat",
    "google_thinking_3": "google_chat",
    "google_image_generation": "google_chat",
    "anthropic_standard": "anthropic_chat",
    "anthropic_adaptive": "anthropic_chat",
    "together_text_standard": "together_chat",
    "together_image": "together_image",
    "together_video": "together_video",
    "groq_standard": "groq_chat",
    "cerebras_standard": "cerebras_chat",
    "cerebras_reasoning": "cerebras_chat",
    "xai_standard": "xai_chat",
}


class UnifiedAIClient:
    """Unified client for all AI providers"""

    model_manager = get_ai_model_manager()

    def __init__(self):
        from providers import (
            AnthropicChat,
            CerebrasChat,
            GoogleChat,
            GroqChat,
            OpenAIChat,
            TogetherChat,
            XAIChat,
        )

        self.google_chat = GoogleChat()
        self.openai_chat = OpenAIChat()
        self.anthropic_chat = AnthropicChat()
        self.cerebras_chat = CerebrasChat()
        self.together_chat = TogetherChat()
        self.groq_chat = GroqChat()
        self.xai_chat = XAIChat()

    async def execute(
        self,
        request: AIMatrixRequest,
    ) -> UnifiedResponse:
        from processing.audio.audio_preprocessing import (
            preprocess_audio_in_messages,
            should_preprocess_audio,
        )
        from processing.audio.audio_support import api_class_supports_audio

        config = request.config
        model_id_or_name = config.model
        debug = request.debug

        # Get model details first (need to know API class for audio support check)
        model_data = await self.model_manager.load_model(model_id_or_name)

        if not model_data:
            raise ValueError(f"Model not found: {model_id_or_name}")

        model_name = model_data.name
        config.model = model_name

        api_class = model_data.api_class
        endpoint = API_CLASS_TO_ENDPOINT.get(api_class)

        # Check if audio needs transcription (either explicitly requested or API doesn't support audio)
        if should_preprocess_audio(config.messages, api_class):
            if debug:
                if api_class_supports_audio(api_class):
                    vcprint(
                        "Audio auto-transcription explicitly enabled - preprocessing messages",
                        "Unified Client",
                        color="cyan",
                    )
                else:
                    vcprint(
                        f"API '{api_class}' doesn't support audio - auto-transcribing as fallback",
                        "Unified Client",
                        color="yellow",
                    )

            config.messages, transcription_usage_list = preprocess_audio_in_messages(
                config.messages, api_class, debug=debug
            )

            # Add transcription usage to request history
            for usage in transcription_usage_list:
                request.add_usage(usage)
                if debug:
                    vcprint(
                        f"Tracked Groq transcription: {usage.metadata.get('duration_seconds', 0):.1f}s "
                        f"({usage.metadata.get('billed_duration', 0):.1f}s billed)",
                        "Usage Tracking",
                        color="blue",
                    )

        if not endpoint:
            raise ValueError(f"No endpoint mapping for api_class: {api_class}")

        if endpoint == "openai_chat":
            return await self.openai_chat.execute(config, api_class, debug)
        elif endpoint == "anthropic_chat":
            return await self.anthropic_chat.execute(config, api_class, debug)
        elif endpoint == "google_chat":
            return await self.google_chat.execute(config, api_class, debug)
        elif endpoint == "cerebras_chat":
            return await self.cerebras_chat.execute(config, api_class, debug)
        elif endpoint == "together_chat":
            return await self.together_chat.execute(config, api_class, debug)
        elif endpoint == "groq_chat":
            return await self.groq_chat.execute(config, api_class, debug)
        elif endpoint == "xai_chat":
            return await self.xai_chat.execute(config, api_class, debug)
        else:
            raise ValueError(f"No execution method for api_class: {api_class}")

    async def translate_request(
        self,
        request: AIMatrixRequest,
    ) -> dict[str, Any]:
        """Translate unified request to provider-specific format"""
        from providers import (
            AnthropicTranslator,
            CerebrasTranslator,
            GoogleTranslator,
            GroqTranslator,
            OpenAITranslator,
            TogetherTranslator,
            XAITranslator,
        )

        config = request.config
        model_id_or_name = config.model

        # Get model details
        model_data = await self.model_manager.load_model(model_id_or_name)

        if not model_data:
            raise ValueError(f"Model not found: {model_id_or_name}")

        model_name = model_data.name
        config.model = model_name

        api_class = model_data.api_class
        endpoint = API_CLASS_TO_ENDPOINT.get(api_class)

        if not endpoint:
            raise ValueError(f"No endpoint mapping for api_class: {api_class}")

        if api_class == "openai_standard":
            return OpenAITranslator().to_openai(config, api_class)
        elif api_class == "openai_reasoning":
            return OpenAITranslator().to_openai(config, api_class)
        elif api_class in ("anthropic_standard", "anthropic", "anthropic_adaptive"):
            return AnthropicTranslator().to_anthropic(config, api_class)
        elif api_class == "google_standard":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "google_thinking":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "google_thinking_3":
            return GoogleTranslator().to_google(config, api_class)
        elif api_class == "cerebras_standard":
            return CerebrasTranslator().to_cerebras(config, api_class)
        elif api_class == "cerebras_reasoning":
            return CerebrasTranslator().to_cerebras(config, api_class)
        elif api_class == "together_text_standard":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "together_image":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "together_video":
            return TogetherTranslator().to_together(config, api_class)
        elif api_class == "groq_standard":
            return GroqTranslator().to_groq(config, api_class)
        elif api_class == "xai_standard":
            return XAITranslator().to_xai(config, api_class)
        else:
            raise ValueError(f"Unknown provider: {endpoint}")

    def translate_response(
        self,
        provider: Literal[
            "openai", "anthropic", "gemini", "together", "groq", "xai", "cerebras"
        ],
        response: dict[str, Any],
    ) -> UnifiedResponse:
        """Translate provider-specific response to unified format"""
        from providers import (
            AnthropicTranslator,
            CerebrasTranslator,
            GoogleTranslator,
            GroqTranslator,
            OpenAITranslator,
            TogetherTranslator,
            XAITranslator,
        )

        if provider.startswith("openai"):
            return OpenAITranslator().from_openai(response)
        elif provider.startswith("anthropic"):
            return AnthropicTranslator().from_anthropic(response)
        elif provider.startswith("gemini"):
            return GoogleTranslator().from_google(response)
        elif provider.startswith("together"):
            return TogetherTranslator().from_together(response)
        elif provider.startswith("groq"):
            return GroqTranslator().from_groq(response)
        elif provider.startswith("xai"):
            return XAITranslator().from_xai(response)
        elif provider.startswith("cerebras"):
            return CerebrasTranslator().from_cerebras(response)
        else:
            raise ValueError(f"Unknown provider: {provider}")
