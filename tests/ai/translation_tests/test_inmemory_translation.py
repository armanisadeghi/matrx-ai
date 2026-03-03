"""
In-Memory Translation Round-Trip Tests.

Validates that every content type survives:
  unified → to_storage_dict → reconstruct_content → to_storage_dict (idempotent)
and can be converted to each provider format without errors.

No database, no API keys required.

Run:
    pytest tests/ai/translation_tests/test_inmemory_translation.py -v
"""

import copy
import json

import pytest

from matrx_ai.config import (
    CodeExecutionContent,
    CodeExecutionResultContent,
    ImageContent,
    TextContent,
    ThinkingContent,
    ToolCallContent,
    ToolResultContent,
    UnifiedConfig,
    UnifiedMessage,
    WebSearchCallContent,
    reconstruct_content,
)
from matrx_ai.config.media_config import (
    AudioContent,
    DocumentContent,
    VideoContent,
    YouTubeVideoContent,
    reconstruct_media_content,
)

from .fixtures.multi_turn_conversations import (
    ALL_FIXTURES,
    FAKE_ANTHROPIC_SIGNATURE,
    FAKE_GOOGLE_SIGNATURE,
    FAKE_OPENAI_SIGNATURE,
    TINY_PNG_BASE64,
    get_all_fixture_ids,
    get_fixture_by_id,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _can_import_translators() -> bool:
    """Check if provider translator modules can be imported (requires fastapi)."""
    try:
        import fastapi  # noqa: F401
        return True
    except ImportError:
        return False


def _build_config(fixture: dict) -> UnifiedConfig:
    """Build UnifiedConfig from fixture dict (same shape as from_dict input)."""
    # Extract fixture-only keys that are not UnifiedConfig fields
    data = {k: v for k, v in fixture.items() if k not in ("id", "description")}
    return UnifiedConfig.from_dict(data)


def _deep_compare(a, b, path: str = "") -> list[str]:
    """Return list of difference descriptions between two values."""
    diffs: list[str] = []
    if type(a) is not type(b):
        if isinstance(a, (int, float)) and isinstance(b, (int, float)):
            if a != b:
                diffs.append(f"{path}: {a!r} != {b!r}")
        else:
            diffs.append(f"{path}: type {type(a).__name__} vs {type(b).__name__}")
        return diffs

    if isinstance(a, dict):
        for key in sorted(set(a) | set(b)):
            if key not in a:
                diffs.append(f"{path}.{key}: missing in first")
            elif key not in b:
                diffs.append(f"{path}.{key}: missing in second")
            else:
                diffs.extend(_deep_compare(a[key], b[key], f"{path}.{key}"))
    elif isinstance(a, list):
        if len(a) != len(b):
            diffs.append(f"{path}: len {len(a)} vs {len(b)}")
        for i, (x, y) in enumerate(zip(a, b)):
            diffs.extend(_deep_compare(x, y, f"{path}[{i}]"))
    elif isinstance(a, bytes):
        if a != b:
            diffs.append(f"{path}: bytes differ (len {len(a)} vs {len(b)})")
    elif a != b:
        diffs.append(f"{path}: {a!r} != {b!r}")
    return diffs


# ============================================================================
# INDIVIDUAL CONTENT TYPE TESTS
# ============================================================================


class TestTextContentRoundTrip:

    def test_simple(self):
        orig = TextContent(text="Hello, world!", id="txt_001")
        stored = orig.to_storage_dict()
        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, TextContent)
        assert rebuilt.text == orig.text
        assert rebuilt.id == orig.id

    def test_with_citations(self):
        cites = [{"url": "https://a.com", "title": "A", "start_index": 0, "end_index": 5}]
        orig = TextContent(text="Text.", id="c1", metadata={"citations": cites})
        stored = orig.to_storage_dict()
        assert stored["citations"] == cites
        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, TextContent)
        assert rebuilt.metadata.get("citations") == cites

    def test_to_openai_roles(self):
        tc = TextContent(text="Hi")
        assert tc.to_openai(role="user")["type"] == "input_text"
        assert tc.to_openai(role="assistant")["type"] == "output_text"

    def test_to_anthropic(self):
        assert TextContent(text="Hi").to_anthropic() == {"type": "text", "text": "Hi"}

    def test_to_google(self):
        assert TextContent(text="Hi").to_google() == {"text": "Hi"}

    def test_google_thought_signature_in_metadata(self):
        tc = TextContent(text="R", metadata={"google_thought_signature": FAKE_GOOGLE_SIGNATURE})
        g = tc.to_google()
        assert g["thoughtSignature"] == FAKE_GOOGLE_SIGNATURE

    def test_empty_text_roundtrip(self):
        orig = TextContent(text="")
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert isinstance(rebuilt, TextContent)
        assert rebuilt.text == ""

    def test_unicode_text(self):
        txt = "日本語テスト 🎉 Ñoño"
        rebuilt = reconstruct_content(TextContent(text=txt).to_storage_dict())
        assert rebuilt.text == txt

    def test_long_text(self):
        txt = "x" * 100_000
        rebuilt = reconstruct_content(TextContent(text=txt).to_storage_dict())
        assert rebuilt.text == txt


