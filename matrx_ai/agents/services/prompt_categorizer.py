"""Prompt Categorization Service.

Uses the "prompt_builtin" categorizer agent to analyze a prompt entry and
return structured metadata (category, tags, description). Handles the full
lifecycle: fetch prompt -> run agent -> parse response -> update database.

The categorizer builtin agent ID is a constant here so it's easy to change
if the prompt is ever re-created.

Usage (from an API route or management script):
    from matrx_ai.agents.services.prompt_categorizer import categorize_prompt

    result = await categorize_prompt("some-prompt-uuid")

Supported tables: Prompts, PromptBuiltins.
"""

from __future__ import annotations

import json
from typing import Any

from matrx_utils import vcprint
from pydantic import BaseModel, Field

from matrx_ai.agents.definition import Agent
from matrx_ai.agents.manager import pm
from matrx_ai.agents.response_parser import extract_model

CATEGORIZER_BUILTIN_ID = "e58dc3fc-7cf0-42e4-a557-f326c517a78b"


# ---------------------------------------------------------------------------
# Response model — what the categorizer agent returns
# ---------------------------------------------------------------------------


class CategorizationResult(BaseModel):
    id: str
    category: str | None = None
    tags: list[str] = Field(default_factory=list)
    description: str | None = None


# ---------------------------------------------------------------------------
# Public result type
# ---------------------------------------------------------------------------


class CategorizationOutcome(BaseModel):
    prompt_id: str
    success: bool
    result: CategorizationResult | None = None
    error: str | None = None
    raw_output: str | None = None


# ---------------------------------------------------------------------------
# Core service function
# ---------------------------------------------------------------------------


async def categorize_prompt(
    prompt_id: str,
    *,
    dry_run: bool = False,
) -> CategorizationOutcome:
    """Categorize a single prompt entry.

    1. Loads the prompt from the database (tries Prompts first, then PromptBuiltins).
    2. Feeds the full prompt JSON to the categorizer builtin agent.
    3. Parses the structured JSON response.
    4. Updates the database entry with category, tags, and description.

    Args:
        prompt_id: UUID of the prompt to categorize.
        dry_run: If True, skip the database update and just return the result.

    Returns:
        CategorizationOutcome with success/failure status and parsed result.
    """
    try:
        data = await _fetch_prompt_data(prompt_id)
    except Exception as exc:
        vcprint(str(exc), f"[PromptCategorizer] Failed to fetch prompt id: {prompt_id}", color="red")
        return CategorizationOutcome(
            prompt_id=prompt_id,
            success=False,
            error=f"Failed to fetch prompt: {exc}",
        )

    prompt_json = json.dumps(data, indent=2, default=str, ensure_ascii=False)

    try:
        agent = await Agent.from_builtin(CATEGORIZER_BUILTIN_ID)
        agent.set_variable("prompt_data", prompt_json)
        result = await agent.execute()
        raw_output = result.output
    except Exception as exc:
        vcprint(prompt_json, "[PromptCategorizer] Error executing agent. Prompt JSON", color="red")
        return CategorizationOutcome(
            prompt_id=prompt_id,
            success=False,
            error=f"Agent execution failed: {exc}",
        )

    parsed = extract_model(raw_output, CategorizationResult)
    if parsed is None:
        vcprint(raw_output, "[PromptCategorizer] Failed to parse categorization response. Raw Output", color="red")
        return CategorizationOutcome(
            prompt_id=prompt_id,
            success=False,
            error="Failed to parse categorization response",
            raw_output=raw_output,
        )

    if not dry_run:
        try:
            await _apply_categorization(prompt_id, parsed, data)
        except Exception as exc:
            return CategorizationOutcome(
                prompt_id=prompt_id,
                success=False,
                result=parsed,
                error=f"Database update failed: {exc}",
                raw_output=raw_output,
            )

    vcprint(
        f"[PromptCategorizer] {'(dry run) ' if dry_run else ''}Categorized {prompt_id}: "
        f"category={parsed.category}, tags={parsed.tags}",
        color="green",
    )
    return CategorizationOutcome(
        prompt_id=prompt_id,
        success=True,
        result=parsed,
        raw_output=raw_output,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


async def _fetch_prompt_data(prompt_id: str) -> dict[str, Any]:
    """Load a prompt by ID and return its dict representation.

    Tries Prompts first, then PromptBuiltins.
    """
    item = await pm.load_by_id(prompt_id)
    if item:
        return item.to_dict()

    raise ValueError(f"Prompt not found in any table: {prompt_id}")


async def _apply_categorization(
    prompt_id: str,
    result: CategorizationResult,
    existing_data: dict[str, Any],
) -> None:
    """Apply categorization results to the database.

    - category: always replaced
    - tags: merged with existing (new tags added, no duplicates)
    - description: replaced only if the new value is not None
    """
    updates: dict[str, Any] = {}

    # vcprint(result, "[PromptCategorizer] Result", color="blue")
    # vcprint(existing_data, "[PromptCategorizer] Existing Data", color="green")

    if result.category is not None:
        updates["category"] = result.category

    if result.tags:
        existing_tags = existing_data.get("tags") or []
        if isinstance(existing_tags, list):
            merged = list(dict.fromkeys(existing_tags + result.tags))
        else:
            merged = list(result.tags)
        updates["tags"] = merged

    if result.description is not None:
        updates["description"] = result.description

    if not updates:
        vcprint(f"[PromptCategorizer] No updates to apply for {prompt_id}", color="yellow")
        return

    try:
        await pm.update_by_id(prompt_id, **updates)
    except Exception as exc:
        vcprint(
            f"[PromptCategorizer] DB update failed for {prompt_id}: {exc}",
            color="red",
        )
        raise


# ---------------------------------------------------------------------------
# Batch helpers — used by the management script
# ---------------------------------------------------------------------------


async def get_uncategorized_prompt_ids(limit: int | None = None) -> list[str]:
    """Return IDs of PromptBuiltins that lack a category, then uncategorized Prompts.

    PromptBuiltins are checked first since they have the richest metadata
    schema (category, tags, description).
    """
    uncategorized: list[str] = []

    builtins = await pm.find_builtins()
    uncategorized.extend(
        str(item.id)
        for item in builtins
        if not getattr(item, "category", None)
    )

    prompts = await pm.find_prompts()
    uncategorized.extend(
        str(item.id)
        for item in prompts
        if not getattr(item, "category", None)
    )

    if limit is not None:
        uncategorized = uncategorized[:limit]
    return uncategorized


async def get_all_prompt_ids(limit: int | None = None) -> list[str]:
    """Return all Prompt and PromptBuiltin IDs (for full re-categorization)."""
    builtins = await pm.find_builtins()
    prompts = await pm.find_prompts()

    ids = [str(item.id) for item in builtins] + [str(item.id) for item in prompts]
    if limit is not None:
        ids = ids[:limit]
    return ids
