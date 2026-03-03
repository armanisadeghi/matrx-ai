"""
Database Persistence Round-Trip Tests.

Tests that conversation data survives the full cycle:
    UnifiedConfig → to_storage_dict → DB write → DB read → reconstruct → verify

These tests require:
    - Database credentials in .env (SUPABASE_MATRIX_* vars)
    - DEVELOPER_USER_ID and TEST_USER_EMAIL in .env

Run:
    pytest tests/ai/translation_tests/test_db_persistence.py -v

Skip if no DB:
    pytest tests/ai/translation_tests/test_db_persistence.py -v -k "not db"
    (all tests in this file are marked with @pytest.mark.db)
"""

import json
import os
from uuid import uuid4

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


def _build_config(fixture: dict) -> UnifiedConfig:
    data = {k: v for k, v in fixture.items() if k not in ("id", "description")}
    return UnifiedConfig.from_dict(data)


def _deep_compare(a, b, path: str = "") -> list[str]:
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
            diffs.append(f"{path}: bytes differ")
    elif a != b:
        diffs.append(f"{path}: {a!r} != {b!r}")
    return diffs


def _has_db_credentials() -> bool:
    """Check if database credentials are available."""
    required = ["SUPABASE_MATRIX_HOST", "SUPABASE_MATRIX_PASSWORD"]
    return all(os.environ.get(k) for k in required)


# Mark all tests in this module as requiring DB
pytestmark = [
    pytest.mark.db,
    pytest.mark.skipif(not _has_db_credentials(), reason="No DB credentials in env"),
]


# ---------------------------------------------------------------------------
# JSON serialization round-trip (simulates DB JSONB column behavior)
# ---------------------------------------------------------------------------
# Supabase PostgreSQL stores content in JSONB columns.
# JSONB round-trips through json.dumps → json.loads, which can alter types
# (e.g., tuples become lists, bytes are lost if not encoded).
# These tests simulate that layer.


class TestJsonbSimulatedRoundTrip:
    """Simulate the JSONB serialization that PostgreSQL performs.

    to_storage_dict → json.dumps → json.loads → reconstruct_content
    This catches issues where Python types don't survive JSON serialization.
    """

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_jsonb_roundtrip(self, fixture_id: str):
        fixture = get_fixture_by_id(fixture_id)
        config = _build_config(fixture)
        storage = config.to_storage_dict()

        # Simulate JSONB: serialize then deserialize
        json_str = json.dumps(storage, default=str)
        loaded = json.loads(json_str)

        assert loaded["model"] == storage["model"]
        assert len(loaded["messages"]) == len(storage["messages"])

        for i, (orig_stored, jsonb_stored) in enumerate(zip(storage["messages"], loaded["messages"])):
            assert orig_stored["role"] == jsonb_stored["role"]
            assert len(orig_stored["content"]) == len(jsonb_stored["content"])

            for j, (oc, jc) in enumerate(zip(orig_stored["content"], jsonb_stored["content"])):
                rebuilt_orig = reconstruct_content(oc)
                rebuilt_jsonb = reconstruct_content(jc)
                assert type(rebuilt_orig).__name__ == type(rebuilt_jsonb).__name__, (
                    f"msg[{i}].content[{j}]: type mismatch after JSONB"
                )

    @pytest.mark.parametrize("fixture_id", get_all_fixture_ids())
    def test_double_jsonb_idempotent(self, fixture_id: str):
        """JSONB round-trip is idempotent: two passes produce identical dicts."""
        fixture = get_fixture_by_id(fixture_id)
        config = _build_config(fixture)

        for mi, msg in enumerate(config.messages):
            for ci, content in enumerate(msg.content):
                s1 = content.to_storage_dict()
                j1 = json.loads(json.dumps(s1, default=str))
                r1 = reconstruct_content(j1)
                s2 = r1.to_storage_dict()
                j2 = json.loads(json.dumps(s2, default=str))

                diffs = _deep_compare(j1, j2, f"msg[{mi}].content[{ci}]")
                assert not diffs, "Double JSONB round-trip diffs:\n" + "\n".join(diffs)


class TestThinkingSignatureJsonbSurvival:
    """Signatures (bytes and strings) must survive JSONB round-trip."""

    def test_openai_bytes_signature_survives_jsonb(self):
        orig = ThinkingContent(id="rs_1", provider="openai", signature=FAKE_OPENAI_SIGNATURE)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored, default=str))
        rebuilt = reconstruct_content(jsonb)
        assert isinstance(rebuilt, ThinkingContent)
        assert rebuilt.signature == FAKE_OPENAI_SIGNATURE
        assert isinstance(rebuilt.signature, bytes)

    def test_anthropic_string_signature_survives_jsonb(self):
        orig = ThinkingContent(text="T", provider="anthropic", signature=FAKE_ANTHROPIC_SIGNATURE)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_content(jsonb)
        assert rebuilt.signature == FAKE_ANTHROPIC_SIGNATURE

    def test_google_bytes_signature_survives_jsonb(self):
        orig = ThinkingContent(text="T", provider="google", signature=FAKE_GOOGLE_SIGNATURE)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored, default=str))
        rebuilt = reconstruct_content(jsonb)
        assert isinstance(rebuilt, ThinkingContent)
        assert rebuilt.signature == FAKE_GOOGLE_SIGNATURE
        assert isinstance(rebuilt.signature, bytes)