class TestThinkingContentRoundTrip:

    def test_openai_bytes_signature(self):
        orig = ThinkingContent(
            id="rs_001", provider="openai", signature=FAKE_OPENAI_SIGNATURE,
            summary=[{"type": "summary_text", "text": "test"}],
        )
        stored = orig.to_storage_dict()
        assert stored["signature_encoding"] == "base64"
        assert isinstance(stored["signature"], str)

        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, ThinkingContent)
        assert rebuilt.provider == "openai"
        assert rebuilt.signature == FAKE_OPENAI_SIGNATURE
        assert isinstance(rebuilt.signature, bytes)
        assert rebuilt.id == "rs_001"
        assert rebuilt.summary[0]["text"] == "test"

    def test_anthropic_string_signature(self):
        orig = ThinkingContent(
            text="Analysis...", provider="anthropic", signature=FAKE_ANTHROPIC_SIGNATURE,
        )
        stored = orig.to_storage_dict()
        assert "signature_encoding" not in stored
        assert stored["signature"] == FAKE_ANTHROPIC_SIGNATURE

        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, ThinkingContent)
        assert rebuilt.signature == FAKE_ANTHROPIC_SIGNATURE
        assert rebuilt.text == "Analysis..."

    def test_google_bytes_signature(self):
        orig = ThinkingContent(
            text="Thought...", provider="google", signature=FAKE_GOOGLE_SIGNATURE,
        )
        stored = orig.to_storage_dict()
        assert stored["signature_encoding"] == "base64"

        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, ThinkingContent)
        assert rebuilt.signature == FAKE_GOOGLE_SIGNATURE
        assert isinstance(rebuilt.signature, bytes)

    def test_openai_to_openai(self):
        tc = ThinkingContent(
            id="rs_x", provider="openai", signature=FAKE_OPENAI_SIGNATURE,
            summary=[{"type": "summary_text", "text": "S"}],
        )
        result = tc.to_openai()
        assert result is not None
        assert result["type"] == "reasoning"
        assert result["encrypted_content"] == FAKE_OPENAI_SIGNATURE
        assert result["id"] == "rs_x"

    def test_cross_provider_isolation_openai(self):
        tc = ThinkingContent(provider="openai", signature=FAKE_OPENAI_SIGNATURE)
        assert tc.to_openai() is not None
        assert tc.to_anthropic() is None
        assert tc.to_google() is None

    def test_cross_provider_isolation_anthropic(self):
        tc = ThinkingContent(text="t", provider="anthropic", signature=FAKE_ANTHROPIC_SIGNATURE)
        assert tc.to_openai() is None
        assert tc.to_anthropic() is not None
        assert tc.to_google() is None

    def test_cross_provider_isolation_google(self):
        tc = ThinkingContent(text="t", provider="google", signature=FAKE_GOOGLE_SIGNATURE)
        assert tc.to_openai() is None
        assert tc.to_anthropic() is None
        assert tc.to_google() is not None

    def test_no_signature_returns_none_for_all(self):
        tc = ThinkingContent(text="bare", provider="openai", signature=None)
        assert tc.to_openai() is None
        assert tc.to_anthropic() is None
        assert tc.to_google() is None

    def test_anthropic_to_anthropic_fields(self):
        tc = ThinkingContent(text="T", provider="anthropic", signature=FAKE_ANTHROPIC_SIGNATURE)
        r = tc.to_anthropic()
        assert r["type"] == "thinking"
        assert r["thinking"] == "T"
        assert r["signature"] == FAKE_ANTHROPIC_SIGNATURE

    def test_google_to_google_fields(self):
        tc = ThinkingContent(text="G", provider="google", signature=FAKE_GOOGLE_SIGNATURE)
        r = tc.to_google()
        assert r["thought"] is True
        assert r["text"] == "G"
        assert r["thoughtSignature"] == FAKE_GOOGLE_SIGNATURE


