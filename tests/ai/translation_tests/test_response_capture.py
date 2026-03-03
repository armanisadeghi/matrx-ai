"""
Tests for the response capture system itself.

Validates that:
  - Capture is disabled by default
  - Capture writes valid JSON files when enabled
  - Loading captured files works with filtering
  - Bytes and Pydantic objects are properly serialized
  - Captured files can be used as test fixtures

Run:
    pytest tests/ai/translation_tests/test_response_capture.py -v
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from .response_capture import (
    CAPTURE_DIR,
    _json_deserializer,
    _json_serializer,
    capture_provider_response,
    clear_captured_responses,
    is_capture_enabled,
    load_captured_as_fixture,
    load_captured_responses,
)


class TestCaptureEnableDisable:

    def test_disabled_by_default(self):
        with patch.dict(os.environ, {}, clear=True):
            assert is_capture_enabled() is False

    def test_enabled_with_1(self):
        with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "1"}):
            assert is_capture_enabled() is True

    def test_enabled_with_true(self):
        with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "true"}):
            assert is_capture_enabled() is True

    def test_disabled_returns_none(self):
        with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "0"}):
            result = capture_provider_response("openai", "gpt-5", {"test": True})
            assert result is None


class TestJsonSerializer:

    def test_bytes_serialization(self):
        data = b"hello bytes"
        serialized = _json_serializer(data)
        assert serialized["__bytes__"] is True
        assert isinstance(serialized["data"], str)

    def test_bytes_deserialization(self):
        serialized = {"__bytes__": True, "data": "aGVsbG8gYnl0ZXM="}
        result = _json_deserializer(serialized)
        assert result == b"hello bytes"

    def test_regular_dict_passthrough(self):
        d = {"key": "value"}
        assert _json_deserializer(d) == d


class TestCaptureAndLoad:

    def test_capture_write_and_load(self, tmp_path):
        """Test full capture → load cycle."""
        import tests.ai.translation_tests.response_capture as mod

        original_dir = mod.CAPTURE_DIR
        mod.CAPTURE_DIR = tmp_path
        try:
            with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "1"}):
                response = {
                    "id": "resp_123",
                    "model": "gpt-5",
                    "output": [{"type": "message", "content": [{"type": "text", "text": "Hello"}]}],
                    "usage": {"input_tokens": 10, "output_tokens": 20},
                }
                filepath = capture_provider_response(
                    "openai", "gpt-5", response,
                    conversation_context={"turn": 1, "has_tools": False},
                    label="test_capture",
                )
                assert filepath is not None
                assert filepath.exists()

                # Verify JSON is valid
                with open(filepath) as f:
                    data = json.load(f)
                assert data["capture_metadata"]["provider"] == "openai"
                assert data["capture_metadata"]["model"] == "gpt-5"
                assert data["response"]["id"] == "resp_123"

                # Load back
                loaded = load_captured_responses(provider="openai")
                assert len(loaded) >= 1
                assert loaded[0]["capture_metadata"]["provider"] == "openai"
        finally:
            mod.CAPTURE_DIR = original_dir

    def test_capture_with_bytes(self, tmp_path):
        """Test that bytes in responses are properly serialized."""
        import tests.ai.translation_tests.response_capture as mod

        original_dir = mod.CAPTURE_DIR
        mod.CAPTURE_DIR = tmp_path
        try:
            with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "1"}):
                response = {
                    "thinking": {"encrypted_content": b"secret_bytes_data"},
                    "text": "Hello",
                }
                filepath = capture_provider_response("openai", "gpt-5", response)
                assert filepath is not None

                # Should be valid JSON (bytes encoded)
                with open(filepath) as f:
                    data = json.load(f)
                enc = data["response"]["thinking"]["encrypted_content"]
                assert enc["__bytes__"] is True
        finally:
            mod.CAPTURE_DIR = original_dir

    def test_load_as_fixture(self, tmp_path):
        """Test load_captured_as_fixture."""
        import tests.ai.translation_tests.response_capture as mod

        original_dir = mod.CAPTURE_DIR
        mod.CAPTURE_DIR = tmp_path
        try:
            with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "1"}):
                response = {"content": "test"}
                filepath = capture_provider_response("anthropic", "claude-sonnet-4-6", response)

                fixture = load_captured_as_fixture(filepath)
                assert fixture["provider"] == "anthropic"
                assert fixture["model"] == "claude-sonnet-4-6"
                assert fixture["response"]["content"] == "test"
        finally:
            mod.CAPTURE_DIR = original_dir

    def test_filter_by_provider(self, tmp_path):
        """Test filtering by provider."""
        import tests.ai.translation_tests.response_capture as mod

        original_dir = mod.CAPTURE_DIR
        mod.CAPTURE_DIR = tmp_path
        try:
            with patch.dict(os.environ, {"MATRX_CAPTURE_LLM_RESPONSES": "1"}):
                capture_provider_response("openai", "gpt-5", {"a": 1})
                capture_provider_response("anthropic", "claude", {"b": 2})
                capture_provider_response("google", "gemini", {"c": 3})

                openai_only = load_captured_responses(provider="openai")
                assert len(openai_only) == 1
                assert openai_only[0]["capture_metadata"]["provider"] == "openai"

                all_responses = load_captured_responses()
                assert len(all_responses) == 3
        finally:
            mod.CAPTURE_DIR = original_dir