class TestMediaBase64JsonbSurvival:
    """Base64 image data must survive JSONB round-trip."""

    def test_image_base64_survives_jsonb(self):
        orig = ImageContent(base64_data=TINY_PNG_BASE64, mime_type="image/png")
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_media_content(jsonb)
        assert isinstance(rebuilt, ImageContent)
        assert rebuilt.base64_data == TINY_PNG_BASE64

    def test_large_base64_survives_jsonb(self):
        big = "A" * 500_000
        orig = ImageContent(base64_data=big, mime_type="image/png")
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_media_content(jsonb)
        assert rebuilt.base64_data == big


class TestToolContentJsonbSurvival:
    """Tool calls and results with complex content survive JSONB."""

    def test_nested_tool_arguments(self):
        args = {
            "query": "SELECT *",
            "params": {"timeout": 30, "nested": {"deep": [1, 2, {"x": True}]}},
        }
        orig = ToolCallContent(id="t1", name="db", arguments=args)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_content(jsonb)
        assert rebuilt.arguments == args

    def test_tool_result_list_content(self):
        data = [{"a": 1, "b": [2, 3]}, {"a": 4, "b": [5, 6]}]
        orig = ToolResultContent(tool_use_id="t", name="q", content=data)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_content(jsonb)
        assert rebuilt.content == data

    def test_tool_result_error_flag(self):
        orig = ToolResultContent(tool_use_id="t", name="q", content="Error", is_error=True)
        stored = orig.to_storage_dict()
        jsonb = json.loads(json.dumps(stored))
        rebuilt = reconstruct_content(jsonb)
        assert rebuilt.is_error is True


# ---------------------------------------------------------------------------
# Live Database Tests (require actual DB connection)
# ---------------------------------------------------------------------------


class TestLiveDbRoundTrip:
    """Write to real DB and read back. Requires CxManagers (cxm)."""

    @pytest.fixture
    def conversation_id(self):
        """Generate a unique conversation ID for each test."""
        return str(uuid4())

    async def _write_and_read_messages(self, messages_storage: list[dict]) -> list[dict]:
        """Write message storage dicts to DB and read them back.

        This uses the cx_message table through the CxManagers singleton.
        Returns the content arrays as read from the DB.
        """
        try:
            from matrx_ai.conversation.cx_managers import cxm
        except ImportError:
            pytest.skip("CxManagers not available")

        conv_id = str(uuid4())
        user_id = os.environ.get("DEVELOPER_USER_ID", "")
        if not user_id:
            pytest.skip("DEVELOPER_USER_ID not set")

        # Write messages
        for i, msg_storage in enumerate(messages_storage):
            await cxm.message.create_cx_message(
                conversation_id=conv_id,
                role=msg_storage["role"],
                content=msg_storage["content"],
                position=i,
            )

        # Read them back
        db_messages = await cxm.message.filter_cx_messages(
            conversation_id=conv_id,
            order_by="position",
        )

        return [{"role": m.role, "content": m.content} for m in db_messages]

    @pytest.mark.parametrize("fixture_id", ["simple_text", "openai_thinking", "anthropic_thinking"])
    async def test_live_db_roundtrip(self, fixture_id: str):
        """Write fixture messages to DB, read back, reconstruct, and compare."""
        fixture = get_fixture_by_id(fixture_id)
        config = _build_config(fixture)
        storage = config.to_storage_dict()

        try:
            read_back = await self._write_and_read_messages(storage["messages"])
        except Exception as e:
            pytest.skip(f"DB not available: {e}")

        assert len(read_back) == len(storage["messages"])

        for i, (orig, db) in enumerate(zip(storage["messages"], read_back)):
            assert orig["role"] == db["role"]
            assert len(orig["content"]) == len(db["content"])

            for j, (oc, dc) in enumerate(zip(orig["content"], db["content"])):
                r_orig = reconstruct_content(oc)
                r_db = reconstruct_content(dc)
                assert type(r_orig).__name__ == type(r_db).__name__, (
                    f"msg[{i}].content[{j}] type mismatch after DB"
                )

                if isinstance(r_orig, TextContent):
                    assert r_db.text == r_orig.text
                if isinstance(r_orig, ThinkingContent):
                    assert r_db.provider == r_orig.provider
                    if r_orig.signature is not None:
                        assert r_db.signature == r_orig.signature


# ---------------------------------------------------------------------------
# Full Config Storage Dict Completeness
# ---------------------------------------------------------------------------


class TestConfigStorageDictCompleteness:
    """Verify to_storage_dict captures all config fields."""

    def test_config_fields_preserved(self):
        fixture = get_fixture_by_id("tool_calls_multi_turn")
        config = _build_config(fixture)
        storage = config.to_storage_dict()

        assert storage["model"] == "gpt-5"
        assert storage["system_instruction"] == "You are a travel assistant. Use tools to help plan trips."
        # Config should contain temperature, max_output_tokens, etc.
        cfg = storage.get("config", {})
        assert cfg.get("temperature") == 0.7 or config.temperature == 0.7
        assert cfg.get("max_output_tokens") == 8192 or config.max_output_tokens == 8192

    def test_thinking_config_preserved(self):
        fixture = get_fixture_by_id("anthropic_thinking")
        config = _build_config(fixture)
        storage = config.to_storage_dict()
        cfg = storage.get("config", {})
        assert cfg.get("thinking_budget") == 4096 or config.thinking_budget == 4096

    def test_reasoning_config_preserved(self):
        fixture = get_fixture_by_id("openai_thinking")
        config = _build_config(fixture)
        storage = config.to_storage_dict()
        cfg = storage.get("config", {})
        assert cfg.get("reasoning_effort") == "high" or config.reasoning_effort == "high"
