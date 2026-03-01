# `app.core` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `app/core` |
| Last generated | 2026-03-01 00:09 |
| Output file | `app/core/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py app/core --mode signatures
```

**To add permanent notes:** Write anywhere outside the `<!-- AUTO:... -->` blocks.
<!-- /AUTO:meta -->

<!-- HUMAN-EDITABLE: This section is yours. Agents & Humans can edit this section freely — it will not be overwritten. -->

## Architecture

> **Fill this in.** Describe the execution flow and layer map for this module.
> See `utils/code_context/MODULE_README_SPEC.md` for the recommended format.
>
> Suggested structure:
>
> ### Layers
> | File | Role |
> |------|------|
> | `entry.py` | Public entry point — receives requests, returns results |
> | `engine.py` | Core dispatch logic |
> | `models.py` | Shared data types |
>
> ### Call Flow (happy path)
> ```
> entry_function() → engine.dispatch() → implementation()
> ```


<!-- AUTO:tree -->
## Directory Tree

> Auto-generated. 9 files across 1 directories.

```
app/core/
├── MODULE_README.md
├── __init__.py
├── ai_task.py
├── cancellation.py
├── exceptions.py
├── middleware.py
├── response.py
├── sentry.py
├── streaming.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: app/core/__init__.py  [python]



---
Filepath: app/core/exceptions.py  [python]

  class MatrxException(Exception):
      def __init__(self, message: str, status_code: int = 500, detail: dict | None = None) -> None
  class ProviderError(MatrxException):
      def __init__(self, provider: str, message: str, detail: dict | None = None) -> None
  class AgentNotFoundError(MatrxException):
      def __init__(self, agent_id: str) -> None
  class ToolNotFoundError(MatrxException):
      def __init__(self, tool_name: str) -> None
  class StreamingError(MatrxException):
      def __init__(self, message: str) -> None
  async def matrx_exception_handler(request: Request, exc: MatrxException) -> ORJSONResponse
  async def unhandled_exception_handler(request: Request, exc: Exception) -> ORJSONResponse


---
Filepath: app/core/cancellation.py  [python]

  class CancellationRegistry:
      def __init__(self, ttl_seconds: float = 60.0)
      def get_instance(cls) -> CancellationRegistry
      async def cancel(self, request_id: str) -> None
      def is_cancelled(self, request_id: str) -> bool
      async def cleanup_expired(self) -> int


---
Filepath: app/core/response.py  [python]

  def create_streaming_response(ctx: AppContext, task_fn: Callable[..., Awaitable[None]], *task_args: Any, initial_message: str = 'Connecting...', debug_label: str = 'stream') -> StreamingResponse
  async def _stream()
  async def _run_with_error_handling()


---
Filepath: app/core/sentry.py  [python]

  def init_sentry() -> None
  def _traces_sampler(sampling_context: dict) -> float


---
Filepath: app/core/streaming.py  [python]

  async def sse_generator(source: AsyncGenerator[dict[str, Any]], keepalive_interval: float = 15.0) -> AsyncGenerator[dict[str, Any]]
  def make_sse_response(generator: AsyncGenerator[dict[str, Any]], keepalive_interval: float = 15.0) -> EventSourceResponse
  async def ndjson_generator(source: AsyncIterator[dict[str, Any]]) -> AsyncGenerator[bytes]
  def make_ndjson_response(source: AsyncIterator[dict[str, Any]]) -> StreamingResponse
  async def text_chunks_to_sse(source: AsyncGenerator[str], event: str = 'chunk', done_event: str = 'done') -> AsyncGenerator[dict[str, Any]]
  async def _keepalive() -> None
  async def _drain_source() -> None


---
Filepath: app/core/middleware.py  [python]

  class RequestContextMiddleware:
      def __init__(self, app: ASGIApp) -> None
      async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None
  async def send_with_capture(message: Any) -> None


---
Filepath: app/core/ai_task.py  [python]

  async def run_ai_task(emitter: StreamEmitter, config: UnifiedConfig, max_iterations: int = 20, max_retries_per_iteration: int = 2) -> None
  def _update_cache(completed: CompletedRequest) -> None
  async def _emit_completion(emitter: StreamEmitter, completed: CompletedRequest) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `app/routers/agent.py` | `CancellationRegistry()` |
| `app/main.py` | `MatrxException()` |
| `app/main.py` | `RequestContextMiddleware()` |
| `app/routers/tool.py` | `ToolNotFoundError()` |
| `app/routers/agent.py` | `create_streaming_response()` |
| `app/routers/chat.py` | `create_streaming_response()` |
| `app/routers/conversation.py` | `create_streaming_response()` |
| `app/main.py` | `init_sentry()` |
| `app/main.py` | `matrx_exception_handler()` |
| `app/routers/agent.py` | `run_ai_task()` |
| `app/routers/chat.py` | `run_ai_task()` |
| `app/routers/conversation.py` | `run_ai_task()` |
| `app/main.py` | `unhandled_exception_handler()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** fastapi, matrx_utils, orjson, sentry_sdk, sse_starlette, starlette
**Internal modules:** agents.cache, agents.definition, app.config, config.unified_config, context.app_context, context.emitter_protocol, context.events, context.stream_emitter, orchestrator, orchestrator.requests
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "app/core",
  "mode": "signatures",
  "scope": null,
  "project_noise": null,
  "include_call_graph": false,
  "entry_points": null,
  "call_graph_exclude": [
    "tests"
  ]
}
```
<!-- /AUTO:config -->
