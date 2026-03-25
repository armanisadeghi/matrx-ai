import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
import json
import os
from datetime import datetime

import matrx_ai
from matrx_ai.context.app_context import clear_app_context
from tests.ai.test_context import create_test_app_context

matrx_ai.initialize()

import rich
from matrx_utils import cleanup_async_resources, clear_terminal, to_matrx_json, vcprint

from matrx_ai.orchestrator import CompletedRequest

LOCAL_USER_ID = os.getenv("LOCAL_USER_ID")
test_user_id = os.getenv("TEST_USER_ID", "")


async def register_all_tools():
    from matrx_ai.tools.registry import ToolRegistryV2
    tool_registry = ToolRegistryV2.get_instance()
    await tool_registry.load_from_database()
    vcprint(tool_registry.count, title="[EXECUTION TEST] register_tools Tools Loaded", color="blue", inline=True)


# ---------------------------------------------------------------------------
# TEST_MODE switch
#   "direct" → calls execute_ai_request() in-process (no HTTP, no server needed)
#   "api"    → fires real HTTP requests at the running server (full stack)
# ---------------------------------------------------------------------------
TEST_MODE = "direct"


async def test_autonomous_execution(config: dict, debug: bool = False):
    """Test autonomous execution — same path as a live API call.

    Creates a fresh AppContext with the correct debug setting, builds a
    UnifiedConfig from the config dict, then delegates entirely to
    execute_ai_request() which reads user_id, conversation_id, and all other
    context from AppContext.

    No AIMatrixRequest, no UnifiedAIClient — the engine handles all of that.

    Returns (final_result, storage_data) — storage_data is serialized while
    AppContext is still alive because to_storage_dict() reads user_id from it.
    """
    from matrx_ai.config.unified_config import UnifiedConfig
    from matrx_ai.db.custom import ensure_conversation_exists, ensure_user_request_exists
    from matrx_ai.orchestrator.executor import execute_ai_request
    from matrx_ai.context.app_context import get_app_context

    ctx_token = create_test_app_context(debug=debug, new_conversation=True)
    try:
        ctx = get_app_context()
        unified_config = UnifiedConfig.from_dict(config)
        vcprint(
            {"conversation_id": ctx.conversation_id, "user_id": ctx.user_id, "debug": ctx.debug},
            "[EXECUTION TEST] Context",
            color="green"
        )

        await ensure_conversation_exists(
            conversation_id=ctx.conversation_id,
            user_id=ctx.user_id,
        )
        await ensure_user_request_exists(
            request_id=ctx.request_id,
            conversation_id=ctx.conversation_id,
            user_id=ctx.user_id,
        )

        result = await execute_ai_request(
            unified_config, max_iterations=10, max_retries_per_iteration=0
        )
        storage_data = result.to_storage_dict()
        return result, storage_data
    finally:
        clear_app_context(ctx_token)


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
# API TEST HELPERS — hit the real HTTP endpoints against a running server
# ============================================================================

_API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
_ADMIN_TOKEN = os.getenv("ADMIN_API_TOKEN", "")


def _auth_headers() -> dict:
    if not _ADMIN_TOKEN:
        raise RuntimeError(
            "ADMIN_API_TOKEN is not set in .env — required for API tests."
        )
    return {
        "Authorization": f"Bearer {_ADMIN_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/x-ndjson",
    }


async def _stream_api_request(method: str, path: str, body: dict) -> list[dict]:
    """POST/GET to the server and print each NDJSON line as it arrives.

    Returns the list of parsed event dicts so callers can inspect the result.
    """
    try:
        import httpx
    except ImportError:
        raise RuntimeError("httpx is required for API tests: uv pip install httpx")

    url = f"{_API_BASE}{path}"
    vcprint(f"\n[API TEST] {method} {url}", color="cyan")
    rich.print(body)

    events: list[dict] = []
    async with httpx.AsyncClient(timeout=120.0) as client:
        async with client.stream(
            method, url, json=body, headers=_auth_headers()
        ) as response:
            if response.status_code != 200:
                error_body = await response.aread()
                vcprint(
                    f"[API TEST] HTTP {response.status_code}: {error_body.decode()}",
                    color="red",
                )
                return events

            vcprint(
                f"[API TEST] Stream opened (HTTP {response.status_code})", color="green"
            )
            async for raw_line in response.aiter_lines():
                line = raw_line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                    events.append(event)
                    _print_event(event)
                except json.JSONDecodeError:
                    vcprint(f"[API TEST] Non-JSON line: {line!r}", color="yellow")

    vcprint(
        f"\n[API TEST] Stream complete — {len(events)} events received", color="blue"
    )
    return events


