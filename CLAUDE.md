# CLAUDE.md — matrx-ai

**Project:** Matrx AI Engine — Core FastAPI backend for AI orchestration
**Owner:** Arman (Armani) Sadeghi

---

## What This Is

A **Python FastAPI backend** that serves as the unified AI orchestration engine for all Matrx products. It integrates 7 AI providers, manages multi-turn conversations with persistent state, executes tools via a registry-based system, and streams responses via SSE/NDJSON.

This is **not** a frontend project. It is consumed by separate Next.js and React Native clients via REST/streaming APIs.

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
│   │   ├── exceptions.py         # MatrxException hierarchy + handlers
│   │   ├── middleware.py         # RequestContextMiddleware (request ID + timing)
│   │   ├── streaming.py          # SSE & NDJSON response helpers, keepalive
│   │   └── sentry.py             # Sentry init
│   ├── routers/                  # ⚠️ CURRENTLY PLACEHOLDER — see Task List
│   │   ├── health.py             # /api/health (real, but no DB checks)
│   │   ├── chat.py               # /api/ai/chat (MOCK — _mock_stream)
│   │   ├── agent.py              # /api/ai/agents/* (MOCK — _mock_agent_stream)
│   │   ├── conversation.py       # /api/ai/conversations/* (MOCK — _mock_conversation_stream)
│   │   └── tool.py               # /api/tools/test/* (PARTIAL — hardcoded registry)
│   └── models/                   # Pydantic request/response schemas
│       ├── chat.py               # ChatRequest, ChatResponse, StreamMode
│       ├── agent.py              # AgentRunRequest, AgentEvent, AgentStatus
│       ├── conversation.py       # ConversationContinueRequest
│       └── tool.py               # ToolCallRequest, ToolCallResult, ToolDefinition
│
├── client/                       # Unified AI client & execution engine (REAL)
│   ├── unified_client.py         # AIMatrixRequest, UnifiedAIClient, CompletedRequest
│   ├── ai_requests.py            # execute_until_complete() — main agentic loop
│   ├── translators.py            # Provider response → unified format
│   ├── usage.py                  # TokenUsage tracking
│   ├── timing.py                 # TimingUsage tracking
│   ├── tool_call_tracking.py     # ToolCallUsage tracking
│   ├── recovery_logic.py         # Finish reason handling + retry decisions
│   ├── errors.py                 # Error classification per provider
│   ├── thinking_config.py        # Extended thinking / reasoning config
│   ├── stream_protocol.py        # Stream parsing protocols
│   ├── cache.py                  # Response caching
│   └── system_agents.py          # System-level agent definitions
│
├── providers/                    # AI provider SDKs (ALL REAL)
│   ├── openai_api.py             # AsyncOpenAI (Responses API)
│   ├── anthropic_api.py          # AsyncAnthropic
│   ├── google_api.py             # google.genai
│   ├── groq_api.py               # AsyncGroq (OpenAI-compatible)
│   ├── cerebras_api.py           # AsyncCerebras
│   ├── together_api.py           # AsyncTogether
│   └── xai_api.py                # AsyncOpenAI → xAI endpoint
│
├── conversation/                 # Conversation persistence & lifecycle
│   ├── gate.py                   # ensure_conversation_exists, create_pending_user_request
│   ├── persistence.py            # persist_completed_request (central write path)
│   ├── rebuild.py                # Rebuild conversation from message history
│   ├── cx_conversation.py        # Conversation manager
│   ├── cx_message.py             # Message manager
│   ├── cx_media.py               # Media manager
│   ├── cx_user_request.py        # User request manager
│   ├── cx_request.py             # Per-iteration request manager
│   └── cx_agent_memory.py        # Agent memory manager
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
│   ├── emitter_protocol.py       # Streaming emitter protocol
│   ├── events.py                 # Event type definitions
│   └── console_emitter.py        # Dev/test console emitter
│
├── tools/                        # Tool system V2
│   ├── registry.py               # ToolRegistryV2 — loads from DB
│   ├── executor.py               # ToolExecutor — unified execution pipeline
│   ├── handle_tool_calls.py      # Integration with AI request loop
│   ├── guardrails.py             # 6-layer security (rate, cost, loop, recursion)
│   ├── models.py                 # ToolResult, ToolContext, ToolError
│   ├── logger.py                 # Two-phase DB logging (started → completed)
│   ├── streaming.py              # Tool event streaming
│   ├── lifecycle.py              # Tool lifecycle management
│   ├── arg_models/               # Pydantic input validators per tool
│   └── implementations/          # 14 tool implementations
│       ├── browser.py            # Playwright browser automation (REAL)
│       ├── code.py               # HTML storage, code fetching (REAL)
│       ├── database.py           # Sandboxed SQL via Supabase RPC (REAL)
│       ├── filesystem.py         # Workspace file ops (REAL)
│       ├── math.py               # Safe math eval (REAL)
│       ├── memory.py             # Persistent agent memory (REAL)
│       ├── news.py               # News API integration (REAL)
│       ├── questionnaire.py      # Interactive questionnaire (REAL)
│       ├── seo.py                # DataForSEO integration (REAL)
│       ├── shell.py              # Sandboxed shell execution (REAL)
│       ├── text.py               # Text analysis, regex (REAL)
│       ├── travel.py             # MOCK — demo/test only
│       ├── user_lists.py         # User list management (REAL)
│       ├── user_tables.py        # User table creation (REAL)
│       └── web.py                # Web search/read/research (REAL)
│
├── prompts/                      # Prompt management & templating
│   ├── manager.py                # PromptsManager — load from DB, to_config()
│   ├── session.py                # SimpleSession for stateful prompts
│   ├── agent.py                  # Agent prompt system
│   ├── variables.py              # {{variable}} substitution
│   ├── cache.py                  # Prompt caching
│   └── instructions/             # System instruction generation
│       ├── system_instructions.py
│       ├── content_blocks_manager.py
│       ├── pattern_parser.py
│       └── matrx_fetcher.py
│
├── db/                           # Database layer (matrx-orm)
│   ├── models.py                 # 17 auto-generated ORM models
│   ├── managers/                 # Auto-generated + custom managers
│   │   ├── ai_model.py, ai_provider.py
│   │   ├── cx_conversation.py, cx_message.py, cx_request.py
│   │   ├── cx_user_request.py, cx_tool_call.py, cx_media.py
│   │   ├── cx_agent_memory.py
│   │   ├── prompts.py, prompt_builtins.py, tools.py
│   │   ├── content_blocks.py, shortcut_categories.py
│   │   └── user_tables.py, table_data.py, table_fields.py
│   ├── custom/                   # Extended manager logic
│   │   └── ai_model_manager.py   # Model caching + name/ID resolution
│   ├── matrx_orm.yaml            # ORM schema config
│   └── generate.py               # Schema code generator
│
├── shared/                       # Shared utilities (PLACEHOLDER stubs)
│   ├── supabase_client.py        # get_supabase_client() — lazy singleton
│   ├── json_utils.py             # to_matrx_json helper
│   └── file_handler.py           # FileHandler placeholder
│
├── media/                        # Media handling
│   └── mime_utils.py             # MIME type detection
│
├── migrations/                   # Database migrations
│   └── 0001_baseline.py          # Initial schema (8 cx_ tables + ai_model)
│
├── tests/                        # Test suite (mostly manual/interactive)
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

