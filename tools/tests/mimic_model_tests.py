"""Mimic exactly what a model sees when a tool is called.

Usage:
    Update the test name at the bottom in `if __name__` and run this file.

Provides `run_tool()` which takes a tool name and args dict (exactly as a model
would produce them) and returns the exact dict the model receives back — the
output of `ToolResult.to_tool_result_content()`.

To add a new tool test, write a function that calls `run_tool()` with the
args the model would send.
"""
from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from matrx_utils import vcprint
import rich

from initialize_systems import initialize
from matrx_utils import clear_terminal, cleanup_async_resources
from tests.ai.test_context import create_test_tool_context, create_test_execution_context

from tools.models import ToolContext, ToolResult
from client.usage import MODEL_PRICING, TokenUsage

initialize()
_ctx_token = create_test_execution_context()



COST_COMPARISON_MODELS = [
    ("Small", "gemini-3-flash-preview", "google"),
    ("Medium", "gpt-5.2", "openai"),
    ("Large", "claude-opus-4", "anthropic"),
]

CHARS_PER_TOKEN = 4


def _estimate_cost_table(content: str) -> None:
    char_count = len(content)
    estimated_tokens = max(1, char_count // CHARS_PER_TOKEN)

    print()
    print("=" * 80)
    print("INPUT TOKEN COST ESTIMATE (tool result as input to next model turn)")
    print("=" * 80)
    print(f"  Content length:    {char_count:>10,} chars")
    print(f"  Estimated tokens:  {estimated_tokens:>10,} tokens  (~{CHARS_PER_TOKEN} chars/token)")
    print()
    print(f"  {'Model':<14} {'Tier':<8} {'$/M Input':>12} {'Est. Cost':>12}")
    print(f"  {'─' * 14} {'─' * 8} {'─' * 12} {'─' * 12}")

    for label, model_name, api in COST_COMPARISON_MODELS:
        pricing = MODEL_PRICING.get(model_name)
        if not pricing:
            print(f"  {label:<14} {'—':<8} {'N/A':>12} {'N/A':>12}")
            continue

        usage = TokenUsage(
            input_tokens=estimated_tokens,
            output_tokens=0,
            cached_input_tokens=0,
            model=model_name,
            api=api,
        )
        cost = usage.calculate_cost()
        tier = pricing.get_tier(estimated_tokens)
        price_per_m = tier.input_price if tier else 0

        cost_str = f"${cost:.6f}" if cost is not None else "N/A"
        print(f"  {label:<14} {price_per_m:>7.2f} {'$/M':>5} {cost_str:>12}")

    print("=" * 80)


def _build_ctx(tool_name: str, stream: bool = True) -> ToolContext:
    return create_test_tool_context(tool_name)


def _get_tool_map() -> dict[str, Any]:
    from tools.implementations import (
        # Math
        calculate,
        # Text
        text_analyze, regex_extract,
        # Web
        web_search, web_read, web_research,
        # Database
        db_query, db_insert, db_update, db_schema,
        # Memory
        memory_store, memory_recall, memory_search, memory_update, memory_forget,
        # Filesystem
        fs_read, fs_write, fs_list, fs_search, fs_mkdir,
        # Shell
        shell_execute, shell_python,
        # Browser
        browser_navigate, browser_click, browser_type_text, browser_screenshot,
        # User Lists
        create_user_list, create_simple_list, get_user_lists,
        get_list_details, update_list_item, batch_update_list_items,
        # SEO
        check_meta_titles, check_meta_descriptions, check_meta_tags_batch,
        get_keyword_search_data,
        # Code
        store_html, fetch_code,
        # News
        get_news_headlines,
        # User Tables
        create_user_generated_table,
        # Questionnaire
        ask_user_questions,
        # Travel
        get_location, get_weather, get_restaurants,
        get_activities, get_events, create_travel_summary,
    )

    return {
        "calculate": calculate,
        "text_analyze": text_analyze,
        "regex_extract": regex_extract,
        "web_search": web_search,
        "web_read": web_read,
        "web_research": web_research,
        "db_query": db_query,
        "db_insert": db_insert,
        "db_update": db_update,
        "db_schema": db_schema,
        "memory_store": memory_store,
        "memory_recall": memory_recall,
        "memory_search": memory_search,
        "memory_update": memory_update,
        "memory_forget": memory_forget,
        "fs_read": fs_read,
        "fs_write": fs_write,
        "fs_list": fs_list,
        "fs_search": fs_search,
        "fs_mkdir": fs_mkdir,
        "shell_execute": shell_execute,
        "shell_python": shell_python,
        "browser_navigate": browser_navigate,
        "browser_click": browser_click,
        "browser_type_text": browser_type_text,
        "browser_screenshot": browser_screenshot,
        "create_user_list": create_user_list,
        "create_simple_list": create_simple_list,
        "get_user_lists": get_user_lists,
        "get_list_details": get_list_details,
        "update_list_item": update_list_item,
        "batch_update_list_items": batch_update_list_items,
        "check_meta_titles": check_meta_titles,
        "check_meta_descriptions": check_meta_descriptions,
        "check_meta_tags_batch": check_meta_tags_batch,
        "get_keyword_search_data": get_keyword_search_data,
        "store_html": store_html,
        "fetch_code": fetch_code,
        "get_news_headlines": get_news_headlines,
        "create_user_generated_table": create_user_generated_table,
        "ask_user_questions": ask_user_questions,
        "get_location": get_location,
        "get_weather": get_weather,
        "get_restaurants": get_restaurants,
        "get_activities": get_activities,
        "get_events": get_events,
        "create_travel_summary": create_travel_summary,
    }


DB_TOOLS = {"db_query", "db_insert", "db_update", "db_schema", "memory_store",
             "memory_recall", "memory_search", "memory_update", "memory_forget",
             "create_user_list", "create_simple_list", "get_user_lists",
             "get_list_details", "update_list_item", "batch_update_list_items",
             "create_user_generated_table", "ask_user_questions",
             "store_html"}


async def run_tool(
    tool_name: str,
    args: dict[str, Any],
    *,
    stream: bool = True,
    print_result: bool = True,
    use_db: bool | None = None,
) -> dict[str, Any]:
    """Execute a tool exactly as the executor would and return the model-facing result."""

    tool_map = _get_tool_map()
    func = tool_map.get(tool_name)
    if func is None:
        raise ValueError(
            f"Tool '{tool_name}' not in TOOL_MAP. "
            f"Available: {sorted(tool_map.keys())}"
        )

    ctx = _build_ctx(tool_name, stream=stream)

    print("=" * 80)
    print(f"TOOL: {tool_name}")
    print("ARGS (what the model sends):")
    rich.print(args)
    print("=" * 80)

    start = time.perf_counter()
    result: ToolResult = await func(args, ctx)
    elapsed = time.perf_counter() - start

    model_facing = result.to_tool_result_content()

    if print_result:
        print()
        print("=" * 80)
        print("MODEL RECEIVES (to_tool_result_content):")
        print("=" * 80)
        rich.print(model_facing)
        print()

        print("-" * 80)
        print("CONTENT (the actual string the model reads):")
        print("-" * 80)
        content = model_facing.get("content", "")
        if isinstance(content, str):
            try:
                parsed = json.loads(content)
                rich.print(parsed)
            except (json.JSONDecodeError, TypeError):
                print(content[:3000])
                if len(content) > 3000:
                    print(f"\n... [{len(content):,} chars total, truncated for display]")
        else:
            rich.print(content)

        print()
        print("-" * 80)
        
        if result.success:
            vcprint(f"SUCCESS: {result.success}", color="green")
        else:
            vcprint(f"SUCCESS: {result.success}", color="red")
        
        
        
        is_error = model_facing.get('is_error', False)
        if is_error:
            vcprint(f"IS_ERROR: {is_error}", color="red")
        else:
            vcprint(f"IS_ERROR: {is_error}", color="green")
        print(f"DURATION: {elapsed:.2f}s (result.duration_ms={result.duration_ms}ms)")
        if result.usage:
            print(f"USAGE: {result.usage}")
        if result.child_usages:
            print(f"CHILD USAGES: {result.child_usages}")
        print("-" * 80)

        content_for_cost = model_facing.get("content", "")
        if isinstance(content_for_cost, str) and content_for_cost:
            _estimate_cost_table(content_for_cost)

    return model_facing


# ============================================================================
# MATH
# ============================================================================

async def test_calculate():
    return await run_tool("calculate", {
        "expression": "(12 * 8) + (45 / 3) - 7",
    })


# ============================================================================
# TEXT
# ============================================================================

async def test_text_analyze():
    return await run_tool("text_analyze", {
        "text": "The quick brown fox jumps over the lazy dog. This is a sample text for analysis. It contains multiple sentences and various words.",
        "analysis_type": "summary",
    })


async def test_regex_extract():
    return await run_tool("regex_extract", {
        "text": "Contact us at support@example.com or sales@company.org for more info.",
        "pattern": r"[\w.+-]+@[\w-]+\.[\w.-]+",
        "find_all": True,
    })


# ============================================================================
# WEB
# ============================================================================

async def test_web_search():
    return await run_tool("web_search", {
        "queries": ["Python 3.13 new features"],
        "max_results_per_query": 3,
    })


async def test_web_read():
    return await run_tool("web_read", {
        "urls": ["https://docs.python.org/3/whatsnew/3.13.html"],
        "max_content_length": 5000,
    })


async def test_web_research():
    return await run_tool("web_research", {
        "queries": ["latest AI developments 2026", "LLM benchmarks 2026"],
        "instructions": "Focus on practical breakthroughs that affect software developers. Include specific model names and capabilities.",
        "research_depth": "shallow",
    })


# ============================================================================
# DATABASE
# ============================================================================

async def test_db_query():
    return await run_tool("db_query", {
        "query": "SELECT id, name FROM tools WHERE is_active = true LIMIT 5",
    })


async def test_db_schema():
    return await run_tool("db_schema", {
        "table": "tools",
    })


# ============================================================================
# MEMORY
# ============================================================================

async def test_memory_store():
    return await run_tool("memory_store", {
        "key": "test_preference",
        "content": "User prefers dark mode and concise responses.",
        "memory_type": "long",
        "scope": "user",
        "importance": 0.7,
    })


async def test_memory_recall():
    return await run_tool("memory_recall", {
        "query": "user preferences",
        "scope": "user",
        "limit": 5,
    })


async def test_memory_search():
    return await run_tool("memory_search", {
        "query": "dark mode",
        "scope": "user",
        "limit": 5,
    })


# ============================================================================
# FILESYSTEM
# ============================================================================

async def test_fs_write_then_read():
    await run_tool("fs_write", {
        "path": "test_file.txt",
        "content": "Hello from fs_write test!\nLine 2.",
        "create_dirs": True,
    })
    return await run_tool("fs_read", {
        "path": "test_file.txt",
    })


async def test_fs_list():
    return await run_tool("fs_list", {
        "path": ".",
        "recursive": False,
    })


async def test_fs_search():
    return await run_tool("fs_search", {
        "pattern": "*.txt",
        "path": ".",
        "max_results": 20,
    })


# ============================================================================
# SHELL
# ============================================================================

async def test_shell_execute():
    return await run_tool("shell_execute", {
        "command": "echo 'Hello from shell test' && date",
        "timeout_seconds": 10,
    })


async def test_shell_python():
    return await run_tool("shell_python", {
        "code": "import sys; print(f'Python {sys.version}')\nprint(2 + 2)",
        "timeout_seconds": 10,
    })


# ============================================================================
# BROWSER
# ============================================================================

async def test_browser_navigate():
    return await run_tool("browser_navigate", {
        "url": "https://example.com",
        "extract_text": True,
    })


async def test_browser_screenshot():
    return await run_tool("browser_screenshot", {
        "url": "https://example.com",
        "width": 1280,
        "height": 720,
    })


# ============================================================================
# USER LISTS
# ============================================================================

async def test_create_simple_list():
    return await run_tool("create_simple_list", {
        "list_name": "Test Grocery List",
        "description": "Weekly groceries",
        "labels": ["Milk", "Eggs", "Bread", "Butter", "Apples"],
    })


async def test_get_user_lists():
    return await run_tool("get_user_lists", {
        "page": 1,
        "page_size": 10,
    })


# ============================================================================
# SEO
# ============================================================================

async def test_check_meta_titles():
    return await run_tool("check_meta_titles", {
        "titles": [
            "Best Python Frameworks 2026 - Complete Guide",
            "A",
            "This is an extremely long title that probably exceeds the recommended character limit for search engine optimization and will get truncated in search results pages",
        ],
    })


async def test_check_meta_descriptions():
    return await run_tool("check_meta_descriptions", {
        "descriptions": [
            "Learn about the best Python frameworks for web development in 2026. Compare FastAPI, Django, and Flask with real benchmarks.",
            "Short.",
        ],
    })


# ============================================================================
# CODE
# ============================================================================

async def test_store_html():
    return await run_tool("store_html", {
        "html_input": "<html><body><h1>Test Page</h1><p>Hello world</p></body></html>",
    })


async def test_fetch_code():
    return await run_tool("fetch_code", {
        "project_root": ".",
        "directory_to_fetch": "ai/tool_system/implementations",
        "output_type": "directory_structure",
    })


# ============================================================================
# NEWS
# ============================================================================

async def test_get_news_headlines():
    return await run_tool("get_news_headlines", {
        "country": "us",
        "category": "technology",
        "language": "en",
    })


# ============================================================================
# USER TABLES
# ============================================================================

async def test_create_user_generated_table():
    return await run_tool("create_user_generated_table", {
        "table_name": "Test Comparison Table",
        "description": "Framework comparison",
        "data": [
            {"framework": "FastAPI", "language": "Python", "stars": 70000},
            {"framework": "Express", "language": "JavaScript", "stars": 62000},
            {"framework": "Gin", "language": "Go", "stars": 74000},
        ],
    })


# ============================================================================
# QUESTIONNAIRE
# ============================================================================

async def test_ask_user_questions():
    return await run_tool("ask_user_questions", {
        "introduction": "Help me understand your project requirements:",
        "questions": [
            {
                "id": "framework",
                "prompt": "Which framework do you prefer?",
                "component_type": "dropdown",
                "options": ["FastAPI", "Django", "Flask", "Express"],
            },
            {
                "id": "scale",
                "prompt": "How important is performance?",
                "component_type": "slider",
            },
        ],
    })


# ============================================================================
# TRAVEL
# ============================================================================

async def test_get_location():
    return await run_tool("get_location", {})


async def test_get_weather():
    return await run_tool("get_weather", {
        "city": "San Francisco",
    })


async def test_get_restaurants():
    return await run_tool("get_restaurants", {
        "city": "San Francisco",
    })


async def test_get_activities():
    return await run_tool("get_activities", {
        "city": "San Francisco",
        "weather": "sunny",
    })


async def test_get_events():
    return await run_tool("get_events", {
        "city": "San Francisco",
        "weather": "sunny",
    })


async def test_create_travel_summary():
    return await run_tool("create_travel_summary", {
        "location": "San Francisco",
        "weather_info": {"condition": "sunny", "temp": 68},
        "restaurants": [{"name": "House of Prime Rib", "cuisine": "American"}],
        "activities": [{"name": "Golden Gate Bridge Walk", "type": "outdoor"}],
        "events": [{"name": "Outside Lands", "type": "music festival"}],
    })


# ============================================================================
# ALL AVAILABLE TESTS — copy a name below into `if __name__` to run it
# ============================================================================
#
#   Math:
#     test_calculate - x
#
#   Text:
#     test_text_analyze - x
#     test_regex_extract - x
#
#   Web:
#     test_web_search - X
#     test_web_read - x
#     test_web_research - x
#
#   Database:
#     test_db_query - x
#     test_db_schema - x
#
#   Memory:
#     test_memory_store - x
#     test_memory_recall - x
#     test_memory_search
#
#   Filesystem:
#     test_fs_write_then_read - x
#     test_fs_list - x
#     test_fs_search - x
#
#   Shell:
#     test_shell_execute
#     test_shell_python
#
#   Browser:
#     test_browser_navigate
#     test_browser_screenshot
#
#   User Lists:
#     test_create_simple_list - x
#     test_get_user_lists - x
#
#   SEO:
#     test_check_meta_titles - x
#     test_check_meta_descriptions - x
#
#   Code:
#     test_store_html
#     test_fetch_code
#
#   News:
#     test_get_news_headlines - x
#
#   User Tables:
#     test_create_user_generated_table - x
#
#   Questionnaire:
#     test_ask_user_questions - x
#
#   Travel:
#     test_get_location - x
#     test_get_weather - x
#     test_get_restaurants - x
#     test_get_activities - x
#     test_get_events - x
#     test_create_travel_summary - x
#
# ============================================================================


if __name__ == "__main__":
    clear_terminal()

    asyncio.run(test_get_user_lists())

    cleanup_async_resources()
