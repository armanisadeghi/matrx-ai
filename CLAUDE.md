# CLAUDE.md — matrx-ai

**Project:** Matrx AI Engine — Core FastAPI backend for AI orchestration
**Owner:** Arman (Armani) Sadeghi

---

## What This Is

A **Python FastAPI backend** that serves as the unified AI orchestration engine for all Matrx products. It integrates 7 AI providers, manages multi-turn conversations with persistent state, executes tools via a registry-based system, and streams responses via SSE/NDJSON.

This is **not** a frontend project. It is consumed by separate Next.js and React Native clients via REST/streaming APIs.

**Origin:** Extracted from the main `aidream` application (`ai/` layer) into a standalone package. Directory mapping from aidream:

- `ai/` → `client/`
- `ai/config/` → `config/`
- `ai/db/` → `conversation/`
- `ai/providers/` → `providers/`
- `ai/tool_system/` → `tools/`
- `ai/prompts/` → `prompts/`
- `aidream/api/` → `app/` and `context/`

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI 0.115+ with uvloop |
| **Runtime** | Python 3.13+ |
| **Async** | uvloop (2-4x throughput over default asyncio) |
| **Serialization** | orjson (10x faster than stdlib json) |
| **Streaming** | SSE (sse-starlette) + NDJSON |
| **Validation** | Pydantic 2.10+ / pydantic-settings |
| **Database** | Supabase PostgreSQL via matrx-orm 2.0.10 |
| **AI Providers** | OpenAI, Anthropic, Google Gemini, Groq, Cerebras, Together AI, xAI |
| **Error Tracking** | Sentry |
| **Package Manager** | uv |
| **Linting** | ruff (py313, line-length 100) |
| **Type Checking** | pyright (standard mode) |
| **Testing** | pytest + pytest-asyncio |

---

## Quick Start

```bash
uv sync                  # Install dependencies
make dev                 # Dev server with reload on :8000
make run                 # Production mode
make lint                # ruff check
make fmt                 # ruff format
make typecheck           # pyright
make test                # pytest -v
```

---

## Project Structure