class TestToolCallContentRoundTrip:

    def test_basic_roundtrip(self):
        orig = ToolCallContent(
            id="tool_001", call_id="call_abc", name="get_weather",
            arguments={"city": "SF", "days": 3},
        )
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert isinstance(rebuilt, ToolCallContent)
        assert rebuilt.id == "tool_001"
        assert rebuilt.call_id == "call_abc"
        assert rebuilt.name == "get_weather"
        assert rebuilt.arguments == {"city": "SF", "days": 3}

    def test_to_openai(self):
        tc = ToolCallContent(id="t1", call_id="c1", name="fn", arguments={"a": 1})
        r = tc.to_openai()
        assert r["type"] == "function_call"
        assert r["name"] == "fn"
        assert json.loads(r["arguments"]) == {"a": 1}

    def test_to_anthropic(self):
        tc = ToolCallContent(id="toolu_x", name="search", arguments={"q": "test"})
        r = tc.to_anthropic()
        assert r["type"] == "tool_use"
        assert r["id"] == "toolu_x"
        assert r["input"] == {"q": "test"}

    def test_to_google(self):
        tc = ToolCallContent(name="calc", arguments={"expr": "2+2"})
        r = tc.to_google()
        assert r["functionCall"]["name"] == "calc"
        assert r["functionCall"]["args"] == {"expr": "2+2"}

    def test_deeply_nested_arguments(self):
        args = {
            "query": "SELECT *",
            "params": {"timeout": 30, "cache": True},
            "filters": [
                {"field": "age", "op": ">", "value": 18},
                {"field": "status", "op": "==", "value": "active"},
            ],
            "nested": {"a": {"b": {"c": [1, 2, {"d": 3}]}}},
        }
        rebuilt = reconstruct_content(ToolCallContent(id="tc", name="q", arguments=args).to_storage_dict())
        assert isinstance(rebuilt, ToolCallContent)
        assert rebuilt.arguments == args


class TestToolResultContentRoundTrip:

    def test_string_content(self):
        orig = ToolResultContent(
            tool_use_id="toolu_1", call_id="call_1", name="weather", content="Sunny 72°F",
        )
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert isinstance(rebuilt, ToolResultContent)
        assert rebuilt.content == "Sunny 72°F"
        assert rebuilt.tool_use_id == "toolu_1"

    def test_list_content(self):
        data = [{"product": "A", "rev": 1000}, {"product": "B", "rev": 2000}]
        rebuilt = reconstruct_content(ToolResultContent(tool_use_id="t", name="q", content=data).to_storage_dict())
        assert rebuilt.content == data

    def test_error_flag(self):
        orig = ToolResultContent(tool_use_id="te", name="db", content="Timeout", is_error=True)
        stored = orig.to_storage_dict()
        assert stored["is_error"] is True
        rebuilt = reconstruct_content(stored)
        assert rebuilt.is_error is True

    def test_to_openai(self):
        tr = ToolResultContent(call_id="c1", content={"r": "ok"})
        r = tr.to_openai()
        assert r["type"] == "function_call_output"
        assert r["call_id"] == "c1"

    def test_to_anthropic(self):
        tr = ToolResultContent(tool_use_id="toolu_1", content="Result")
        r = tr.to_anthropic()
        assert r["type"] == "tool_result"
        assert r["tool_use_id"] == "toolu_1"

    def test_to_anthropic_error(self):
        tr = ToolResultContent(tool_use_id="t", content="Err", is_error=True)
        assert tr.to_anthropic()["is_error"] is True


