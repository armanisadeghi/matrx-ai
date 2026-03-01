# Tool System V2 — Rollout Checklist & Integration Guide

**Location**: `ai/tool_system/`
**Status**: LIVE — Tool System V2 is the default. Legacy mcp_server paths removed from ai/ module.
**Related**: `ai/tool_system/TOOL_OVERHAUL_PLAN.md` (full architecture plan)

---

## What's Been Built

| File | Purpose |
|------|---------|
| `models.py` | All Pydantic models: `ToolDefinition`, `ToolContext`, `ToolResult`, `ToolError`, `GuardrailResult`, `CxToolCallRecord` |
| `registry.py` | `ToolRegistryV2` — loads tools from DB, resolves callables, auto-generates param schemas from Pydantic models |
| `executor.py` | `ToolExecutor` — single execution pipeline for LOCAL, EXTERNAL_MCP, and AGENT tools |
| `guardrails.py` | `GuardrailEngine` — duplicate detection, rate limiting, conversation limits, cost budgets, loop detection, recursion depth |
| `streaming.py` | `ToolStreamManager` + `ToolStreamEvent` — structured streaming to client |
| `logger.py` | `ToolExecutionLogger` — fire-and-forget writes to `cx_tool_call` (single table, events embedded) |
| `lifecycle.py` | `ToolLifecycleManager` — resource cleanup, idle timeout, background sweep |
| `external_mcp.py` | `ExternalMCPClient` — JSON-RPC 2.0 client for remote MCP servers |
| `agent_tool.py` | `execute_agent_tool()` + `register_agent_as_tool()` — agent-as-tool execution with child usage tracking |
| `handle_tool_calls.py` | `handle_tool_calls_v2()` — drop-in replacement for the current `handle_tool_calls()` in `ai/ai_requests.py` |
| `sql_migrations.sql` | Database schema: `cx_tool_call`, `cx_agent_memory` |
| `arg_models/` | Pydantic argument models for every tool category (web, math, text, db, memory, fs, shell, browser) |
| `implementations/` | Actual tool functions in the new `async def tool(args, ctx) -> ToolResult` signature |
| `__init__.py` | Public API exports |
| `TOOL_OVERHAUL_PLAN.md` | Full architecture plan and rationale |

---

## Database Architecture

### Two tables total

1. **`cx_tool_call`** — Single source of truth for every tool call. One row per tool invocation, containing:
   - Input (arguments)
   - Output (full result text/json)
   - Performance (duration, timing)
   - Cost/usage (tokens, USD)
   - Streaming events (JSONB array, accumulated during execution, written once at completion)
   - Persistence metadata (persist_key, file_path)
   - Nesting (self-FK `parent_call_id` for agent-as-tool trees)

2. **`cx_agent_memory`** — Agent short/medium/long-term memory (separate entity, not tool execution data)

### How cx_tool_call integrates with cx_message

- `cx_message` rows with `role='tool'` are **lightweight positional markers** — their `content` is empty (null or `[]`).
- The full tool result lives solely in `cx_tool_call.output`.
- `cx_tool_call.message_id` is a FK back to the `cx_message` row.
- For conversation rebuild (cold load), a `LEFT JOIN` or parallel query fetches the tool data.
- For streaming (live), the UI reads from the stream — it never touches `cx_message.content` for tool rows.
- This eliminates data duplication and makes `cx_tool_call` the single authoritative source.

### Why not 3 separate tables?

The previous design had `tool_execution_logs`, `tool_execution_events`, and `tool_outputs` — this created duplicative storage and scattered a single tool call's data across 3 tables. The consolidated `cx_tool_call` table stores everything in one place:
- Events go into the `execution_events` JSONB column (accumulated during the call, written once)
- Persisted output is identified by the `persist_key` column — no separate outputs table needed
- Analytics queries hit one table instead of joining three

---

## Pre-Integration Checklist

### 1. Database Migrations