```
matrx-ai/
├── app/                          # FastAPI application
│   ├── main.py                   # App factory, lifespan, middleware, router registration
│   ├── config.py                 # pydantic-settings (reads .env)
│   ├── core/
│   │   ├── ai_task.py            # run_ai_task() — shared streaming task for all AI routes
│   │   ├── response.py           # create_streaming_response() — NDJSON streaming infra
│   │   ├── cancellation.py       # CancellationRegistry
│   │   ├── exceptions.py         # MatrxException hierarchy + handlers
│   │   ├── middleware.py         # RequestContextMiddleware (request ID + timing)
│   │   ├── streaming.py          # SSE & NDJSON response helpers, keepalive
│   │   └── sentry.py             # Sentry init
│   ├── routers/
│   │   ├── health.py             # /api/health
│   │   ├── chat.py               # /api/ai/chat — uses run_ai_task
│   │   ├── agent.py              # /api/ai/agents/* — uses AgentConfigResolver + run_ai_task
│   │   ├── conversation.py       # /api/ai/conversations/* — uses ConversationResolver + run_ai_task
│   │   └── tool.py               # /api/tools/test/*
│   └── models/                   # Pydantic request/response schemas
│       ├── chat.py               # ChatRequest
│       ├── agent.py              # AgentStartRequest
│       ├── conversation.py       # ConversationContinueRequest
│       └── tool.py               # ToolCallRequest, ToolCallResult
│
├── client/                       # Unified AI client & execution engine
│   ├── unified_client.py         # AIMatrixRequest, UnifiedAIClient, CompletedRequest
│   ├── ai_requests.py            # execute_until_complete() + execute_ai_request() entry point
│   ├── translators.py            # Provider response → unified format (TokenUsage)
│   ├── usage.py                  # TokenUsage (matrx_model_name + provider_model_name)
│   ├── timing.py                 # TimingUsage tracking
│   ├── tool_call_tracking.py     # ToolCallUsage tracking
│   ├── recovery_logic.py         # Finish reason handling + retry decisions
│   ├── errors.py                 # Error classification per provider
│   ├── thinking_config.py        # Extended thinking / reasoning config
│   ├── stream_protocol.py        # Stream parsing protocols
│   ├── cache.py                  # Response caching
│   └── system_agents.py          # System-level agent definitions
│
├── providers/                    # AI provider SDKs
│   ├── openai_api.py             # AsyncOpenAI (Responses API)
│   ├── anthropic_api.py          # AsyncAnthropic
│   ├── google_api.py             # google.genai
│   ├── groq_api.py               # AsyncGroq (OpenAI-compatible)
│   ├── cerebras_api.py           # AsyncCerebras
│   ├── together_api.py           # AsyncTogether
│   └── xai_api.py                # AsyncOpenAI → xAI endpoint
│
├── conversation/                 # Conversation persistence & lifecycle
│   ├── cx_managers.py            # CxManagers singleton (cxm) — unified DB access
│   ├── conversation_resolver.py  # ConversationResolver + AgentConfigResolver
│   ├── gate.py                   # ensure_conversation_exists, create_pending_user_request
│   ├── persistence.py            # persist_completed_request (central write path)
│   └── rebuild.py                # Rebuild conversation from raw message/tool/media data
│
├── config/                       # Domain configuration models
│   ├── unified_config.py         # UnifiedConfig, UnifiedMessage, UnifiedResponse
│   ├── tools_config.py           # Tool definitions & config
│   ├── media_config.py           # Media handling config
│   ├── enums.py                  # Shared enumerations
│   ├── finish_reason.py          # Finish reason mapping
│   └── extra_config.py           # Extended config options
│
├── context/                      # Request-scoped context (ContextVar)
│   ├── app_context.py            # AppContext: user_id, emitter, conversation state
│   ├── stream_emitter.py         # StreamEmitter for NDJSON responses
│   ├── emitter_protocol.py       # Streaming emitter protocol
│   ├── events.py                 # Event type definitions (CompletionPayload, etc.)
│   └── console_emitter.py        # Dev/test console emitter
│
├── tools/                        # Tool system V2
│   ├── registry.py               # ToolRegistryV2 — loads from DB
│   ├── executor.py               # ToolExecutor — unified execution pipeline
│   ├── handle_tool_calls.py      # Integration with AI request loop
│   ├── guardrails.py             # 6-layer security (rate, cost, loop, recursion)
│   ├── models.py                 # ToolResult, ToolContext, ToolError
│   ├── logger.py                 # Two-phase DB logging via cxm.tool_call
│   ├── streaming.py              # Tool event streaming
│   ├── lifecycle.py              # Tool lifecycle management
│   ├── arg_models/               # Pydantic input validators per tool
│   └── implementations/          # 14 tool implementations
│       ├── browser.py, code.py, database.py, filesystem.py
│       ├── math.py, memory.py, news.py, questionnaire.py
│       ├── seo.py, shell.py, text.py, travel.py
│       ├── user_lists.py, user_tables.py, web.py
│
├── prompts/                      # Prompt management & templating
│   ├── manager.py                # PromptsManager — load from DB, to_config()
│   ├── agent.py                  # Agent — config resolution, variable application, execution
│   ├── variables.py              # {{variable}} substitution
│   ├── cache.py                  # Two-tier AgentCache (active 30min + warm 10min)
│   └── instructions/             # System instruction generation
│       ├── system_instructions.py
│       ├── content_blocks_manager.py
│       ├── pattern_parser.py
│       └── matrx_fetcher.py
│
├── db/                           # Database layer (matrx-orm)
│   ├── models.py                 # 17 auto-generated ORM models
│   ├── managers/                 # Auto-generated Base managers (DO NOT EDIT)
│   │   ├── cx_conversation.py, cx_message.py, cx_request.py
│   │   ├── cx_user_request.py, cx_tool_call.py, cx_media.py
│   │   ├── cx_agent_memory.py
│   │   ├── ai_model.py, ai_provider.py
│   │   ├── prompts.py, prompt_builtins.py, tools.py
│   │   ├── content_blocks.py, shortcut_categories.py
│   │   └── user_tables.py, table_data.py, table_fields.py
│   ├── custom/                   # Extended manager logic
│   │   └── ai_model_manager.py   # Model caching + name/ID resolution
│   ├── matrx_orm.yaml            # ORM schema config
│   └── generate.py               # Schema code generator
│
├── shared/                       # Shared utilities
│   ├── supabase_client.py        # get_supabase_client() — lazy singleton
│   ├── json_utils.py             # to_matrx_json helper
│   └── file_handler.py           # FileHandler placeholder
│
├── media/                        # Media handling
│   └── mime_utils.py             # MIME type detection
│
├── tests/                        # Test suite
│   ├── ai/                       # AI execution, error handling, translation tests
│   ├── openai/                   # OpenAI-specific integration tests
│   └── prompts/                  # Prompt loading, variable tests
│
├── .env                          # Environment variables (local, not committed)
├── .env.example                  # Template for required env vars
├── pyproject.toml                # Project metadata & dependencies
├── Makefile                      # Common dev commands
├── Dockerfile                    # Container build
└── entrypoint.sh                 # Docker entrypoint
```

