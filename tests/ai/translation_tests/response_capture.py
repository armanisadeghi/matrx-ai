"""
Response Capture System — Record Raw LLM Responses for Test Fixtures.

Captures the raw native response from any provider BEFORE translation to
unified format, saving it as a JSON file for later use as test data.

Quick start — Enable capture and make normal LLM calls:
    export MATRX_CAPTURE_LLM_RESPONSES=1
    # Run your application / tests as normal
    # Captured files appear in tests/ai/translation_tests/captured_responses/

Integration — Add one line in each provider's execute path:
    # In providers/openai/openai_api.py, after response = await ...:
    from tests.ai.translation_tests.response_capture import capture_provider_response
    capture_provider_response("openai", "gpt-5", response.model_dump(), {"turn": 3})

    # In providers/anthropic/anthropic_api.py:
    capture_provider_response("anthropic", "claude-sonnet-4-6", response.model_dump())

    # In providers/google/google_api.py (after accumulating chunks):
    capture_provider_response("google", "gemini-3-pro", accumulated_dict)

    # Similarly for groq, cerebras, together, xai

Load captured data as test fixtures:
    from tests.ai.translation_tests.response_capture import load_captured_responses
    for captured in load_captured_responses(provider="openai"):
        response_dict = captured["response"]
        # Use response_dict in tests
"""

import json
import os
import time
from pathlib import Path
from typing import Any

CAPTURE_DIR = Path(__file__).parent / "captured_responses"
CAPTURE_DIR.mkdir(exist_ok=True)

_CAPTURE_ENABLED_ENV = "MATRX_CAPTURE_LLM_RESPONSES"


def is_capture_enabled() -> bool:
    return os.environ.get(_CAPTURE_ENABLED_ENV, "").lower() in ("1", "true", "yes")


def _json_serializer(obj: Any) -> Any:
    """Handle bytes, Pydantic models, and arbitrary objects."""
    import base64

    if isinstance(obj, bytes):
        return {"__bytes__": True, "data": base64.b64encode(obj).decode("ascii")}
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    return str(obj)


def _json_deserializer(dct: dict) -> Any:
    """Restore bytes from serialized form."""
    import base64

    if "__bytes__" in dct and dct.get("__bytes__") is True:
        return base64.b64decode(dct["data"])
    return dct


def capture_provider_response(
    provider: str,
    model: str,
    response: dict[str, Any] | list[dict[str, Any]],
    conversation_context: dict[str, Any] | None = None,
    label: str = "",
) -> Path | None:
    """
    Save a raw provider response to JSON.

    Returns:
        Path to saved file, or None if capture is disabled.
    """
    if not is_capture_enabled():
        return None

    timestamp = int(time.time() * 1000)
    safe_model = model.replace("/", "_").replace(".", "_")
    label_part = f"_{label}" if label else ""
    filename = f"{provider}_{safe_model}{label_part}_{timestamp}.json"
    filepath = CAPTURE_DIR / filename

    capture_data = {
        "capture_metadata": {
            "provider": provider,
            "model": model,
            "timestamp_ms": timestamp,
            "label": label,
            "context": conversation_context or {},
        },
        "response": response,
    }

    with open(filepath, "w") as f:
        json.dump(capture_data, f, indent=2, default=_json_serializer)

    return filepath


def load_captured_responses(
    provider: str | None = None,
    model: str | None = None,
    label: str | None = None,
) -> list[dict[str, Any]]:
    """Load captured responses, optionally filtered by provider/model/label."""
    results = []
    if not CAPTURE_DIR.exists():
        return results

    for filepath in sorted(CAPTURE_DIR.glob("*.json")):
        try:
            with open(filepath) as f:
                data = json.load(f, object_hook=_json_deserializer)
            meta = data.get("capture_metadata", {})
            if provider and meta.get("provider") != provider:
                continue
            if model and model not in meta.get("model", ""):
                continue
            if label and label not in meta.get("label", ""):
                continue
            data["_filepath"] = str(filepath)
            results.append(data)
        except (json.JSONDecodeError, KeyError):
            continue

    return results


def load_captured_as_fixture(filepath: str | Path) -> dict[str, Any]:
    """Load a single captured file as a test fixture dict."""
    with open(filepath) as f:
        data = json.load(f, object_hook=_json_deserializer)
    meta = data.get("capture_metadata", {})
    return {
        "provider": meta.get("provider", "unknown"),
        "model": meta.get("model", "unknown"),
        "response": data.get("response", {}),
        "context": meta.get("context", {}),
    }


def clear_captured_responses() -> int:
    """Delete all captured files. Returns count deleted."""
    count = 0
    if CAPTURE_DIR.exists():
        for fp in CAPTURE_DIR.glob("*.json"):
            fp.unlink()
            count += 1
    return count