class TestMediaContentRoundTrip:

    def test_image_url(self):
        orig = ImageContent(url="https://a.com/i.jpg", mime_type="image/jpeg")
        stored = orig.to_storage_dict()
        assert stored["type"] == "media"
        assert stored["kind"] == "image"
        rebuilt = reconstruct_media_content(stored)
        assert isinstance(rebuilt, ImageContent)
        assert rebuilt.url == "https://a.com/i.jpg"

    def test_image_base64(self):
        orig = ImageContent(base64_data=TINY_PNG_BASE64, mime_type="image/png")
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert isinstance(rebuilt, ImageContent)
        assert rebuilt.base64_data == TINY_PNG_BASE64

    def test_image_file_uri(self):
        orig = ImageContent(file_uri="gs://b/img.jpg", mime_type="image/jpeg")
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert rebuilt.file_uri == "gs://b/img.jpg"

    def test_image_media_resolution(self):
        orig = ImageContent(url="https://a.com/hi.jpg", mime_type="image/jpeg", media_resolution="HIGH")
        stored = orig.to_storage_dict()
        assert stored["metadata"]["media_resolution"] == "HIGH"
        rebuilt = reconstruct_media_content(stored)
        assert rebuilt.media_resolution == "HIGH"

    def test_audio(self):
        orig = AudioContent(url="https://a.com/a.mp3", mime_type="audio/mpeg", auto_transcribe=True, transcription_result="Hello")
        stored = orig.to_storage_dict()
        assert stored["kind"] == "audio"
        rebuilt = reconstruct_media_content(stored)
        assert isinstance(rebuilt, AudioContent)
        assert rebuilt.auto_transcribe is True
        assert rebuilt.transcription_result == "Hello"

    def test_video(self):
        orig = VideoContent(file_uri="gs://b/v.mp4", mime_type="video/mp4", video_metadata={"start": 0, "end": 120})
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert isinstance(rebuilt, VideoContent)
        assert rebuilt.video_metadata == {"start": 0, "end": 120}

    def test_youtube(self):
        orig = YouTubeVideoContent(url="https://www.youtube.com/watch?v=abc123")
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert isinstance(rebuilt, YouTubeVideoContent)
        assert rebuilt.url == "https://www.youtube.com/watch?v=abc123"

    def test_document(self):
        orig = DocumentContent(url="https://a.com/r.pdf", mime_type="application/pdf")
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert isinstance(rebuilt, DocumentContent)
        assert rebuilt.mime_type == "application/pdf"


class TestCodeExecutionRoundTrip:

    def test_code_exec(self):
        orig = CodeExecutionContent(code="print(1)", language="python")
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert isinstance(rebuilt, CodeExecutionContent)
        assert rebuilt.code == "print(1)"
        assert rebuilt.language == "python"

    def test_code_result(self):
        orig = CodeExecutionResultContent(outcome="success", output="1\n")
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert isinstance(rebuilt, CodeExecutionResultContent)
        assert rebuilt.outcome == "success"
        assert rebuilt.output == "1\n"


class TestWebSearchRoundTrip:

    def test_web_search(self):
        orig = WebSearchCallContent(
            id="ws_1", status="completed",
            action={"type": "search", "query": "test", "sources": [{"url": "https://a.com"}]},
        )
        stored = orig.to_storage_dict()
        assert stored["type"] == "web_search"
        rebuilt = reconstruct_content(stored)
        assert isinstance(rebuilt, WebSearchCallContent)
        assert rebuilt.id == "ws_1"
        assert rebuilt.action["query"] == "test"


# ============================================================================
# UNIFIED MESSAGE TESTS
# ============================================================================


class TestUnifiedMessageRoundTrip:

    def test_simple_user(self):
        msg = UnifiedMessage(role="user", content=[TextContent(text="Hi!")])
        stored = msg.to_storage_dict()
        assert stored["role"] == "user"
        assert len(stored["content"]) == 1

    def test_assistant_thinking_plus_text(self):
        msg = UnifiedMessage(role="assistant", content=[
            ThinkingContent(text="Hmm...", provider="anthropic", signature=FAKE_ANTHROPIC_SIGNATURE),
            TextContent(text="42."),
        ])
        stored = msg.to_storage_dict()
        assert len(stored["content"]) == 2
        assert stored["content"][0]["type"] == "thinking"
        assert stored["content"][1]["type"] == "text"
        r0 = reconstruct_content(stored["content"][0])
        r1 = reconstruct_content(stored["content"][1])
        assert isinstance(r0, ThinkingContent) and r0.signature == FAKE_ANTHROPIC_SIGNATURE
        assert isinstance(r1, TextContent) and r1.text == "42."

    def test_user_image_plus_text(self):
        msg = UnifiedMessage(role="user", content=[
            TextContent(text="What's this?"),
            ImageContent(url="https://x.com/i.jpg", mime_type="image/jpeg"),
        ])
        stored = msg.to_storage_dict()
        assert stored["content"][0]["type"] == "text"
        assert stored["content"][1]["type"] == "media"
        assert stored["content"][1]["kind"] == "image"


