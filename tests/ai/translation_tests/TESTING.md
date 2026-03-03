# LLM Translation Round-Trip Test Suite

## Overview

This test suite validates zero-loss bidirectional translation between the unified config schema and all native LLM provider schemas (OpenAI, Anthropic, Google Gemini, Groq, Cerebras, Together AI, xAI). It covers:

1. **In-memory translation** — Content type serialization, storage round-trips, provider format conversion
2. **Database persistence** — JSONB simulation, live DB read/write
3. **Response capture** — Recording real LLM responses for future test fixtures

## Running the Tests

### All translation tests (no DB required)
```bash
pytest tests/ai/translation_tests/ -v
```

### In-memory tests only
```bash
pytest tests/ai/translation_tests/test_inmemory_translation.py -v
```

### Database persistence tests (requires .env credentials)
```bash
pytest tests/ai/translation_tests/test_db_persistence.py -v
```

### Response capture system tests
```bash
pytest tests/ai/translation_tests/test_response_capture.py -v
```

### Skip DB-dependent tests
```bash
pytest tests/ai/translation_tests/ -v -m "not db"
```

### Run a specific fixture
```bash
pytest tests/ai/translation_tests/test_inmemory_translation.py -v -k "long_15_plus"
```

## Test Architecture

```
tests/ai/translation_tests/
├── TESTING.md                  ← This file
├── conftest.py                 ← Shared fixtures, markers
├── fixtures/
│   ├── __init__.py
│   └── multi_turn_conversations.py  ← 14 fixture conversations (200+ messages total)
├── captured_responses/         ← Auto-generated from live LLM calls
├── response_capture.py         ← Capture utility for recording real responses
├── test_inmemory_translation.py     ← In-memory round-trip tests (~100 tests)
├── test_db_persistence.py           ← DB persistence tests
└── test_response_capture.py         ← Tests for the capture utility itself
```

## What's Tested

### Content Types (each tested for storage round-trip + provider conversion)
- **TextContent** — plain text, citations, unicode, long strings, empty strings
- **ThinkingContent** — OpenAI (bytes signature), Anthropic (string signature), Google (bytes thought_signature)
- **ToolCallContent** — simple args, deeply nested JSON, empty args
- **ToolResultContent** — string content, list content, JSON strings, error flag
- **ImageContent** — URL, base64, file_uri, media_resolution
- **AudioContent** — URL, transcription metadata
- **VideoContent** — URL, file_uri, video metadata
- **YouTubeVideoContent** — URL
- **DocumentContent** — URL, file_uri, mime_type
- **CodeExecutionContent** — code, language
- **CodeExecutionResultContent** — outcome, output
- **WebSearchCallContent** — id, status, action

### Round-Trip Scenarios
- **Single round-trip**: unified → storage → reconstruct
- **Double round-trip**: unified → storage → reconstruct → storage → reconstruct (idempotency)
- **JSONB simulation**: storage → json.dumps → json.loads → reconstruct (simulates PostgreSQL JSONB)
- **Cross-provider isolation**: OpenAI thinking → to_anthropic() returns None, etc.
- **Provider format conversion**: every message in every fixture converts to OpenAI/Anthropic/Google format without errors

### Fixtures
| ID | Messages | Content Types |
|----|----------|---------------|
| `simple_text` | 3 | text |
| `openai_thinking` | 6 | text, thinking (OpenAI, bytes sig) |
| `anthropic_thinking` | 4 | text, thinking (Anthropic, string sig) |
| `google_thinking` | 2 | text, thinking (Google, bytes sig) |
| `tool_calls_multi_turn` | 17 | text, thinking, tool_call, tool_result |
| `image_conversation` | 6 | text, image (URL, base64, file_uri) |
| `anthropic_tool_calls` | 8 | text, thinking, tool_call, tool_result |
| `mixed_media` | 8 | text, image, document, youtube, audio |
| `code_execution` | 4 | text, code_execution, code_execution_result |
| `error_tool_result` | 4 | text, tool_call, tool_result (is_error) |
| `cross_provider_thinking` | 8 | text, thinking (3 providers in 1 conversation) |
| `long_15_plus` | 18 | text, thinking, tool_call, tool_result, image |
| `parallel_tool_calls` | 8 | text, tool_call, tool_result (3 parallel) |
| `complex_tool_args` | 6 | text, tool_call (deep nested args), tool_result |

## Adding New Test Data

### Option 1: Add a fixture function

In `fixtures/multi_turn_conversations.py`:

```python
def my_new_conversation() -> dict:
    return {
        "id": "my_new_test",
        "description": "Short description",
        "model": "gpt-5",
        "system_instruction": "You are helpful.",
        "temperature": 0.5,
        "max_output_tokens": 4096,
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
            {"role": "assistant", "content": [{"type": "text", "text": "Hi!"}]},
        ],
    }

# Then add to ALL_FIXTURES list at the bottom:
ALL_FIXTURES.append(my_new_conversation())
```

All parametrized tests automatically pick up new fixtures.

### Option 2: Capture real LLM responses

```bash
# Enable capture
export MATRX_CAPTURE_LLM_RESPONSES=1

# Run your app / tests that make real LLM calls
python -m matrx_ai.app.main  # or whatever triggers LLM calls

# Captured responses appear in:
# tests/ai/translation_tests/captured_responses/
```

Then load them in tests:
```python
from tests.ai.translation_tests.response_capture import load_captured_responses

for captured in load_captured_responses(provider="openai"):
    response_dict = captured["response"]
    # Use in assertions
```

### Option 3: Add integration points for continuous capture

Add this one-liner in each provider's execute path (just before translation):

```python
# providers/openai/openai_api.py — after response = await client.responses.create(...)
from tests.ai.translation_tests.response_capture import capture_provider_response
capture_provider_response("openai", config_data["model"], response.model_dump(),
                         {"turn": turn_count, "has_tools": bool(config.tools)})

# providers/anthropic/anthropic_api.py
capture_provider_response("anthropic", config_data["model"], response.model_dump())

# providers/google/google_api.py (after accumulating chunks)
capture_provider_response("google", model_name, accumulated_response)
```

When `MATRX_CAPTURE_LLM_RESPONSES` is not set, these calls are no-ops (return None immediately).

## Environment Variables

| Variable | Required For | Description |
|----------|-------------|-------------|
| `MATRX_CAPTURE_LLM_RESPONSES` | Capture system | Set to `1` to enable response capture |
| `SUPABASE_MATRIX_HOST` | DB tests | Database host |
| `SUPABASE_MATRIX_PASSWORD` | DB tests | Database password |
| `DEVELOPER_USER_ID` | DB tests | Your Supabase user UUID |
| `TEST_USER_EMAIL` | DB tests | Your Supabase email |
