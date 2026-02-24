# TASKS.md — matrx-ai Detailed Task List

**Last updated:** 2026-02-24
**Status legend:** `CRITICAL` `HIGH` `MEDIUM` `LOW`

---

## 1. CRITICAL — Wire Routers to AI Engine

The routers in `app/routers/` are all placeholder/mock. The real execution engine exists in `client/`, `providers/`, and `conversation/` but is **not connected** to the HTTP layer. This is the single most important set of tasks.

### 1.1 Wire `/api/ai/chat` to real providers — `CRITICAL`
**File:** `app/routers/chat.py`
**Problem:** `_mock_stream()` (line 64) returns canned echo responses. Real providers in `providers/` are never called.
**Solution:**
- Replace `_mock_stream()` with a function that:
  1. Creates an `AppContext` with user_id from auth (or anonymous)
  2. Builds a `UnifiedConfig` from the `ChatRequest` body
  3. Creates an `AIMatrixRequest`
  4. Instantiates `UnifiedAIClient` and calls `execute_until_complete()`
  5. Streams real provider responses via the existing SSE/NDJSON helpers
- The `_chat_blocking()` path also needs the same treatment
- Token usage in response (line 54) currently returns all zeros

### 1.2 Wire `/api/ai/agents/{agent_id}` to real agent orchestration — `CRITICAL`
**File:** `app/routers/agent.py`
**Problem:** `_mock_agent_stream()` (line 106) returns hardcoded steps. No real agent execution.
**Solution:**
- Replace mock with:
  1. Load agent config from DB (prompts, tools, system instructions)
  2. Build `AIMatrixRequest` from `AgentRunRequest`
  3. Execute via `execute_until_complete()` with real tool handling
  4. Stream multi-step events (thinking, tool_call, chunk, done)
- Replace `_KNOWN_AGENTS` wildcard (line 98) with real agent registry from DB
- `_assert_agent_exists()` should query the `prompts` or `prompt_builtins` table

### 1.3 Wire `/api/ai/conversations/{id}` to real conversation engine — `CRITICAL`
**File:** `app/routers/conversation.py`
**Problem:** `_mock_conversation_stream()` (line 50) echoes input back.
**Solution:**
- Replace mock with:
  1. Load existing conversation from DB (messages, config, model)
  2. Rebuild conversation state via `conversation/rebuild.py`
  3. Append new user message
  4. Execute via `execute_until_complete()`
  5. Stream response
- This router only supports NDJSON currently — add SSE support for parity with chat/agent

### 1.4 Wire `/api/ai/cancel/{request_id}` — `HIGH`
**File:** `app/routers/agent.py` (line 90)
**Problem:** Returns static `{"status": "cancel_requested"}`, does nothing.
**Solution:**
- Implement cancellation via:
  1. Look up running request by ID
  2. Set a cancellation flag (e.g., via asyncio.Event or a shared store)
  3. The `execute_until_complete()` loop should check for cancellation between iterations
  4. Update `cx_user_request` status to "cancelled"

### 1.5 Wire `/warm` endpoints — `MEDIUM`
**Files:** `app/routers/agent.py` (line 62), `app/routers/conversation.py` (line 41)
**Problem:** Both are TODO stubs.
**Solution:**
- Pre-load and cache:
  - Agent config (prompts, tools, system instructions)
  - Conversation history (messages, metadata)
  - Model warm-up (optional: send a minimal request to keep provider connection alive)

---

## 2. CRITICAL — Authentication & Authorization

### 2.1 Add auth middleware to extract user identity — `CRITICAL`
**Problem:** No authentication on any endpoint. `AppContext.user_id` is never set from HTTP requests.
**Solution:**
- Add Supabase JWT verification middleware or dependency
- Extract user_id from `Authorization: Bearer <token>` header
- Set `AppContext` with authenticated user info
- Reject unauthenticated requests on AI endpoints (health can remain public)

### 2.2 Add request-level authorization — `HIGH`
**Problem:** No checks that a user owns a conversation before continuing it.
**Solution:**
- Before operating on a conversation, verify `cx_conversation.user_id` matches authenticated user
- Same for cancel, warm, and agent endpoints

---

## 3. HIGH — Tool System Integration

### 3.1 Replace hardcoded tool registry in router — `HIGH`
**File:** `app/routers/tool.py` (line 23-50)
**Problem:** `_TOOL_REGISTRY` is a hardcoded dict with only "search" (stub) and "calculator".
**Solution:**
- Replace with `ToolRegistryV2` from `tools/registry.py` which loads from DB
- Call `initialize_tool_system()` at app startup (in `lifespan()`)
- Wire `/api/tools/test/execute` to `ToolExecutor` from `tools/executor.py`
- Remove `/test/` prefix from production routes (or add a real `/api/tools/` router)