# ============================================================================
# FULL CONVERSATION ROUND-TRIP (parametrized over all fixtures)
# ============================================================================


class TestConversationStorageRoundTrip:
    """Each fixture → UnifiedConfig → to_storage_dict → reconstruct → verify."""

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_storage_roundtrip(self, fixture_id: str):
        fixture = get_fixture_by_id(fixture_id)
        config = _build_config(fixture)
        storage = config.to_storage_dict()

        assert storage["model"] == fixture["model"]
        msgs = list(config.messages)
        assert len(storage["messages"]) == len(msgs)

        for i, (orig_msg, stored_msg) in enumerate(zip(msgs, storage["messages"])):
            role_str = orig_msg.role.value if hasattr(orig_msg.role, "value") else orig_msg.role
            assert stored_msg["role"] == role_str, f"msg[{i}] role mismatch"
            assert len(stored_msg["content"]) == len(orig_msg.content), f"msg[{i}] content count"

            for j, (oc, sc) in enumerate(zip(orig_msg.content, stored_msg["content"])):
                rebuilt = reconstruct_content(sc)
                assert type(rebuilt).__name__ == type(oc).__name__, (
                    f"msg[{i}].content[{j}] type: {type(rebuilt).__name__} vs {type(oc).__name__}"
                )
                if isinstance(oc, TextContent):
                    assert rebuilt.text == oc.text
                if isinstance(oc, ThinkingContent):
                    assert rebuilt.provider == oc.provider
                    if oc.signature is not None:
                        assert rebuilt.signature == oc.signature
                if isinstance(oc, ToolCallContent):
                    assert rebuilt.name == oc.name
                    assert rebuilt.arguments == oc.arguments
                if isinstance(oc, ToolResultContent):
                    assert rebuilt.content == oc.content
                    assert rebuilt.is_error == oc.is_error


class TestDoubleStorageRoundTrip:
    """serialize → reconstruct → serialize → reconstruct → compare storage dicts."""

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_idempotent(self, fixture_id: str):
        fixture = get_fixture_by_id(fixture_id)
        config = _build_config(fixture)

        for mi, msg in enumerate(config.messages):
            for ci, content in enumerate(msg.content):
                s1 = content.to_storage_dict()
                r1 = reconstruct_content(s1)
                s2 = r1.to_storage_dict()
                diffs = _deep_compare(s1, s2, f"msg[{mi}].content[{ci}]")
                assert not diffs, "Double round-trip diffs:\n" + "\n".join(diffs)


class TestProviderConversionNoError:
    """Every fixture message converts to each provider format without exceptions."""

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_to_openai(self, fixture_id: str):
        config = _build_config(get_fixture_by_id(fixture_id))
        for msg in config.messages:
            msg.to_openai_items()  # should not raise

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_to_anthropic(self, fixture_id: str):
        config = _build_config(get_fixture_by_id(fixture_id))
        for msg in config.messages:
            result = msg.to_anthropic_blocks()
            assert isinstance(result, list)

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_to_google(self, fixture_id: str):
        config = _build_config(get_fixture_by_id(fixture_id))
        for msg in config.messages:
            role_str = msg.role.value if hasattr(msg.role, "value") else msg.role
            if role_str in ("user", "assistant", "tool"):
                try:
                    msg.to_google_content()  # should not raise
                except Exception as exc:
                    # Google's image conversion may try to download URLs;
                    # HTTP errors from fake URLs are acceptable in tests.
                    import requests

                    if isinstance(exc, requests.HTTPError):
                        pass  # Expected for test URLs
                    else:
                        raise


class TestCrossProviderThinkingIsolation:

    def test_cross_provider_fixture(self):
        """Each thinking block only converts to its own provider, None otherwise."""
        config = _build_config(get_fixture_by_id("cross_provider_thinking"))
        for msg in config.messages:
            for content in msg.content:
                if isinstance(content, ThinkingContent):
                    p = content.provider
                    if p == "openai":
                        assert content.to_openai() is not None
                        assert content.to_anthropic() is None
                        assert content.to_google() is None
                    elif p == "anthropic":
                        assert content.to_anthropic() is not None
                        assert content.to_openai() is None
                        assert content.to_google() is None
                    elif p == "google":
                        assert content.to_google() is not None
                        assert content.to_openai() is None
                        assert content.to_anthropic() is None

    def test_all_signatures_survive_storage(self):
        """Every thinking block with a signature keeps it through storage."""
        config = _build_config(get_fixture_by_id("cross_provider_thinking"))
        for msg in config.messages:
            for content in msg.content:
                if isinstance(content, ThinkingContent) and content.signature is not None:
                    stored = content.to_storage_dict()
                    rebuilt = reconstruct_content(stored)
                    assert isinstance(rebuilt, ThinkingContent)
                    assert rebuilt.signature == content.signature
                    assert rebuilt.provider == content.provider