### The Disconnect: Routers vs Engine

**This is the project's central problem.** Two layers exist independently:

1. **FastAPI Routers** (`app/routers/`) — Placeholder HTTP endpoints returning mock/hardcoded data
2. **AI Engine** (`client/`, `providers/`, `tools/`, `conversation/`) — Production-grade execution pipeline that actually works

The routers need to be wired to the engine. The engine's entry point is:
```python
from client.ai_requests import execute_until_complete
from client.unified_client import UnifiedAIClient, AIMatrixRequest
```

### Execution Flow (How the Engine Works)

```
1. AppContext set (user_id, conversation_id, emitter)
2. AIMatrixRequest created with UnifiedConfig
3. conversation.gate.ensure_conversation_exists()
4. conversation.gate.create_pending_user_request()
5. execute_until_complete() loop:
   ├─ client.execute(request) → provider SDK call
   ├─ handle_finish_reason() → retry/continue/stop
   ├─ handle_tool_calls() → ToolExecutor pipeline
   │   ├─ guardrails check
   │   ├─ dispatch (local/mcp/agent)
   │   ├─ log to cx_tool_call
   │   └─ return results
   ├─ AIMatrixRequest.add_response() → append to messages
   └─ Loop until no more tool calls
6. persist_completed_request() → write all to DB
```

### Streaming Architecture
- **SSE**: `text/event-stream` with 15s keepalive heartbeat
- **NDJSON**: `application/x-ndjson` with line-delimited JSON
- Both support: `chunk`, `thinking`, `tool_call`, `done`, `error` events

### Database Pattern
- **Two-phase writes**: Minimal INSERT at start, full UPDATE after execution
- **Fire-and-forget persistence**: Errors logged, never crash the caller
- **Conversation gate**: Ensures row exists before any writes

---

## API Endpoints

| Method | Path | Status | Purpose |
|--------|------|--------|---------|
| GET | `/api/health` | Real (partial) | Health check (no DB ping) |
| GET | `/api/health/ready` | Real | Kubernetes readiness |
| GET | `/api/health/live` | Real | Kubernetes liveness |
| POST | `/api/ai/chat` | **MOCK** | Streaming chat completions |
| POST | `/api/ai/agents/{agent_id}` | **MOCK** | Agent conversation |
| POST | `/api/ai/agents/{agent_id}/warm` | **TODO** | Cache warming |
| GET | `/api/ai/agents/{agent_id}` | **MOCK** | Agent status/metadata |
| POST | `/api/ai/cancel/{request_id}` | **TODO** | Request cancellation |
| POST | `/api/ai/conversations/{id}` | **MOCK** | Continue conversation |
| POST | `/api/ai/conversations/{id}/warm` | **TODO** | Cache warming |
| GET | `/api/tools/test/list` | Real (hardcoded) | List tools |
| GET | `/api/tools/test/{name}` | Real (hardcoded) | Get tool definition |
| POST | `/api/tools/test/execute` | Partial | Execute tool (search is stub) |

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