### 3.2 Wire search tool to real implementation — `HIGH`
**File:** `app/routers/tool.py` (line 94)
**Problem:** Search returns `{"results": [], "note": "stub — wire real search"}`
**Solution:**
- The real `web_search` tool exists in `tools/implementations/web.py`
- Route through `ToolExecutor` instead of the inline `_dispatch()` function

### 3.3 Replace mock travel tools or remove — `LOW`
**File:** `tools/implementations/travel.py`
**Problem:** Returns random/hardcoded data. Docstring says "retained for demo/test purposes."
**Decision needed:** Keep as demo or remove entirely.

---

## 4. HIGH — App Startup & Lifecycle

### 4.1 Initialize tool system at startup — `HIGH`
**File:** `app/main.py` (line 67-81, `lifespan()`)
**Problem:** The lifespan function has comments saying "Place async resource initialisation here" but nothing is initialized.
**Solution:**
- Call `initialize_tool_system()` from `tools/handle_tool_calls.py`
- Initialize DB connection pool
- Warm AI model cache from `db/custom/ai_model_manager.py`
- Create shared `httpx.AsyncClient` on `app.state`

### 4.2 Add graceful shutdown — `MEDIUM`
**File:** `app/main.py` (line 79-81)
**Problem:** Shutdown section is empty (just a log message).
**Solution:**
- Close httpx client
- Flush pending persistence writes
- Close DB connections
- Cancel any running agent executions

---

## 5. HIGH — Health Check Improvements

### 5.1 Add real health checks — `HIGH`
**File:** `app/routers/health.py`
**Problem:** `_run_checks()` only verifies the event loop is running. No DB, provider, or dependency checks.
**Solution:**
- Add Supabase DB ping (simple `SELECT 1`)
- Add provider API key validation (non-empty check, not actual API calls)
- Check tool registry loaded
- Report individual component status in `/api/health/detailed`

---

## 6. HIGH — Database Manager Completion

### 6.1 Complete DTO validation stubs — `HIGH`
**Files:** All files in `db/managers/` (16 files)
**Problem:** Every generated manager has 4 empty `pass` methods in the DTO class:
```python
async def _initialize_dto(self, model): pass
async def _process_core_data(self, model): pass
async def _process_metadata(self, model): pass
async def _initial_validation(self, model): pass
```
**Decision needed:** Are these intentional hooks for custom logic, or do they need implementations?
**Note:** The base class in matrx-orm may provide default behavior. Verify before modifying.

### 6.2 Implement shared utility stubs — `MEDIUM`
**Files:**
- `shared/supabase_client.py` (line 1: "Placeholder") — needs real `get_supabase_client()`
- `shared/file_handler.py` (line 1: "Placeholder") — needs real `FileHandler`
- `shared/json_utils.py` (line 1: "Placeholder") — needs real `to_matrx_json()`

---

## 7. MEDIUM — Prompt System Completion

### 7.1 Implement prompt database persistence — `MEDIUM`
**File:** `prompts/tests/agent_old.py` (lines 505, 661-731)
**Problem:** 6 TODO comments for "Implement database save" / "Placeholder for database integration"
**Note:** This is in a test/old file. Verify if the main `prompts/manager.py` handles persistence already. If so, this file can be deleted.

### 7.2 Clean up old prompt test file — `LOW`
**File:** `prompts/tests/agent_old.py`
**Problem:** Contains placeholder imports (`from typing import Any as StreamHandler`) and multiple stub methods.
**Decision needed:** Delete or migrate useful tests to proper test files.

---

## 8. MEDIUM — Testing Infrastructure

### 8.1 Create conftest.py with shared fixtures — `HIGH`
**Problem:** No `conftest.py` exists. Each test imports its own context. No shared fixtures.
**Solution:**
- Create `tests/conftest.py` with:
  - `@pytest.fixture` for `AppContext`
  - `@pytest.fixture` for `UnifiedAIClient`
  - `@pytest.fixture` for DB connection
  - Environment validation

### 8.2 Convert manual tests to proper pytest tests — `MEDIUM`
**Problem:** 18 of 19 test files are manual scripts (not discoverable by pytest).
**Files needing conversion:**
- `tests/ai/execution_test.py`
- `tests/ai/groq_transcription_test.py`
- `tests/openai/openai_small_tests.py`
- `tests/openai/openai_image_input.py`
- `tests/openai/openai_function_test.py`
- `tests/openai/conversation_id_test.py`
- `tests/openai/background_stream_async.py`
- `tests/openai/openai_translation_test.py`
- `tests/prompts/test_basic_prompts.py`
- `tests/prompts/prompt_to_config.py`
- `tests/prompts/agent_comparison.py`