- [ ] **Review `sql_migrations.sql`** — read through the 2 new tables and their indexes
- [ ] **Run migrations on dev/staging Supabase instance** — all migrations are additive (no drops or modifications)
  ```sql
  -- Run the contents of ai/tool_system/sql_migrations.sql against your Supabase SQL editor
  ```
- [ ] **Add RLS policies** to the 2 new tables based on your auth model:
  - `cx_tool_call` — service role only for writes (backend writes); admin and user can read own via `user_id = auth.uid()`
  - `agent_memory` — user can CRUD own memories (`user_id = auth.uid()`)
- [ ] **Decide on guardrail columns** — currently, guardrail config is read from the `annotations` JSONB on the existing `tools` table. Alternatively, uncomment the explicit columns in the migration file.

### 2. Dependencies

- [ ] **Verify `pydantic` ≥ 2.12** is installed — `uv pip list | grep pydantic`
- [ ] **Verify `httpx`** is installed (used by `ExternalMCPClient`) — `uv pip list | grep httpx`
- [ ] **Optional: Verify `playwright`** is installed if browser tools are needed — `pip install playwright && playwright install chromium`

### 3. Test the System in Isolation

The entire `ai/tool_system/` is self-contained. You can test it without touching any production code:

```python
import asyncio
from ai.tool_system import ToolRegistryV2, ToolExecutor, GuardrailEngine, ToolContext
from ai.tool_system.implementations.math import calculate
from ai.tool_system.implementations.text import text_analyze, regex_extract

async def test_basic():
    # 1. Set up registry with local tools (no DB needed)
    registry = ToolRegistryV2()
    registry.register_local("calculate", calculate, description="Math calculator", category="math")
    registry.register_local("text_analyze", text_analyze, description="Text analysis", category="text")
    registry.register_local("regex_extract", regex_extract, description="Regex extraction", category="text")

    # 2. Create executor
    executor = ToolExecutor(registry=registry)

    # 3. Build context
    ctx = ToolContext(
        user_id="test-user",
        conversation_id="test-conv",
        request_id="test-req",
        call_id="test-call-1",
        tool_name="calculate",
    )

    # 4. Execute
    content_dict, result = await executor.execute("calculate", {"expression": "2 ** 10"}, ctx)
    print(f"Success: {result.success}")
    print(f"Output: {result.output}")
    print(f"Duration: {result.duration_ms}ms")
    print(f"Content dict: {content_dict}")

    # 5. Test guardrails (duplicate detection)
    ctx2 = ctx.model_copy(update={"call_id": "test-call-2"})
    content_dict2, result2 = await executor.execute("calculate", {"expression": "2 ** 10"}, ctx2)
    print(f"\nDuplicate blocked: {not result2.success}")
    print(f"Error: {result2.error.message if result2.error else 'None'}")

asyncio.run(test_basic())
```

- [ ] **Run the test above** and verify all assertions pass
- [ ] **Test batch execution** with multiple tools
- [ ] **Test error handling** — call a non-existent tool, pass invalid args
- [ ] **Test guardrails** — rate limits, loop detection, recursion depth

### 4. Test with Database

```python
async def test_with_db():
    from supabase import create_client
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    from ai.tool_system.handle_tool_calls import initialize_tool_system
    count = await initialize_tool_system(supabase)
    print(f"Loaded {count} tools from database")

    # Now execute tools that are registered in the DB
    # ...
```

- [ ] **Run with your dev Supabase instance** and verify tool loading
- [ ] **Check `cx_tool_call`** table — verify rows are being written with output, events, cost data
- [ ] **Verify streaming events** are embedded in the `execution_events` JSONB column

---

## Integration Steps (Phased Rollout)

### Phase 1: Initialize at Startup (No Breaking Changes)

**File**: `run.py` or your FastAPI startup hook

```python
# Add to your app startup
from ai.tool_system.handle_tool_calls import initialize_tool_system

@app.on_event("startup")
async def startup():
    # ... existing startup code ...
    await initialize_tool_system(supabase_client)
```

- [ ] Add `initialize_tool_system()` to app startup
- [ ] Verify it loads tools and starts the lifecycle sweep
- [ ] Monitor logs for any resolution errors

