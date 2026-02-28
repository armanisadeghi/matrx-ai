import asyncio

# from initialize_systems import initialize
import json
import os
from datetime import datetime
from pathlib import Path

import dotenv
import rich
from matrx_utils import cleanup_async_resources, clear_terminal, vcprint

from orchestrator.executor import execute_until_complete
from providers.unified_client import (
    AIMatrixRequest,
    UnifiedAIClient,
)
from shared.json_utils import to_matrx_json  # TODO: move to matrx_utils or inline json.dumps
from tests.ai.test_context import create_test_execution_context

dotenv.load_dotenv()

LOCAL_USER_ID = os.getenv("LOCAL_USER_ID")

# initialize()
_ctx_token = create_test_execution_context(debug=False)


async def register_all_tools():
    from tools.registry import ToolRegistryV2
    tool_registry = ToolRegistryV2.get_instance()
    await tool_registry.load_from_database()
    vcprint(tool_registry.count, title="[EXECUTION TEST] register_tools Tools Loaded", color="blue", inline=True)



async def test_autonomous_execution(config: dict, conversation_id: str, debug: bool = False):
    """Test autonomous execution that handles all tool calls automatically"""
    
    if config.get("tools") and isinstance(config.get("tools"), list) and len(config.get("tools")) > 0:
        await register_all_tools()
    
    settings_to_use = {
        "conversation_id": conversation_id,
        "debug": debug,
        "config": config,
    }

    client = UnifiedAIClient()
    request = AIMatrixRequest.from_dict(settings_to_use)
    rich.print(request)

    try:
        completed = await execute_until_complete(
            initial_request=request,
            client=client,
            max_iterations=10,
            max_retries_per_iteration=0,
        )

        return completed

    except RuntimeError as e:
        vcprint(f"\n✗ Autonomous execution failed: {str(e)}", color="red")
        raise


def clean_up_response(response):
    last_response = response.request.config.messages.get_last_by_role("assistant")
    last_output = response.request.config.get_last_output()
    clean_response = {
        "output": last_output,
        "assistant_response": last_response,
        "config": response.request.config,
        "usage": response.total_usage,
        "metadata": response.metadata,
    }
    rich.print(clean_response)
    return clean_response


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