---

## Architecture

### Core Patterns

**CxManagers (cxm)** — All database access for conversation tables goes through the singleton:
```python
from conversation import cxm

await cxm.conversation.create_cx_conversation(...)
await cxm.message.create_cx_message(...)
await cxm.tool_call.filter_cx_tool_calls(...)
await cxm.get_conversation_unified_config(conversation_id)
```

**ConversationResolver** — Cache-first config resolution:
```python
from conversation.conversation_resolver import ConversationResolver, AgentConfigResolver

# Continuing a conversation (AgentCache → DB fallback):
config = await ConversationResolver.from_conversation_id(conversation_id, user_input=...)

# Starting an agent:
config = await AgentConfigResolver.from_id(agent_id, variables=..., overrides=...)
```

**execute_ai_request()** — Public entry point for AI execution. Reads identity/scoping from AppContext:
```python
from client.ai_requests import execute_ai_request
completed = await execute_ai_request(config)
```

**run_ai_task()** — Shared streaming task for all router endpoints:
```python
from app.core.ai_task import run_ai_task
return create_streaming_response(ctx, run_ai_task, config, ...)
```

### Execution Flow

```
1. Router resolves UnifiedConfig (via ConversationResolver or AgentConfigResolver)
2. create_streaming_response() → run_ai_task(emitter, config)
3. execute_ai_request(config) — reads AppContext for user_id, conversation_id
   ├─ conversation.gate.ensure_conversation_exists()
   ├─ conversation.gate.create_pending_user_request()
   └─ execute_until_complete() loop:
       ├─ client.execute(request) → provider SDK call
       ├─ handle_finish_reason() → retry/continue/stop
       ├─ handle_tool_calls() → ToolExecutor pipeline
       │   ├─ guardrails check
       │   ├─ dispatch (local/mcp/agent)
       │   ├─ log to cx_tool_call via cxm
       │   └─ return results
       ├─ AIMatrixRequest.add_response() → append to messages
       └─ Loop until no more tool calls
4. _update_cache() → write config to AgentCache
5. persist_completed_request() → write all to DB via cxm
6. _emit_completion() → send result to client stream
```

### Two-Tier Agent Cache