def _print_event(event: dict) -> None:
    """Pretty-print a single stream event."""
    etype = event.get("event", "unknown")
    data = event.get("data", {})

    color_map = {
        "chunk": "white",
        "status_update": "cyan",
        "data": "blue",
        "completion": "green",
        "error": "red",
        "tool_event": "yellow",
        "end": "magenta",
        "heartbeat": None,
    }
    color = color_map.get(etype, "white")
    if color is None:
        return  # skip heartbeats

    if etype == "chunk":
        print(data.get("text", ""), end="", flush=True)
    elif etype == "completion":
        print()  # newline after streaming chunks
        vcprint(f"\n[{etype.upper()}]", color=color)
        rich.print(data)
    elif etype == "error":
        print()
        vcprint(f"\n[{etype.upper()}] {data.get('message', '')}", color=color)
        rich.print(data)
    else:
        vcprint(f"[{etype}] {data.get('status', data.get('message', ''))}", color=color)


async def test_api_chat(config: dict, debug: bool = False) -> list[dict]:
    """Call POST /ai/chat — equivalent to sending a direct chat request."""
    body = {**config, "debug": debug}
    # The /ai/chat route expects ai_model_id at the top level and messages inside.
    # Our config dicts already use "model" — translate for the route.
    if "model" in body and "ai_model_id" not in body:
        body["ai_model_id"] = body.pop("model")
    return await _stream_api_request("POST", "/ai/chat", body)


async def test_api_agent(
    agent_id: str, user_input: str, debug: bool = False
) -> list[dict]:
    """Call POST /ai/agents/{agent_id} — starts an agent from a DB prompt ID."""
    body = {"user_input": user_input, "debug": debug}
    return await _stream_api_request("POST", f"/ai/agents/{agent_id}", body)


async def test_api_conversation(
    conversation_id: str,
    user_input: str,
    debug: bool = False,
) -> list[dict]:
    """Call POST /ai/conversations/{conversation_id} — continues an existing conversation."""
    body = {"user_input": user_input, "debug": debug}
    return await _stream_api_request(
        "POST", f"/ai/conversations/{conversation_id}", body
    )


# ============================================================================
# EXAMPLE USAGE
# ============================================================================