# ============================================================================
# UNIFIED CONFIG from_dict EDGE CASES
# ============================================================================


class TestUnifiedConfigFromDict:

    def test_system_message_extraction(self):
        data = {
            "model": "gpt-5",
            "messages": [
                {"role": "system", "content": "You are helpful."},
                {"role": "user", "content": "Hi"},
            ],
        }
        config = UnifiedConfig.from_dict(data)
        assert "You are helpful." in (config.system_instruction or "")
        msgs = list(config.messages)
        assert len(msgs) == 1
        assert msgs[0].role == "user" or (hasattr(msgs[0].role, "value") and msgs[0].role.value == "user")

    def test_explicit_system_instruction_priority(self):
        data = {
            "model": "gpt-5",
            "system_instruction": "Priority",
            "messages": [
                {"role": "system", "content": "Ignored."},
                {"role": "user", "content": "Hi"},
            ],
        }
        config = UnifiedConfig.from_dict(data)
        assert config.system_instruction == "Priority"

    def test_max_tokens_alias(self):
        data = {"model": "gpt-5", "max_tokens": 5000, "messages": [{"role": "user", "content": "Hi"}]}
        assert UnifiedConfig.from_dict(data).max_output_tokens == 5000

    def test_string_content_shorthand(self):
        """Messages with content as a plain string should still work."""
        data = {
            "model": "gpt-5",
            "messages": [{"role": "user", "content": "Hello plain string"}],
        }
        config = UnifiedConfig.from_dict(data)
        msgs = list(config.messages)
        assert len(msgs) == 1
        assert isinstance(msgs[0].content[0], TextContent)
        assert msgs[0].content[0].text == "Hello plain string"

    def test_tool_choice_normalization(self):
        for val, expected in [("auto", "auto"), ("required", "required"), ("any", "required"), ("none", "none")]:
            data = {"model": "gpt-5", "tool_choice": val, "messages": [{"role": "user", "content": "Hi"}]}
            assert UnifiedConfig.from_dict(data).tool_choice == expected


# ============================================================================
# FULL PROVIDER TRANSLATOR ROUND-TRIP TESTS
# ============================================================================


@pytest.mark.skipif(
    not _can_import_translators(),
    reason="Provider translators require fastapi (install with: uv sync --extra server)",
)
class TestOpenAITranslatorRoundTrip:
    """Test UnifiedConfig → OpenAI format → verify structure."""

    def test_simple_chat(self):
        from matrx_ai.providers.openai.translator import OpenAITranslator

        translator = OpenAITranslator()
        config = _build_config(get_fixture_by_id("simple_text"))
        result = translator.to_openai(config, "openai_standard")

        assert result["model"] == "gpt-5"
        assert isinstance(result["input"], list)
        assert len(result["input"]) > 0

    def test_thinking_fixture(self):
        from matrx_ai.providers.openai.translator import OpenAITranslator

        translator = OpenAITranslator()
        config = _build_config(get_fixture_by_id("openai_thinking"))
        result = translator.to_openai(config, "openai_reasoning")

        assert result["model"] == "gpt-5"
        assert "reasoning" in result

    def test_tool_calls_fixture(self):
        from matrx_ai.providers.openai.translator import OpenAITranslator

        translator = OpenAITranslator()
        config = _build_config(get_fixture_by_id("tool_calls_multi_turn"))
        result = translator.to_openai(config, "openai_standard")

        assert isinstance(result["input"], list)
        assert len(result["input"]) > 0


