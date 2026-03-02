# Matrx Service Core Template

Reference template for all Matrx Python/FastAPI microservices. Copy this
directory, rename the package, and you have a fully wired service with
identical interfaces for auth, context, streaming, and service-to-service calls.

## Quick Start

### 1. Copy and rename

```bash
cp -r templates/matrx-service-core/ ../matrx-my-service/
cd ../matrx-my-service

# Rename the package directory
mv matrx_service/ matrx_my_service/

# Find and replace everywhere
grep -rl 'matrx_service' . | xargs sed -i 's/matrx_service/matrx_my_service/g'

# Update the CLI entry point name in pyproject.toml
# [project.scripts]
# matrx-my-service = "matrx_my_service.app.main:start"
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env — at minimum set SUPABASE_JWT_SECRET and ADMIN_API_TOKEN
```

### 3. Install and run

```bash
uv sync
make dev          # hot-reload dev server on :8000
make run          # production mode
```

---

## Architecture

Every Matrx microservice shares exactly this infrastructure:

```
Inbound request
    ↓
CORSMiddleware          # outermost — handles OPTIONS preflight
    ↓
RequestContextMiddleware # assigns request ID, logs timing
    ↓
AuthMiddleware          # validates JWT / admin token / fingerprint
                        # → builds AppContext, sets ContextVar
    ↓
Route Handler           # uses Depends(context_dep) to get AppContext
    ↓
create_streaming_response(ctx, task_fn, ...)
    ↓
StreamEmitter.generate() → NDJSON lines to client
```

---

## Core Components

### AppContext (`context/app_context.py`)

Request-scoped dataclass stored in a `ContextVar`. Set once by `AuthMiddleware`,
readable anywhere via `get_app_context()`. Use `ctx.extend()` in route handlers
to set route-specific fields.

```python
from matrx_service.context.app_context import get_app_context

def some_deep_function():
    ctx = get_app_context()
    print(ctx.user_id, ctx.conversation_id)
```

### Event System (`context/events.py`)

Identical across all services. All payloads are Pydantic models, validated on emit.

| EventType      | Payload               | When to use |
|----------------|-----------------------|-------------|
| `chunk`        | `ChunkPayload`        | Streaming LLM text tokens |
| `status_update`| `StatusUpdatePayload` | Progress updates for UI |
| `data`         | `DataPayload`         | Arbitrary structured data |
| `completion`   | `CompletionPayload`   | Final result, once per request |
| `error`        | `ErrorPayload`        | Structured errors |
| `tool_event`   | `ToolEventPayload`    | Tool lifecycle (started/completed/error) |
| `broker`       | `BrokerPayload`       | Cross-service value delivery |
| `heartbeat`    | `HeartbeatPayload`    | Keepalive, auto-sent |
| `end`          | `EndPayload`          | Stream termination signal |

### Emitter (`context/emitter_protocol.py`)

Runtime-checkable `Protocol` that both `StreamEmitter` (production) and
`ConsoleEmitter` (dev/test) satisfy. Always type against `Emitter`, never
against a concrete class.

```python
from matrx_service.context.emitter_protocol import Emitter

async def my_task(emitter: Emitter, data: dict) -> None:
    await emitter.send_status_update("processing", system_message="Working...")
    # ... do work ...
    await emitter.send_data({"result": data})
    await emitter.send_completion(CompletionPayload(status="complete", output=data))
    await emitter.send_end()
```

### Streaming Response (`app/core/response.py`)

```python
from matrx_service.app.core.response import create_streaming_response
from matrx_service.context.app_context import context_dep, AppContext

@router.post("/my-endpoint")
async def my_endpoint(
    request: MyRequest,
    ctx: AppContext = Depends(context_dep),
):
    ctx.extend(conversation_id=request.conversation_id)
    return create_streaming_response(
        ctx,
        my_task_fn,        # async def my_task_fn(emitter, *args)
        request.payload,   # forwarded as *task_args
        initial_message="Processing...",
        debug_label="MyTask",
    )
```

### Service Client (`client/service_client.py`)

Outbound HTTP client that automatically propagates `AppContext` via headers so
downstream services reconstruct the same context.

```python
from matrx_service.client.service_client import ServiceClient

# One-shot
client = ServiceClient(base_url="http://matrx-ai:8000")
response = await client.post_json("/api/ai/chat", {"messages": [...]})

# Using env var (MATRX_AI_URL)
client = ServiceClient.for_service("matrx_ai")

# Stream NDJSON from another service
async with ServiceClient(base_url="http://matrx-ai:8000") as client:
    async for event in client.stream_ndjson("/api/ai/chat", json={...}):
        if event.get("event") == "chunk":
            print(event["data"]["text"], end="")
```

### Auth (`app/middleware/auth.py`)

Three auth tiers, resolved in order:

| Tier | Header | `auth_type` | `is_authenticated` |
|------|--------|------------|---------------------|
| JWT token | `Authorization: Bearer <jwt>` | `token` | `True` |
| Admin token | `Authorization: Bearer <admin_token>` | `token` | `True` + `is_admin=True` |
| Fingerprint | `X-Fingerprint-ID: <id>` | `fingerprint` | `False` |
| None | — | `anonymous` | `False` |

Route gating via FastAPI dependencies:

```python
from matrx_service.app.dependencies.auth import (
    require_guest_or_above,   # fingerprint or token
    require_authenticated,    # JWT required
    require_admin,            # JWT + admin flag
)
```

### Exception Hierarchy (`app/core/exceptions.py`)

```
MatrxException (base, status=500)
├── NotFoundError (404)
├── ProviderError (502)
├── AgentNotFoundError (404)
├── ToolNotFoundError (404)
├── StreamingError (500)
├── AuthorizationError (401)
└── ForbiddenError (403)
```

All exceptions produce this response shape:
```json
{
    "error": "human-readable message",
    "detail": { "structured": "context" },
    "path": "/api/..."
}
```

---

## Dev Commands

```bash
make install    # uv sync
make dev        # hot-reload on :8000
make run        # production
make lint       # ruff check
make fmt        # ruff format
make typecheck  # pyright
make test       # pytest -v
```

---

## Environment Variables

See `.env.example` for the full list. Required to run:

| Variable | Purpose |
|----------|---------|
| `SUPABASE_JWT_SECRET` | Validates Supabase-issued JWTs |
| `ADMIN_API_TOKEN` | Static admin token for internal/dev use |
| `SENTRY_DSN` | Error tracking (optional, disabled if unset) |

---

## Renaming Checklist

After copying the template:

- [ ] `mv matrx_service/ <your_package_name>/`
- [ ] Global replace `matrx_service` → `<your_package_name>`
- [ ] `pyproject.toml`: `name`, `packages`, `[project.scripts]`
- [ ] `Makefile`: `dev` target uvicorn path, `run` target script name
- [ ] `entrypoint.sh`: uvicorn module path
- [ ] `README.md`: service description
- [ ] `app/config.py`: `app_name` default, add service-specific settings
- [ ] `app/main.py`: add service-specific startup logic and routers
- [ ] `app/routers/health.py`: add real component checks to `_run_checks()`
