"""Robust JSON extraction from LLM responses.

LLMs often wrap JSON in markdown fences, include thinking tokens, or produce
minor formatting issues. This module provides a generous parser that handles
all of those cases and returns validated Pydantic models.

Usage:
    from matrx_ai.agents.response_parser import extract_json, extract_model

    raw = agent_result.output
    data = extract_json(raw)                              # -> dict | list | None
    model = extract_model(raw, MyCategorization)          # -> MyCategorization | None
"""

from __future__ import annotations

import json
import re
from typing import TypeVar

from matrx_utils import vcprint
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


# ---------------------------------------------------------------------------
# Core JSON extraction — handles fences, thinking tokens, trailing commas
# ---------------------------------------------------------------------------

_THINKING_RE = re.compile(
    r"<think(?:ing)?>\s*.*?\s*</think(?:ing)?>",
    re.DOTALL | re.IGNORECASE,
)

_FENCE_RE = re.compile(
    r"```(?:json)?\s*\n?(.*?)\n?\s*```",
    re.DOTALL,
)

_TRAILING_COMMA_RE = re.compile(r",\s*([}\]])")


def _strip_thinking(text: str) -> str:
    return _THINKING_RE.sub("", text).strip()


def _try_parse(candidate: str) -> dict | list | None:
    candidate = candidate.strip()
    if not candidate:
        return None

    candidate = _TRAILING_COMMA_RE.sub(r"\1", candidate)

    try:
        result = json.loads(candidate)
        if isinstance(result, (dict, list)):
            return result
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def extract_json(text: str) -> dict | list | None:
    """Extract the first valid JSON object or array from LLM output.

    Handles:
    - Raw JSON (no wrapping)
    - Markdown code fences (```json ... ```)
    - Thinking tokens (<thinking>...</thinking>)
    - Trailing commas
    - Leading/trailing whitespace and prose
    """
    if not text or not text.strip():
        return None

    cleaned = _strip_thinking(text)

    for match in _FENCE_RE.finditer(cleaned):
        result = _try_parse(match.group(1))
        if result is not None:
            return result

    result = _try_parse(cleaned)
    if result is not None:
        return result

    # Last resort: find the first { ... } or [ ... ] span via brace matching
    for open_char, close_char in [("{", "}"), ("[", "]")]:
        start = cleaned.find(open_char)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape_next = False
        for i in range(start, len(cleaned)):
            ch = cleaned[i]
            if escape_next:
                escape_next = False
                continue
            if ch == "\\":
                escape_next = True
                continue
            if ch == '"' and not escape_next:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == open_char:
                depth += 1
            elif ch == close_char:
                depth -= 1
                if depth == 0:
                    result = _try_parse(cleaned[start : i + 1])
                    if result is not None:
                        return result
                    break

    vcprint("[ResponseParser] No valid JSON found in response", color="yellow")
    return None


# ---------------------------------------------------------------------------
# Model extraction — parse + validate against a Pydantic model
# ---------------------------------------------------------------------------


def extract_model[T: BaseModel](text: str, model_class: type[T]) -> T | None:
    """Extract JSON from LLM output and validate it against a Pydantic model.

    Returns None if extraction or validation fails.
    """
    data = extract_json(text)
    if data is None:
        return None
    if not isinstance(data, dict):
        vcprint(
            f"[ResponseParser] Expected dict for {model_class.__name__}, got {type(data).__name__}",
            color="yellow",
        )
        return None
    try:
        return model_class.model_validate(data)
    except ValidationError as exc:
        vcprint(
            f"[ResponseParser] Validation failed for {model_class.__name__}: {exc}",
            color="yellow",
        )
        return None