@pytest.mark.skipif(
    not _can_import_translators(),
    reason="Provider translators require fastapi (install with: uv sync --extra server)",
)
class TestAnthropicTranslatorRoundTrip:
    """Test UnifiedConfig → Anthropic format → verify structure."""

    def test_simple_chat(self):
        from matrx_ai.providers.anthropic.translator import AnthropicTranslator

        translator = AnthropicTranslator()
        config = _build_config(get_fixture_by_id("simple_text"))
        result = translator.to_anthropic(config)

        assert result["model"] == "gpt-5"
        assert isinstance(result["messages"], list)
        assert "system" in result

    def test_anthropic_thinking_fixture(self):
        from matrx_ai.providers.anthropic.translator import AnthropicTranslator

        translator = AnthropicTranslator()
        config = _build_config(get_fixture_by_id("anthropic_thinking"))
        result = translator.to_anthropic(config, "anthropic_standard")

        assert isinstance(result["messages"], list)
        assert "thinking" in result

    def test_anthropic_tool_calls(self):
        from matrx_ai.providers.anthropic.translator import AnthropicTranslator

        translator = AnthropicTranslator()
        config = _build_config(get_fixture_by_id("anthropic_tool_calls"))
        result = translator.to_anthropic(config)

        assert isinstance(result["messages"], list)


@pytest.mark.skipif(
    not _can_import_translators(),
    reason="Provider translators require fastapi (install with: uv sync --extra server)",
)
class TestGoogleTranslatorRoundTrip:
    """Test UnifiedConfig → Google format → verify structure."""

    def test_simple_chat(self):
        from matrx_ai.providers.google.translator import GoogleTranslator

        translator = GoogleTranslator()
        config = _build_config(get_fixture_by_id("simple_text"))
        result = translator.to_google(config, "google_standard")

        assert result["model"] == "gpt-5"
        assert "contents" in result
        assert "config" in result

    def test_google_thinking_fixture(self):
        from matrx_ai.providers.google.translator import GoogleTranslator

        translator = GoogleTranslator()
        config = _build_config(get_fixture_by_id("google_thinking"))
        result = translator.to_google(config, "google_thinking_3")

        assert "contents" in result

    def test_images_fixture(self):
        from matrx_ai.providers.google.translator import GoogleTranslator

        translator = GoogleTranslator()
        config = _build_config(get_fixture_by_id("image_conversation"))
        result = translator.to_google(config, "google_standard")

        assert "contents" in result
        assert len(result["contents"]) > 0


# ============================================================================
# STRESS TESTS — Large payloads & edge cases
# ============================================================================


class TestStressEdgeCases:

    def test_all_fixtures_have_15_plus_messages(self):
        """At least one fixture must have >= 15 messages."""
        max_msgs = max(len(f["messages"]) for f in ALL_FIXTURES)
        assert max_msgs >= 15, f"Largest fixture has only {max_msgs} messages"

    def test_empty_content_list(self):
        """Message with empty content list should not crash."""
        msg = UnifiedMessage(role="user", content=[])
        stored = msg.to_storage_dict()
        assert stored["content"] == []

    def test_tool_result_with_json_string_content(self):
        """Tool result content that is a JSON string (common pattern)."""
        json_str = json.dumps({"key": "value", "nested": {"a": [1, 2, 3]}})
        orig = ToolResultContent(tool_use_id="t", name="fn", content=json_str)
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert rebuilt.content == json_str

    def test_special_characters_in_text(self):
        """Text with special chars, newlines, tabs, unicode."""
        txt = 'Line1\nLine2\tTabbed "quoted" <html>&amp; 日本語 🎉\x00null'
        rebuilt = reconstruct_content(TextContent(text=txt).to_storage_dict())
        assert rebuilt.text == txt

    def test_large_base64_image(self):
        """Large base64 image data survives round-trip."""
        big_b64 = "A" * 1_000_000  # ~750KB of fake image data
        orig = ImageContent(base64_data=big_b64, mime_type="image/png")
        rebuilt = reconstruct_media_content(orig.to_storage_dict())
        assert rebuilt.base64_data == big_b64

    def test_tool_call_empty_arguments(self):
        """Tool call with empty arguments dict."""
        orig = ToolCallContent(id="t", name="fn", arguments={})
        rebuilt = reconstruct_content(orig.to_storage_dict())
        assert rebuilt.arguments == {}

    def test_many_content_blocks_in_one_message(self):
        """Message with 20 content blocks."""
        blocks = [TextContent(text=f"Block {i}") for i in range(20)]
        msg = UnifiedMessage(role="assistant", content=blocks)
        stored = msg.to_storage_dict()
        assert len(stored["content"]) == 20
        for i, sc in enumerate(stored["content"]):
            r = reconstruct_content(sc)
            assert r.text == f"Block {i}"