### Phase 2: Feature-Flagged Dual Path

**File**: `ai/ai_requests.py`

The key change is in the `handle_tool_calls` function. Add a feature flag to route to either the old or new system:

```python
# At the top of ai/ai_requests.py
USE_NEW_TOOL_SYSTEM = False  # Flip to True to enable

# In handle_tool_calls():
if USE_NEW_TOOL_SYSTEM:
    from ai.tool_system.handle_tool_calls import handle_tool_calls_v2
    
    tool_calls_raw = [
        {"name": tc.name, "arguments": tc.arguments, "call_id": tc.call_id or tc.id}
        for tc in tool_calls
    ]
    
    content_dicts, child_usages = await handle_tool_calls_v2(
        tool_calls_raw,
        user_id=current_request.user_id,
        conversation_id=current_request.conversation_id,
        request_id=current_request.request_id,
        iteration=iteration,
        stream_handler=current_request.stream_handler,
        supabase_client=supabase_client,
    )
    
    # Convert content dicts back to ToolResultContent dataclasses
    from config.tools_config import ToolResultContent
    results = [ToolResultContent(**d) for d in content_dicts]
    
    # Aggregate child usages into parent request
    for usage_dict in child_usages:
        from ai.usage_config import TokenUsage
        current_request.add_usage(TokenUsage(
            input_tokens=usage_dict.get("input_tokens", 0),
            output_tokens=usage_dict.get("output_tokens", 0),
            model=usage_dict.get("model", ""),
            api=usage_dict.get("api", ""),
        ))
    
    return results, tool_call_usage
else:
    # ... existing handle_tool_calls code ...
```

- [ ] Add the feature flag `USE_NEW_TOOL_SYSTEM = False`
- [ ] Add the dual-path code in `handle_tool_calls()`
- [ ] Test with flag OFF — verify existing system still works
- [ ] Flip flag ON for a single test conversation — verify results match
- [ ] Check `cx_tool_call` rows have correct data

### Phase 3: Update Persistence Layer

**File**: `ai/db/persistence.py`

The `persist_completed_request()` function currently stores `role='tool'` messages with content in `cx_message`. Update it so that:

1. For `role='tool'` messages, `cx_message.content` is saved as `null` or `[]`
2. The full tool result data is written to `cx_tool_call` by the logger (this already happens automatically in the new system)
3. After writing the `cx_message` row, the `cx_tool_call` row is updated with `message_id` to link them

```python
# In persist_completed_request(), when processing role='tool' messages:
# Instead of storing the tool result in cx_message.content:
message_row = {
    "role": "tool",
    "content": None,  # Full data lives in cx_tool_call
    "position": position,
    "conversation_id": conversation_id,
    # ...
}
# After insert, update cx_tool_call.message_id with the new message ID
```

- [ ] Update persistence to write empty content for tool messages
- [ ] Add message_id backfill to cx_tool_call after cx_message insert
- [ ] Test conversation rebuild with JOIN query

### Phase 4: Migrate Existing Tool Functions

For each tool currently registered in `mcp_server/tools/`, create a new implementation in `ai/tool_system/implementations/`:

**Current pattern** (6 layers):
```python
# mcp_server/tools/core/web.py
@tool_registry.register(...)
def web_search_summarized(arguments, call_id=None, stream_handler=None):
    queries = arguments.get("queries", [])
    return search_web_mcp_summarized(queries=queries, ...)
```

**New pattern** (1 layer):
```python
# ai/tool_system/implementations/web.py
async def web_search(args: dict, ctx: ToolContext) -> ToolResult:
    parsed = WebSearchArgs(**args)
    # Direct business logic here — no wrapper
    ...
```