- **Active cache** (30min TTL, 200 entries) — Full Agent objects from recent conversations
- **Warm cache** (10min TTL, 200 entries) — Pre-loaded via `/warm` endpoints
- Cache hits auto-promote from warm → active

### Streaming Architecture

- **NDJSON**: `application/x-ndjson` with line-delimited JSON
- Events: `status_update`, `chunk`, `thinking`, `tool_call`, `completion`, `error`, `end`

### Database Pattern

- **Two-phase writes**: Minimal INSERT at start (gate), full UPDATE after execution (persistence)
- **Fire-and-forget persistence**: Errors logged, never crash the caller
- **Conversation gate**: Ensures row exists before any writes

---

## API Endpoints

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/api/health` | Health check |
| GET | `/api/health/ready` | Kubernetes readiness |
| GET | `/api/health/live` | Kubernetes liveness |
| POST | `/api/ai/chat` | Streaming chat completions |
| POST | `/api/ai/agents/{agent_id}` | Start agent conversation |
| POST | `/api/ai/agents/{agent_id}/warm` | Pre-warm agent cache |
| POST | `/api/ai/cancel/{request_id}` | Request cancellation |
| POST | `/api/ai/conversations/{id}` | Continue conversation |
| POST | `/api/ai/conversations/{id}/warm` | Pre-warm conversation cache |

---

## Environment Variables

Required in `.env` (see `.env.example`):

```bash
# AI Provider API Keys
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=
TOGETHER_API_KEY=
CEREBRAS_API_KEY=
XAI_API_KEY=

# Supabase
SUPABASE_URL=
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=

# Supabase DB (used by matrx-orm)
SUPABASE_MATRIX_HOST=
SUPABASE_MATRIX_PORT=5432
SUPABASE_MATRIX_DATABASE_NAME=postgres
SUPABASE_MATRIX_USER=postgres
SUPABASE_MATRIX_PASSWORD=

# Sentry
MATRX_ENGINE_SENTRY_DSN=
```

---

## Code Standards

- **Python 3.13+** — Use modern syntax (match/case, type unions with `|`, etc.)
- **Full type hints** — Pydantic models for all boundaries, pyright standard mode
- **No docstrings required** — Self-documenting code via clear naming and types
- **Async throughout** — All I/O is non-blocking
- **ruff** for linting/formatting — Line length 100, target py313
- **No `TODO`, `FIXME`, or stubs** — Complete the work or flag it explicitly
- **Validate at boundaries only** — Trust internal code, validate user input + external APIs
- **Fire-and-forget persistence** — Never let DB writes crash the execution pipeline
- **Structured errors** — Use MatrxException hierarchy, never swallow errors silently

---

## Key Dependencies

- **matrx-orm** (v2.0.10) — Custom ORM, sourced from `../matrx-orm` (editable install)
- **matrx-utils** (v1.0.4+) — Shared utilities (vcprint, etc.)

Both are local workspace dependencies configured in `pyproject.toml` via `[tool.uv.sources]`.

---

## Database Schema (17 Tables)

### Core Conversation Tables (cx_ prefix)
- `cx_conversation` — Thread state, config, model, status
- `cx_message` — Messages with role, position, content (JSONB)
- `cx_user_request` — Per-user-request aggregated metrics
- `cx_request` — Per-iteration API call metrics
- `cx_tool_call` — Tool execution audit trail
- `cx_media` — Media attachments
- `cx_agent_memory` — Persistent agent memory with TTL

### Reference Tables
- `ai_model` — Model metadata, capabilities, provider FK
- `ai_provider` — Provider info
- `tools` — Tool definitions loaded into ToolRegistryV2
- `prompts` — User prompt templates
- `prompt_builtins` — System prompt templates
- `content_blocks` — Reusable content components
- `shortcut_categories` — UI organization
- `user_tables` / `table_data` / `table_fields` — Dynamic user data

### Auth
- `auth.users` — Supabase built-in auth schema (not managed by matrx-orm)