if __name__ == "__main__":
    clear_terminal()

    # test_user_id = get_test_user_id()
    # test_conversation_id = str(uuid.uuid4())

    openai = "gpt-5-mini"
    google = "gemini-3-flash-preview"
    model_3 = "548126f2-714a-4562-9001-0c31cbeea375"
    model_4 = "gemini-3-pro-image-preview"
    model_5 = "gpt-5"
    claude = "claude-sonnet-4-5-20250929"
    claude_low = "5b467c4b-80f3-420f-a516-05218907521b"
    claude_adaptive = "claude-sonnet-4-6"
    claude_high = "claude-sonnet-4-6"
    cerebras = "gpt-oss-120b"
    xai = "grok-4-1-fast-reasoning"
    together = "openai/gpt-oss-120b"
    groq = "llama-3.3-70b-versatile"
    openai_non_reasoning = "gpt-4.1-mini-2025-04-14"

    multiple_tools_settings = {
        "debug": True,
        "config": {
            "model": google,
            "stream": True,
            "reasoning_effort": "low",
            "reasoning_summary": "detailed",
            "tools": [
                "get_location",
                "get_weather",
                "get_restaurants",
                "get_activities",
                "get_events",
                "create_summary",
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": True,
            "internal_web_search": False,
            "internal_url_context": False,
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant. Think through your response step by step and use the many tools you have available to you. You have tools to get you the user's location, the weather, restaurants, activities, and events in the area.",
                },
                {
                    "role": "user",
                    "content": "Hi",
                },
                {
                    "role": "assistant",
                    "content": "Hello! How may I assist you today?",
                },
                {
                    "role": "user",
                    "content": "Hello! Can you give me some recommendations for today? restaurants and events in the area?",
                },
            ],
        },
    }

    image_generation_settings = {
        "ai_model_id": model_4,
        "debug": True,
        "config": {
            # "max_output_tokens": 4444,
            "stream": True,
            "reasoning_effort": "high",
            "reasoning_summary": "always",
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "Can you generate an image of a cat?",
                },
            ],
        },
    }

    complex_settings = {
        "ai_model_id": cerebras,
        "debug": False,
        "config": {
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant. Think through your response step by step before proceeding with a response. Always search the web to ensure you include recent and relevant facts in your response. You can check the user's location with a tool and provide whatever they need.",
                },
                {
                    "role": "user",
                    "content": "Hello! Can you help me? What is the latest us news?",
                },
            ],
            "temperature": 1,
            "max_output_tokens": 4096,
            "top_p": 1,
            "top_k": 50,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "stream": True,
            "response_format": "text",
            "store": True,
            "stop_sequences": [],
            "tools": [
                "get_location",
                "get_weather",
                "get_restaurants",
                "get_activities",
                "get_events",
                "create_summary",
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": False,
            "image_urls": False,
            "file_urls": False,
            "internal_web_search": True,
            "youtube_videos": False,
            "size": "1024x1024",
            "quality": "standard",
            "count": 1,
            "audio_voice": "alloy",
            "audio_format": "mp3",
            "reasoning_effort": "low",
            "verbosity": "medium",
            "reasoning_summary": "auto",
            "modalities": {},
            "preset_name": "default",
            "system_message_override": None,
            "reasoning": {},
        },
    }

    simple_chat_settings = {
        "debug": True,
        "config": {
            "model": "gpt-5-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": "Hello! How are you?",
                },
            ],
            "stream": True,
        },
    }

    single_tool_settings = {
        "debug": False,
        "config": {
            # "max_output_tokens": 4444,
            "model": google,
            "stream": True,
            "reasoning_effort": "low",
            "reasoning_summary": "detailed",
            "tools": [
                "news_get_headlines",
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": True,
            "internal_web_search": False,
            "internal_url_context": False,
            "messages": [
                {
                    "role": "system",
                    "content": f"You're a helpful assistant. Think through your response step by step and use the many tools you have available to you. You have tools to get the latest news headlines. Today's Date: {datetime.now().strftime('%Y-%m-%d')}",
                },
                {
                    "role": "user",
                    "content": "Hi",
                },
                {
                    "role": "assistant",
                    "content": "Hello! How may I assist you today?",
                },
                {
                    "role": "user",
                    "content": "Hello! Can you give me some of the latest news headlines? Just for the US is good and I want them up to  date for today.",
                },
            ],
        },
    }

    # Same as single_tool_settings but using structured system_instruction.
    # Date is auto-injected by SystemInstruction (no f-string hack needed).
    # No {"role": "system", ...} message in the messages array.
    single_tool_settings_v2 = {
        "debug": False,
        "config": {
            "model": google,
            "stream": True,
            "reasoning_effort": "low",
            "reasoning_summary": "detailed",
            "system_instruction": {
                "content": "You're a helpful assistant. Think through your response step by step and use the many tools you have available to you. You have tools to get the latest news headlines.",
                "include_date": True,
            },
            "tools": [
                "news_get_headlines",
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": True,
            "internal_web_search": False,
            "internal_url_context": False,
            "messages": [
                {
                    "role": "user",
                    "content": "Hi",
                },
                {
                    "role": "assistant",
                    "content": "Hello! How may I assist you today?",
                },
                {
                    "role": "user",
                    "content": "Hello! Can you give me some of the latest news headlines? Just for the US is good and I want them up to date for today.",
                },
            ],
        },
    }

    image_input_settings = {
        "debug": True,
        "config": {
            "model": openai_non_reasoning,
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "what is in this image? be specific and detailed.",
                        },
                        {
                            "type": "input_image",
                            "image_url": f"https://txzxabzwovsujtloxrus.supabase.co/storage/v1/object/public/user-public-assets/user-{LOCAL_USER_ID}/mcp-logo.png",
                        },
                    ],
                },
            ],
            "stream": True,
        },
    }

    document_input_settings = {
        "debug": True,
        "config": {
            "model": openai_non_reasoning,
            "messages": [
                {
                    "role": "system",
                    "content": "You're a document analyzer. Only responsd if you can clearly see the document and it's content.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "what is in this document? be specific and detailed.",
                        },
                        {
                            "type": "input_document",
                            "url": f"https://txzxabzwovsujtloxrus.supabase.co/storage/v1/object/public/user-public-assets/user-{LOCAL_USER_ID}/Ads%20Conv%20Analysis.pdf",
                        },
                    ],
                },
            ],
            "stream": True,
        },
    }

    youtube_url_settings = {
        "debug": True,
        "config": {
            "model": google,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "youtube_video",
                            "youtube_url": "https://www.youtube.com/watch?v=9hE5-98ZeCg",
                        },
                        {
                            "type": "text",
                            "text": "Please summarize this video in 3 sentences.",
                        },
                    ],
                },
            ],
            "stream": True,
        },
    }

    # Audio URL for testing
    audio_url = "https://txzxabzwovsujtloxrus.supabase.co/storage/v1/object/public/Audio/Audio%20Files/My%20Recordings/small_sample_audio.m4a"

    # Test 1: Use Groq transcription to convert audio to text, then send to Google
    audio_transcription_test_settings = {
        "debug": True,
        "config": {
            "model": openai_non_reasoning,
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant that analyzes audio content.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "audio",
                            "url": audio_url,
                            # "auto_transcribe": True,  # Transcribe with Groq first
                            # "transcription_model": "whisper-large-v3-turbo", # Optional
                            # "transcription_language": "en", # Optional
                        },
                        {
                            "type": "text",
                            "text": "Please summarize what was said in the audio in 2-3 sentences.",
                        },
                    ],
                },
            ],
            "stream": True,
        },
    }

    # Test 2: Send audio directly to Google (Google can handle audio natively)
    audio_direct_google_settings = {
        "debug": True,
        "config": {
            "model": google,
            "messages": [
                {
                    "role": "system",
                    "content": "You're a helpful assistant that analyzes audio content.",
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "audio",
                            "url": audio_url,
                            "auto_transcribe": False,  # Send directly to Google
                        },
                        {
                            "type": "text",
                            "text": "Please summarize what was said in the audio in 2-3 sentences.",
                        },
                    ],
                },
            ],
            "stream": True,
        },
    }

    # options: simple_chat_settings, single_tool_settings_v2, image_generation_settings, complex_settings,
    # document_input_settings, youtube_url_settings, audio_transcription_test_settings, audio_direct_google_settings
    settings_to_use = single_tool_settings_v2
    settings_to_use["config"]["model"] = google
    # settings_to_use["debug"] = True

    # Run autonomous execution that handles all tool calls automatically
    # final_result = asyncio.run(
    #     test_autonomous_execution(settings_to_use, emitter)
    # )

    from tests.ai.test_context import get_test_conversation_id

    conversation_id = get_test_conversation_id()
    final_result = asyncio.run(
        test_autonomous_execution(settings_to_use["config"], conversation_id, debug=False)
    )

    # Save to file for easy review
    output_file = Path(__file__).parent / "final_response.json"
    serializable_result = to_matrx_json(final_result)
    with open(output_file, "w") as f:
        json.dump(serializable_result, f, indent=4)

    vcprint(f"\nFinal result saved to: {output_file}", color="blue")

    clean_response = clean_up_response(final_result)
    output_file = Path(__file__).parent / "clean_response.json"
    serializable_result = to_matrx_json(clean_response)
    with open(output_file, "w") as f:
        json.dump(serializable_result, f, indent=4)
    vcprint(f"\nClean response saved to: {output_file}", color="blue")

    # Save in cx_ storage format (database-ready)
    storage_data = final_result.to_storage_dict()
    storage_serializable = to_matrx_json(storage_data)
    output_file = Path(__file__).parent / "cx_storage_response.json"
    with open(output_file, "w") as f:
        json.dump(storage_serializable, f, indent=4)
    vcprint(f"\nCX storage format saved to: {output_file}", color="blue")

    # Clean up async resources to prevent ResourceWarnings
    cleanup_async_resources()