if __name__ == "__main__":
    clear_terminal()

    # -----------------------------------------------------------------------
    # API TEST CONFIG
    # Swap TEST_MODE at the top of this file:
    #   "direct" → in-process (no server needed, fastest)
    #   "api"    → real HTTP to running server (full middleware + auth stack)
    # -----------------------------------------------------------------------
    # For "api" mode, set the agent/conversation IDs you want to test:
    TEST_AGENT_ID = os.getenv("TEST_AGENT_ID", "")
    TEST_CONVERSATION_ID = os.getenv("TEST_CONVERSATION_ID", "")

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
    openai_reasoning = "gpt-5"
    google_tts_pro = "gemini-2.5-pro-preview-tts"
    google_tts_flash = "gemini-2.5-flash-preview-tts"
    openai_tts_mini = "gpt-4o-mini-tts"
    openai_tts_1 = "tts-1"
    openai_tts_1_hd = "tts-1-hd"
    groq_tts = "canopylabs/orpheus-v1-english"
    xai_tts = "xai-tts"
    cerebras_reasoning = "zai-glm-4.7"

    multiple_tools_settings = {
        "debug": True,
        "config": {
            "model": google,
            "stream": True,
            "reasoning_effort": "low",
            "reasoning_summary": "detailed",
            "tools": [
                "travel_get_location",
                "travel_get_weather",
                "travel_get_restaurants",
                "travel_get_activities",
                "travel_get_events",
                "travel_create_summary",
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
                "travel_get_location",
                "travel_get_weather",
                "travel_get_restaurants",
                "travel_get_activities",
                "travel_get_events",
                "travel_create_summary",
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
            "tts_voice": "alloy",
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
            "thinking_level": "low",
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
                            "image_url": f"https://txzxabzwovsujtloxrus.supabase.co/storage/v1/object/public/user-public-assets/user-{test_user_id}/mcp-logo.png",
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
                            "url": f"https://txzxabzwovsujtloxrus.supabase.co/storage/v1/object/public/user-public-assets/user-{test_user_id}/Ads%20Conv%20Analysis.pdf",
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


    podcast_direct_settings = {
        "debug": True,
        "config": {
            "model": "gemini-2.5-pro-preview-tts",
            "stream": True,
            "temperature": 1,
            "tts_voice": [
                {
                    "name": "Alex",
                    "voice": "Orus",
                },
                {
                    "name": "Sarah",
                    "voice": "Kore",
                },
            ],
            "messages": [
                {
                    "role": "user",
                    "content": """Please read aloud the following in a podcast interview style:

Alex: Okay, real talk — every single person listening to this right now started life as one cell. One. And somehow that one cell divided and divided and divided until you became a full human being with trillions of cells. How does that even work?

Sarah: And here's what makes it even wilder — that process never really stops. Right now, as you're listening to this, your body is dividing cells to replace the ones you're losing, healing damage, keeping you alive. Cell division is happening inside you this very second.

Alex: Pretty Purple Monkeys Are Tired, everyone. You've got this. Thanks for listening.

Sarah: See you in the next one.""",
                },
            ],
        },
    }

    # ElevenLabs dialogue mode — each turn carries its own voice_id inline.
    # tts_voice is a list of {text, voice_id} dicts; no global voice needed.
    # Voice IDs below match the sample_2 cast from direct_dialogue.py.
    elevenlabs_dialogue_settings = {
        "debug": True,
        "config": {
            "model": "eleven_v3",
            "stream": True,
            "audio_format": "mp3",
            "tts_voice": [
                {
                    "text": "[excited] Welcome to today's episode. Right now, as you're listening to this — your body is quietly making about 25 million new cells every single second. Every. Second. And every one of those new cells gets a perfect copy of your DNA. How does that happen?",
                    "voice_id": "4XUsiqPDK4UACIM2BILe",
                },
                {
                    "text": "[serious] And when that system breaks down? That's cancer. So yeah — understanding the cell cycle isn't just biology homework. It literally explains one of the most deadly diseases on the planet.",
                    "voice_id": "gnF5qCDI1EmWwqRYMHxn",
                },
                {
                    "text": "[thoughtful] You started as one cell. One. And every single cell in your body right now came from divisions of that original cell. The fidelity required is staggering.",
                    "voice_id": "HSdLdxNgP1KF3yQK3IkB",
                },
                {
                    "text": "[excited] Welcome to today's episode. We're diving deep into Chapter 9 — the cell cycle. By the end of this, you'll be able to walk through every phase of cell division and understand what goes wrong in cancer cells at a molecular level.",
                    "voice_id": "4XUsiqPDK4UACIM2BILe",
                },
            ],
            "messages": [],
        },
    }


    # ---------------------------------------------------------------------------
    # CEREBRAS THINKING — cerebras-specific settings test
    #
    # Validates clear_thinking and disable_reasoning on a cerebras_reasoning model.
    # The model is pinned here; swap settings_to_use["config"]["model"] below to
    # run the exact same prompt against any other provider.
    # ---------------------------------------------------------------------------
    cerebras_thinking_settings = {
        "debug": True,
        "config": {
            "model": cerebras_reasoning,
            "stream": True,
            "temperature": 1,
            "top_p": 0.95,
            "max_output_tokens": 4096,
            # Cerebras-specific: strip <thinking> blocks from the final response
            "clear_thinking": False,
            # Cerebras-specific: False = reasoning ON (maps to reasoning_effort="medium"
            # on all providers so intent is preserved when the model is swapped)
            "disable_reasoning": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a rigorous analytical assistant. "
                        "Think carefully before every answer. "
                        "Show your full reasoning process."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "A train leaves City A at 9:00 AM travelling at 120 km/h. "
                        "Another train leaves City B at 10:00 AM travelling toward City A "
                        "at 80 km/h. The cities are 400 km apart. "
                        "At what time do the trains meet, and how far is the meeting point "
                        "from City A? Show every step of your reasoning."
                    ),
                },
            ],
        },
    }

    # ---------------------------------------------------------------------------
    # CEREBRAS TOOL CALL — tests that tool calling still works alongside
    # the new disable_reasoning / clear_thinking knobs.
    #
    # Uses a single lightweight tool (news_get_headlines) so we get at least
    # one full tool-call round-trip to confirm the translator doesn't corrupt
    # the request when reasoning params are present.
    #
    # The model is pinned to cerebras_reasoning but the config is intentionally
    # written so it runs unmodified against any other provider — just change
    # settings_to_use["config"]["model"] below.
    # ---------------------------------------------------------------------------
    cerebras_tool_settings = {
        "debug": True,
        "config": {
            "model": cerebras_reasoning,
            "stream": True,
            "temperature": 1,
            "top_p": 0.95,
            "max_output_tokens": 4096,
            # Cerebras-specific knobs — will be silently dropped on other providers
            "clear_thinking": True,
            "disable_reasoning": False,
            "tools": [
                "news_get_headlines",
            ],
            "tool_choice": "auto",
            "parallel_tool_calls": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"You are a helpful news assistant. Today's date is {datetime.now().strftime('%Y-%m-%d')}. "
                        "Use the available tools to fetch current headlines before answering."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "What are the top US news headlines right now? "
                        "Fetch the latest and give me a brief summary of each one."
                    ),
                },
            ],
        },
    }

    # options: simple_chat_settings, single_tool_settings_v2, image_generation_settings,
    #          complex_settings, document_input_settings, youtube_url_settings,
    #          audio_transcription_test_settings, audio_direct_google_settings,
    #          podcast_direct_settings, elevenlabs_dialogue_settings,
    #          multiple_tools_settings, cerebras_thinking_settings,
    #          cerebras_tool_settings
    settings_to_use = cerebras_thinking_settings

    # Models: claude_adaptive, openai_reasoning, google, openai_tts_mini
    settings_to_use["config"]["model"] = openai
    settings_to_use["debug"] = True

    if TEST_MODE == "api":
        # ------------------------------------------------------------------
        # API MODE — fires real HTTP against the running server.
        # Make sure `python run.py` is running before executing this.
        # Switch between the three route wrappers as needed.
        # ------------------------------------------------------------------
        vcprint(f"\n[TEST MODE] api → {_API_BASE}", color="magenta")

        # Option A: /ai/chat  (supply full config dict)
        asyncio.run(
            test_api_chat(
                settings_to_use["config"],
                debug=settings_to_use.get("debug", False),
            )
        )

        # Option B: /ai/agents/{agent_id}  (uncomment and set TEST_AGENT_ID)
        # asyncio.run(
        #     test_api_agent(
        #         TEST_AGENT_ID,
        #         user_input="Hello! What can you do?",
        #         debug=False,
        #     )
        # )

        # Option C: /ai/conversations/{conversation_id}  (uncomment and set TEST_CONVERSATION_ID)
        # asyncio.run(
        #     test_api_conversation(
        #         TEST_CONVERSATION_ID,
        #         user_input="Continue from where we left off.",
        #         debug=False,
        #     )
        # )

    else:
        # ------------------------------------------------------------------
        # DIRECT MODE (default) — calls execute_ai_request() in-process.
        # No server needed. Fastest feedback loop.
        # ------------------------------------------------------------------
        vcprint("\n[TEST MODE] direct (in-process)", color="magenta")

        final_result, storage_data = asyncio.run(
            test_autonomous_execution(
                settings_to_use["config"],
                debug=settings_to_use.get("debug", False),
            )
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

        # Save in cx_ storage format (database-ready, computed while AppContext was alive)
        storage_serializable = to_matrx_json(storage_data)
        output_file = Path(__file__).parent / "cx_storage_response.json"
        with open(output_file, "w") as f:
            json.dump(storage_serializable, f, indent=4)
        vcprint(f"\nCX storage format saved to: {output_file}", color="blue")

    # Clean up async resources to prevent ResourceWarnings
    cleanup_async_resources()
