from __future__ import annotations

import asyncio
import logging
import time
import traceback
from typing import Any

from tools.arg_models.web_args import (
    RESEARCH_DEPTH_CONFIG,
    WebReadArgs,
    WebResearchArgs,
    WebSearchArgs,
)
from tools.models import ToolContext, ToolError, ToolResult
from tools.streaming import ToolStreamManager

logger = logging.getLogger(__name__)


async def web_search(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Web search using the existing scraper infrastructure.

    This replaces the old web_search_summarized / web_search_quick wrappers.
    The function calls directly into the scraper's search helpers.
    """
    started_at = time.time()
    parsed = WebSearchArgs(**args)
    stream = ToolStreamManager(ctx.emitter, ctx.call_id, "web_search")

    try:
        from scraper.scraper_enhanced.features.quick_search import (
            search_web_mcp_quick,
        )

        all_text_results: list[str] = []
        for query in parsed.queries:
            await stream.progress(f"Searching: {query}")
            results = await search_web_mcp_quick(
                queries=[query],
                freshness=parsed.freshness,
                emitter=ctx.emitter,
                call_id=ctx.call_id,
            )
            if isinstance(results, dict) and results.get("status") == "success":
                text_content = results.get("result", "")
                if text_content:
                    all_text_results.append(text_content)

        combined_text = "\n\n".join(all_text_results)

        if not combined_text.strip():
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="execution",
                    message="No search results found for the given queries.",
                    is_retryable=True,
                    suggested_action="Try different or broader search queries.",
                ),
                started_at=started_at,
                completed_at=time.time(),
                tool_name="web_search",
                call_id=ctx.call_id,
            )

        if parsed.summarize and parsed.instructions:
            await stream.step("summarize", "Summarizing search results...")
            from tools.implementations._summarize_helper import (
                summarize_content,
            )

            summary, child_usages = await summarize_content(
                content=combined_text,
                instructions=parsed.instructions,
                ctx=ctx,
            )
            return ToolResult(
                success=True,
                output=summary,
                child_usages=child_usages,
                started_at=started_at,
                completed_at=time.time(),
                tool_name="web_search",
                call_id=ctx.call_id,
            )

        return ToolResult(
            success=True,
            output=combined_text,
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_search",
            call_id=ctx.call_id,
        )

    except ImportError as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="import",
                message=f"Scraper module not available: {exc}",
                suggested_action="Ensure the scraper package is installed.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_search",
            call_id=ctx.call_id,
        )

    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution",
                message=f"Web search failed: {exc}",
                is_retryable=True,
                suggested_action="Try with different queries or fewer queries.",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_search",
            call_id=ctx.call_id,
        )


async def web_read(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    """Read/scrape web pages. Replaces web_read_quick / web_read_summarized wrappers."""
    started_at = time.time()
    parsed = WebReadArgs(**args)
    stream = ToolStreamManager(ctx.emitter, ctx.call_id, "web_read")

    try:
        from scraper.scraper_enhanced.features.read_page import (
            read_page_mcp_quick,
        )

        pages: list[dict[str, Any]] = []
        for url in parsed.urls:
            await stream.progress(f"Reading: {url[:60]}...")
            result = await read_page_mcp_quick(url=url)
            if isinstance(result, dict):
                content = result.get("content", result.get("result", ""))
                if (
                    isinstance(content, str)
                    and len(content) > parsed.max_content_length
                ):
                    content = content[: parsed.max_content_length] + "\n...[truncated]"
                pages.append({"url": url, "content": content})
            else:
                pages.append(
                    {"url": url, "content": str(result)[: parsed.max_content_length]}
                )

        if parsed.summarize and parsed.instructions:
            await stream.step("summarize", "Summarizing page content...")
            from tools.implementations._summarize_helper import (
                summarize_content,
            )

            combined = "\n\n---\n\n".join(
                f"URL: {p['url']}\n{p['content']}" for p in pages
            )
            summary, child_usages = await summarize_content(
                content=combined,
                instructions=parsed.instructions,
                ctx=ctx,
            )
            return ToolResult(
                success=True,
                output=summary,
                child_usages=child_usages,
                started_at=started_at,
                completed_at=time.time(),
                tool_name="web_read",
                call_id=ctx.call_id,
            )

        return ToolResult(
            success=True,
            output={"pages": pages},
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_read",
            call_id=ctx.call_id,
        )

    except ImportError as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="import",
                message=f"Scraper module not available: {exc}",
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_read",
            call_id=ctx.call_id,
        )
    except Exception as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution",
                message=f"Web read failed: {exc}",
                is_retryable=True,
            ),
            started_at=started_at,
            completed_at=time.time(),
            tool_name="web_read",
            call_id=ctx.call_id,
        )


async def web_research(args: dict[str, Any], ctx: ToolContext) -> ToolResult:
    started_at = time.time()
    parsed = WebResearchArgs(**args)
    stream = ToolStreamManager(ctx.emitter, ctx.call_id, "web_research")

    depth_cfg = RESEARCH_DEPTH_CONFIG[parsed.research_depth]
    urls_per_query = depth_cfg["urls_per_query"]
    good_scrape_threshold = depth_cfg["good_scrape_threshold"]
    target_good_per_query = depth_cfg["target_good_per_query"]

    timing: dict[str, Any] = {}

    try:
        from api_management.brave_search.search_async import (
            async_brave_search,
            generate_search_text_summary,
        )
        from scraper.scraper_enhanced.features.mcp_tool_helpers import (
            scrape_urls_from_search_result,
        )
        from scraper.scraper_enhanced.features.utils import (
            format_scraped_pages_section,
        )

        # ------------------------------------------------------------------
        # Phase 1: Concurrent search — fire all queries at once
        # ------------------------------------------------------------------
        search_start = time.perf_counter()

        async def _search_with_query(query: str) -> tuple[str, dict[str, Any] | None]:
            result = await async_brave_search(
                query=query,
                freshness=parsed.freshness,
                country=parsed.country,
                extra_snippets=True,
            )
            return (query, result)

        search_tasks = [_search_with_query(q) for q in parsed.queries]

        queries_with_results: list[tuple[str, dict[str, Any] | None]] = []
        seen_urls: set[str] = set()
        scraping_tasks: list[asyncio.Task[list[dict[str, Any]]]] = []
        scraping_start_time: float | None = None

        for search_coro in asyncio.as_completed(search_tasks):
            query, search_result = await search_coro

            if not search_result:
                continue

            queries_with_results.append((query, search_result))

            await stream.progress(f"Searched: {query}")

            if scraping_start_time is None:
                scraping_start_time = time.perf_counter()

            scraping_task = asyncio.create_task(
                scrape_urls_from_search_result(
                    search_result=search_result,
                    seen_urls=seen_urls,
                    urls_per_query=urls_per_query,
                    good_scrape_threshold=good_scrape_threshold,
                    emitter=ctx.emitter,
                    call_id=ctx.call_id,
                )
            )
            scraping_tasks.append(scraping_task)

        if not queries_with_results:
            return ToolResult(
                success=False,
                error=ToolError(
                    error_type="execution",
                    message="All search queries failed to return results.",
                    is_retryable=True,
                    suggested_action="Try different search queries or check network connectivity.",
                ),
                started_at=started_at,
                completed_at=time.time(),
            )

        # ------------------------------------------------------------------
        # Phase 2: Wait for all scraping to complete
        # ------------------------------------------------------------------
        all_scraped_results = await asyncio.gather(*scraping_tasks)
        all_scraped_pages = [page for result in all_scraped_results for page in result]

        search_and_scrape_end = time.perf_counter()
        timing["total_search_time"] = round(search_and_scrape_end - search_start, 2)
        timing["total_scraping_time"] = (
            round(search_and_scrape_end - scraping_start_time, 2)
            if scraping_start_time
            else 0
        )

        good_scrapes = [s for s in all_scraped_pages if s.get("is_good_scrape", False)]
        thin_scrapes = [s for s in all_scraped_pages if not s.get("is_good_scrape", False)]
        limited_good_scrapes = good_scrapes[: target_good_per_query * len(parsed.queries)]

        total_attempted = len(seen_urls)
        failed_count = total_attempted - len(all_scraped_pages)

        await stream.step(
            "scraping_complete",
            f"Scraped {len(all_scraped_pages)} pages ({len(good_scrapes)} good, {len(thin_scrapes)} thin, {failed_count} failed)",
        )

        # ------------------------------------------------------------------
        # Phase 3: Format context for the condensation agent
        # ------------------------------------------------------------------
        scraped_pages_content = format_scraped_pages_section(
            limited_good_scrapes=limited_good_scrapes, thin_scrapes=thin_scrapes,
        )

        search_previews_raw = generate_search_text_summary(queries_with_results)
        search_previews_content = (
            f"=== SEARCH RESULT PREVIEWS (Not Fully Scraped) ===\n\n{search_previews_raw}"
        )

        full_context_for_agent = scraped_pages_content + "\n" + search_previews_content

        # ------------------------------------------------------------------
        # Phase 4: Run the research condensation agent
        # ------------------------------------------------------------------
        research_report = ""
        agent_child_usages: list = []

        if full_context_for_agent.strip():
            await stream.step("condensing", "Conducting in-depth research analysis on scraped content")

            from client.system_agents import scrape_research_condenser_agent_1

            queries_str = ", ".join(parsed.queries)

            agent_result = await scrape_research_condenser_agent_1(
                instructions=parsed.instructions,
                scraped_content=full_context_for_agent,
                queries=queries_str,
                search_results=search_previews_raw,
                ctx=ctx,
            )

            if agent_result.success and agent_result.output:
                research_report = (
                    f"\n# Curated Research Results\n\n"
                    f"The following is the result of successfully scraping {len(good_scrapes)} pages "
                    f"and an agent conducting a full review of the top results:\n\n"
                    f"{agent_result.output}\n---\n"
                )
                agent_child_usages = agent_result.usage_history
            else:
                research_report = (
                    "\n# Research Condensation\n\n"
                    "The research agent was unable to produce a condensed report. "
                    "Raw search results and scraped content are provided below.\n---\n"
                )

        # ------------------------------------------------------------------
        # Phase 5: Assemble final output
        # ------------------------------------------------------------------
        all_search_results_text = f"\n# All Search Results:\n\n{search_previews_raw}\n---\n"

        next_steps = (
            "\n## Next steps:\n\n"
            "Assess if this context answers the user's query. If gaps remain or more detail is needed, take action:\n"
            "- Use `web_read` to get complete content from any of the URLs shown in the search results above\n"
            "- Use `web_read` on any specific URLs the user mentioned that seem relevant\n"
            "- Use `web_search` with different or more specific terms if these results miss the mark\n"
            "- Do a new research, just like this one, but with new queries and more specific instructions.\n\n"
            "If the context above sufficiently answers the query, respond directly to the user."
        )

        final_text = (
            f"Comprehensive research using the following queries: {', '.join(parsed.queries)}.\n"
            + all_search_results_text
            + research_report
            + next_steps
        )

        end_time = time.perf_counter()
        timing["condensation_time"] = round(end_time - search_and_scrape_end, 2)
        timing["total_execution_time"] = round(end_time - (started_at if isinstance(started_at, float) else search_start), 2)
        timing["queries_count"] = len(parsed.queries)
        timing["urls_attempted"] = total_attempted
        timing["urls_scraped"] = len(all_scraped_pages)
        timing["good_scrapes"] = len(good_scrapes)
        timing["thin_scrapes"] = len(thin_scrapes)
        timing["failed_scrapes"] = failed_count
        timing["research_depth"] = parsed.research_depth

        return ToolResult(
            success=True,
            output=final_text,
            child_usages=agent_child_usages,
            started_at=started_at,
            completed_at=time.time(),
        )

    except ImportError as exc:
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="import",
                message=f"Required module not available: {exc}",
                traceback=traceback.format_exc(),
                suggested_action="Ensure scraper and API management packages are installed.",
            ),
            started_at=started_at,
            completed_at=time.time(),
        )

    except Exception as exc:
        logger.exception("web_research failed")
        return ToolResult(
            success=False,
            error=ToolError(
                error_type="execution",
                message=f"Web research failed: {exc}",
                traceback=traceback.format_exc(),
                is_retryable=True,
                suggested_action="Try with different queries or reduce research_depth.",
            ),
            started_at=started_at,
            completed_at=time.time(),
        )