Migration order (by risk/impact):
1. [ ] `calculate` (math) — simplest, pure function
2. [ ] `text_analyze`, `regex_extract` — pure functions, no external calls
3. [ ] `web_search_quick`, `web_read_quick` — external calls but no AI
4. [ ] `web_search_summarized`, `web_read_summarized` — uses the new `_summarize_helper` instead of legacy `summarize_scrape_pages_agent_DEPRECATED()`
5. [ ] `db_query`, `db_insert`, `db_update` — database tools
6. [ ] `shell_execute`, `shell_python` — new tools (not migrating, adding fresh)
7. [ ] `memory_store`, `memory_recall`, etc. — new tools
8. [ ] `browser_*` — new tools

**For each migrated tool**:
- [ ] Ensure the tool's `function_path` in the `tools` DB table points to the new implementation (e.g. `ai.tool_system.implementations.math.calculate`)
- [ ] Test the tool through the new executor
- [ ] Verify results match the old system
- [ ] Verify `cx_tool_call` rows are correct

### Phase 5: Wire Up Agent-as-Tool

- [ ] Create a test agent tool using `register_agent_as_tool()`
- [ ] Verify child usage tracking works (tokens from the child agent appear in parent's `cx_tool_call` row)
- [ ] Test recursion depth guardrail — agent calling agent calling agent stops at depth 3
- [ ] Test cost cap — agent tool blocked when cost exceeds cap
- [ ] Verify `parent_call_id` nesting in cx_tool_call — recursive query should rebuild the full call tree

### Phase 6: External MCP Support

- [ ] Configure an external MCP server URL
- [ ] Call `registry.register_mcp_server(url, name)` to discover and register tools
- [ ] Test calling an external tool through the executor
- [ ] Verify timeout and error handling for remote calls

### Phase 7: Cleanup Old System

Once all tools are migrated and the new system is stable:

- [ ] Remove the feature flag — new system is the only path
- [ ] Delete `mcp_server/core/registry.py` (old `ToolRegistry`)
- [ ] Delete `mcp_server/core/tracker.py` (old `ToolUsageTracker`)
- [ ] Delete all `register_*_tool()` wrapper functions in `mcp_server/tools/`
- [ ] Delete thin wrapper functions (the ones that just extract args and delegate)
- [ ] Delete `mcp_server/local_utils/tools_constants.tsx` — frontend should read from DB
- [ ] Update `mcp_server/__init__.py` to point to the new system
- [ ] Delete the `summarize_scrape_pages_agent_DEPRECATED()` function in `scraper/.../mcp_tool_helpers.py`
- [ ] Delete the legacy `GoogleChatEndpoint` / `AiConfig` usage for summarization
- [ ] Run full regression tests

---

## Architecture Quick Reference

### How a Tool Call Flows (New System)

```
LLM Response → ToolCallContent
    ↓
handle_tool_calls_v2()
    ↓
ToolExecutor.execute_batch()
    ↓ (for each tool call, concurrently)
ToolExecutor.execute()
    ├── 1. Registry lookup → ToolDefinition
    ├── 2. Build ToolContext (user, conversation, keys, limits)
    ├── 3. GuardrailEngine.check() → pass/block
    ├── 4. Stream "started" to client
    ├── 5. Dispatch:
    │   ├── LOCAL → tool_function(args, ctx) → ToolResult
    │   ├── EXTERNAL_MCP → ExternalMCPClient.call_tool()
    │   └── AGENT → execute_agent_tool() → child agent with usage tracking
    ├── 6. Stream "completed" / "error" to client
    ├── 7. ToolExecutionLogger.log() → single cx_tool_call row (fire-and-forget)
    └── 8. Return ToolResult → converted to ToolResultContent dict
```

### How Data is Stored

```
cx_message (role='tool')              cx_tool_call
┌─────────────────────┐              ┌──────────────────────────────┐
│ id: UUID             │◄────────────│ message_id: UUID (FK)        │
│ role: 'tool'         │              │ id: UUID                     │
│ content: null        │              │ tool_name, call_id           │
│ position: int        │              │ arguments (JSONB)            │
│ conversation_id      │              │ output (TEXT — full result)  │
└─────────────────────┘              │ success, is_error            │
                                      │ duration_ms, tokens, cost    │
                                      │ execution_events (JSONB[])   │
                                      │ persist_key, file_path       │
                                      │ parent_call_id (self-FK)     │
                                      └──────────────────────────────┘
```

### Key Differences from Old System

| Aspect | Old | New |
|--------|-----|-----|
| DB tables for tools | 0 (data buried in cx_message.content JSON) | 1 (`cx_tool_call` — normalized, queryable) |
| Layers | 6 (registry → wrapper → helper → legacy) | 2 (executor → function) |
| Context passing | `inspect.signature()` magic | Explicit `ToolContext` parameter |
| Error format | `{"status": "error", "result": "..."}` string | `ToolError` with type, traceback, suggested action |
| Usage tracking | Only tracks parent; `summarize_scrape_pages_agent_DEPRECATED()` untracked | All child usages aggregated via `ToolResult.child_usages` |
| Guardrails | Single duplicate check | 6 checks: duplicate, rate, conversation, cost, loop, recursion |
| Streaming | Scattered `stream_handler.send_function_call()` | Centralized `ToolStreamManager` |
| Streaming events | Separate `tool_execution_events` table | Embedded `execution_events` JSONB in `cx_tool_call` |
| Tool output storage | `tool_outputs` table + `cx_message.content` (duplicated) | `cx_tool_call.output` (single source of truth) |
| Tool source | Hardcoded `register_*()` + DB (duplicated) | DB is single source of truth; code provides callables |
| External MCPs | Not supported | `ExternalMCPClient` with JSON-RPC 2.0 |
| Agent-as-tool | Not supported | `ToolType.AGENT` with child session + usage tracking |

### File Locations

```
ai/tool_system/
├── __init__.py                  # Public API
├── models.py                    # All Pydantic models (including CxToolCallRecord)
├── registry.py                  # ToolRegistryV2
├── executor.py                  # ToolExecutor (core pipeline)
├── guardrails.py                # GuardrailEngine
├── streaming.py                 # ToolStreamManager
├── logger.py                    # ToolExecutionLogger (writes to cx_tool_call)
├── lifecycle.py                 # ToolLifecycleManager
├── external_mcp.py              # ExternalMCPClient
├── agent_tool.py                # Agent-as-tool execution
├── handle_tool_calls.py         # Drop-in replacement for ai/ai_requests.py
├── sql_migrations.sql           # Database schema (cx_tool_call + agent_memory)
├── TOOL_OVERHAUL_PLAN.md        # Full architecture plan
├── ROLLOUT_CHECKLIST.md         # This file
│
├── arg_models/                  # Pydantic argument models
│   ├── web_args.py
│   ├── math_args.py
│   ├── text_args.py
│   ├── db_args.py
│   ├── memory_args.py
│   ├── fs_args.py
│   ├── shell_args.py
│   └── browser_args.py
│
└── implementations/             # Tool functions
    ├── math.py                  # calculate
    ├── text.py                  # text_analyze, regex_extract
    ├── web.py                   # web_search, web_read
    ├── database.py              # db_query, db_insert, db_update, db_schema
    ├── memory.py                # memory_store/recall/search/update/forget
    ├── filesystem.py            # fs_read/write/list/search/mkdir
    ├── shell.py                 # shell_execute, shell_python
    ├── browser.py               # browser_navigate/click/type/screenshot
    └── _summarize_helper.py     # Replaces legacy summarize_scrape_pages_agent_DEPRECATED() with unified AI
```

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `TOOL_WORKSPACE_BASE` | `/tmp/workspaces` | Base directory for filesystem tools |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| New system has bugs that break tool calls | Feature flag allows instant rollback |
| Database tables missing | All migrations are `IF NOT EXISTS` |
| Existing tools' `function_path` doesn't match new locations | Registry falls back to old paths; can be updated in DB |
| Performance regression from Pydantic validation | Pydantic v2 is fast; validation adds < 1ms per call |
| External MCP server unreachable | Timeout + retry + error propagated to agent |
| Agent-as-tool cost runaway | GuardrailEngine cost cap + recursion depth limit |
| Tool data lost during schema migration | No data migration needed — new table is additive, old data stays in cx_message |
