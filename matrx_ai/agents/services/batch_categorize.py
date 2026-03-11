"""Batch Prompt Categorization Management Script.

Runs the categorizer agent against many prompts at once with:
- A single cx_user_request row for the whole batch (one user action = one request)
- Resilient concurrency via ConcurrentEngine with adaptive throttling and retry
- Automatic retry with exponential backoff for rate-limited or transient failures
- Guaranteed result preservation — succeeded items are never lost
- Detailed progress reporting and cost summary

Usage:
    # Test with 3 prompts first (dry run)
    python -m ai.agents.services.batch_categorize --count 3 --dry-run

    # Confirm it works, then run 3 for real
    python -m ai.agents.services.batch_categorize --count 3

    # Fire off all uncategorized prompts with concurrency of 15
    python -m ai.agents.services.batch_categorize --concurrency 15

    # Re-categorize ALL prompts (even ones with existing categories)
    python -m ai.agents.services.batch_categorize --all --concurrency 15

    # Specific prompt IDs
    python -m ai.agents.services.batch_categorize --ids id1,id2,id3

    # Stagger launches by 0.5s between each task (for strict rate limits)
    python -m ai.agents.services.batch_categorize --delay 0.5
"""

from __future__ import annotations

import argparse
import asyncio
import time

from matrx_utils import cleanup_async_resources, clear_terminal, vcprint

from matrx_ai.orchestrator.concurrent_engine import (
    BatchResult,
    ConcurrentEngine,
    EngineConfig,
    ItemOutcome,
    WarmupStrategy,
)

# ---------------------------------------------------------------------------
# Progress callback for verbose CLI logging
# ---------------------------------------------------------------------------


async def _log_progress(completed: int, total: int, outcome: ItemOutcome) -> None:
    tag = f"[{completed}/{total}]"
    if outcome.success:
        result = outcome.result
        cat = getattr(result, "result", None)
        category = getattr(cat, "category", "?") if cat else "?"
        tags = getattr(cat, "tags", []) if cat else []
        vcprint(
            f"{tag} OK ({outcome.elapsed:.1f}s) — category={category}, tags={tags}",
            color="green",
        )
    else:
        vcprint(
            f"{tag} FAILED ({outcome.elapsed:.1f}s, {outcome.attempts} attempts) — {outcome.error}",
            color="red",
        )


# ---------------------------------------------------------------------------
# Batch runner
# ---------------------------------------------------------------------------


async def run_batch(
    prompt_ids: list[str],
    *,
    concurrency: int = 10,
    dry_run: bool = False,
    rate_limit_delay: float = 0.0,
    warmup: WarmupStrategy = WarmupStrategy.STAGED,
) -> BatchResult:
    from matrx_ai.agents.services.prompt_categorizer import categorize_prompt
    from matrx_ai.context.app_context import get_app_context
    from matrx_ai.db.custom import ensure_conversation_exists, ensure_user_request_exists

    ctx = get_app_context()

    await ensure_conversation_exists(
        conversation_id=ctx.conversation_id,
        user_id=ctx.user_id,
    )
    await ensure_user_request_exists(
        request_id=ctx.request_id,
        conversation_id=ctx.conversation_id,
        user_id=ctx.user_id,
    )

    async def _categorize_worker(pid: str):
        return await categorize_prompt(pid, dry_run=dry_run)

    engine = ConcurrentEngine(
        config=EngineConfig(
            initial_concurrency=concurrency,
            max_concurrency=concurrency * 2,
            warmup=warmup,
            max_retries=3,
            rate_limit_cooldown=rate_limit_delay if rate_limit_delay > 0 else 30.0,
        ),
        on_progress=_log_progress,
        is_result_success=lambda outcome: getattr(outcome, "success", True),
    )

    return await engine.run(prompt_ids, _categorize_worker)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Batch categorize prompts using the builtin categorizer agent.",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=None,
        help="Maximum number of prompts to process. Default: all uncategorized.",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Max concurrent agent executions. Default: 10.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without updating the database.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="include_all",
        help="Re-categorize all prompts, not just uncategorized ones.",
    )
    parser.add_argument(
        "--ids",
        type=str,
        default=None,
        help="Comma-separated list of specific prompt IDs to categorize.",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.0,
        help="Seconds between task launches for rate limiting. Default: 0.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug output (provider request details, etc.). Default: off.",
    )
    return parser.parse_args()


async def _main(args: argparse.Namespace) -> None:
    from matrx_ai.agents.services.prompt_categorizer import (
        get_all_prompt_ids,
        get_uncategorized_prompt_ids,
    )

    if args.ids:
        prompt_ids = [pid.strip() for pid in args.ids.split(",") if pid.strip()]
    elif args.include_all:
        prompt_ids = await get_all_prompt_ids(limit=args.count)
    else:
        prompt_ids = await get_uncategorized_prompt_ids(limit=args.count)

    if not prompt_ids:
        vcprint("No prompts to categorize.", color="yellow")
        return

    mode = "DRY RUN" if args.dry_run else "LIVE"
    vcprint(
        f"\n{'=' * 60}\n"
        f"Batch Categorization — {mode}\n"
        f"Prompts: {len(prompt_ids)} | Concurrency: {args.concurrency}\n"
        f"{'=' * 60}\n",
        color="blue",
    )

    start = time.perf_counter()
    result = await run_batch(
        prompt_ids,
        concurrency=args.concurrency,
        dry_run=args.dry_run,
        rate_limit_delay=args.delay,
    )
    elapsed = time.perf_counter() - start

    result.print_report(label=f"Batch Categorization — {elapsed:.1f}s total")

    if not args.dry_run:
        from matrx_ai.context.app_context import get_app_context
        from matrx_ai.db.custom import cxm

        try:
            conv_id = get_app_context().conversation_id
            summary = await cxm.get_conversation_cost_summary(conv_id)
            summary.print_summary(label="Batch Job Cost Summary")
        except Exception as exc:
            vcprint(f"Could not fetch cost summary: {exc}", color="yellow")


if __name__ == "__main__":
    clear_terminal()

    from aidream.api.middleware.test_context import create_test_app_context
    from initialize_systems import initialize

    initialize()
    args = _parse_args()
    _ctx_token = create_test_app_context(new_conversation=True, debug=args.debug)

    try:
        asyncio.run(_main(args))
    finally:
        from matrx_ai.context.app_context import clear_app_context
        clear_app_context(_ctx_token)
        cleanup_async_resources()