### 8.3 Add missing test coverage — `MEDIUM`
**Not tested at all:**
- FastAPI route testing (TestClient / httpx)
- Database CRUD operations
- Authentication/authorization
- Streaming edge cases (interruptions, timeouts)
- Tool execution pipeline end-to-end
- Conversation persistence
- Error handling paths
- Provider failover/retry logic

### 8.4 Add CI-friendly test mode — `LOW`
**Problem:** Tests require real API keys and Supabase access. No mock/stub mode for CI.
**Solution:**
- Add `@pytest.mark.integration` markers for tests needing real services
- Create mock providers for unit tests
- Default `make test` to skip integration tests

---

## 9. MEDIUM — Conversation Router SSE Support

### 9.1 Add SSE streaming to conversation router — `MEDIUM`
**File:** `app/routers/conversation.py`
**Problem:** Only supports NDJSON. Chat and agent routers support both SSE and NDJSON.
**Solution:** Add `stream_mode` to `ConversationContinueRequest` and handle SSE like the chat router does.

---

## 10. MEDIUM — Security & Hardening

### 10.1 Remove eval() from calculator tool — `MEDIUM`
**File:** `app/routers/tool.py` (line 98)
**Problem:** `eval(expr, {"__builtins__": {}}, {})` — restricted but still risky.
**Note:** The real calculator in `tools/implementations/math.py` uses safe evaluation. This is only in the placeholder router.

### 10.2 Review API key exposure — `HIGH`
**Problem:** `.env` contains real API keys. Verify `.gitignore` includes `.env`.
**Action:** Confirm `.env` is in `.gitignore`. Check git history for accidental commits.

### 10.3 Disable docs/openapi in production — `LOW`
**File:** `app/main.py` (lines 97-99)
**Status:** Already done — docs disabled when `settings.debug == False`. Verify production .env sets `DEBUG=false`.

---

## 11. LOW — Code Quality & Cleanup

### 11.1 Remove dead/placeholder shared modules — `LOW`
**Files:** `shared/json_utils.py`, `shared/file_handler.py`
**Problem:** Marked as "Placeholder" with minimal or no implementation.
**Action:** Either implement or remove. Update imports if removed.

### 11.2 Clean up Cerebras mock response — `LOW`
**File:** `providers/cerebras_api.py` (line 263)
**Problem:** Uses `SimpleNamespace` to create a mock response object in non-streaming path.
**Note:** May be intentional for reconstructing streaming chunks into a response-like object. Verify.

### 11.3 Clean up prompts/session.py empty methods — `LOW`
**File:** `prompts/session.py` (lines 38, 60, 69, 78)
**Problem:** Multiple methods with only `pass`.
**Action:** Verify if these are abstract hooks or need implementations.

### 11.4 Move `json_utils` import — `LOW`
**File:** `tests/ai/execution_test.py` (line 13)
**Problem:** TODO comment: "move to matrx_utils or inline json.dumps"

---

## 12. LOW — Documentation & DevEx

### 12.1 Populate README.md — `LOW`
**File:** `README.md`
**Problem:** Contains only `# matrx-ai`. No setup instructions, architecture overview, or API docs.

### 12.2 Add .env.example completeness check — `LOW`
**Problem:** Some env vars used in code may not be in `.env.example`.
**Action:** Audit all `Settings` fields against `.env.example`.

### 12.3 Add API documentation — `LOW`
**Problem:** No API documentation beyond FastAPI auto-generated docs (which are disabled in production).
**Action:** Consider generating OpenAPI spec for client teams.

---

## Summary: Priority Order

| Priority | Count | Focus |
|----------|-------|-------|
| **CRITICAL** | 5 | Wire routers to engine, add auth |
| **HIGH** | 8 | Tool integration, startup lifecycle, health checks, test fixtures, API key review |
| **MEDIUM** | 8 | DB stubs, prompt persistence, test conversion, SSE support, security |
| **LOW** | 7 | Cleanup, docs, dead code removal |

### Recommended Execution Order

1. **Auth middleware** (2.1) — Everything else depends on knowing who the user is
2. **Wire chat router** (1.1) — Smallest surface area, validates the pattern
3. **App startup initialization** (4.1) — Tool system and DB connections
4. **Wire agent router** (1.2) — Builds on chat pattern + tool execution
5. **Wire conversation router** (1.3) — Adds state management
6. **Tool router integration** (3.1, 3.2) — Replace hardcoded registry
7. **Health checks** (5.1) — Operational readiness
8. **Cancel endpoint** (1.4) — Needed for production reliability
9. **Test infrastructure** (8.1, 8.2) — Enable confident iteration
10. **Everything else** — Warm endpoints, cleanup, docs
