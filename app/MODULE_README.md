# `app` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `app` |
| Last generated | 2026-02-28 13:39 |
| Output file | `app/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py app --mode signatures \
        --call-graph-scope handle_tool_calls,executor,registry,guardrails
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

> Auto-generated. 28 files across 6 directories.

```
app/
├── MODULE_README.md
├── __init__.py
├── config.py
├── core/
│   ├── __init__.py
│   ├── ai_task.py
│   ├── cancellation.py
│   ├── exceptions.py
│   ├── middleware.py
│   ├── response.py
│   ├── sentry.py
│   ├── streaming.py
├── dependencies/
│   ├── __init__.py
│   ├── auth.py
├── main.py
├── middleware/
│   ├── __init__.py
│   ├── auth.py
├── models/
│   ├── __init__.py
│   ├── agent.py
│   ├── chat.py
│   ├── conversation.py
│   ├── health.py
│   ├── tool.py
├── routers/
│   ├── __init__.py
│   ├── agent.py
│   ├── chat.py
│   ├── conversation.py
│   ├── health.py
│   ├── tool.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: app/config.py  [python]

  class Settings(BaseSettings):
  def get_settings() -> Settings


---
Filepath: app/__init__.py  [python]



---
Filepath: app/main.py  [python]

  async def lifespan(app: FastAPI) -> AsyncGenerator[None]
  def create_app() -> FastAPI
  def custom_openapi()


---
Filepath: app/dependencies/__init__.py  [python]



---
Filepath: app/dependencies/auth.py  [python]

  async def require_guest_or_above(request: Request) -> None
  async def require_authenticated(request: Request) -> None
  async def require_admin(request: Request) -> None


---
Filepath: app/middleware/__init__.py  [python]



---
Filepath: app/middleware/auth.py  [python]

  class AuthMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response
  def _build_context(request: Request) -> AppContext
  def _validate_token(authorization: str, fingerprint_id: str | None, ctx: AppContext) -> AppContext | None


---
Filepath: app/routers/__init__.py  [python]



---
Filepath: app/routers/health.py  [python]

  async def health() -> HealthStatus
  async def health_detailed() -> HealthStatus
  async def readiness() -> ORJSONResponse
  async def liveness() -> ORJSONResponse
  async def _run_checks() -> dict[str, str]
  async def _event_loop_check() -> str


---
Filepath: app/routers/tool.py  [python]

  async def list_tools() -> list[ToolDefinition]
  async def get_tool(name: str = Path(..., description='Tool name')) -> ToolDefinition
  async def execute_tool(body: ToolCallRequest) -> ToolCallResult
  async def _dispatch(tool_name: str, arguments: dict[str, Any]) -> Any


---
Filepath: app/routers/chat.py  [python]

  def _build_unified_config(request: ChatRequest) -> tuple[UnifiedConfig, set]
  async def chat(request: ChatRequest, ctx: AppContext = Depends(context_dep)) -> Any


---
Filepath: app/routers/conversation.py  [python]

  async def continue_conversation(conversation_id: str, request: ConversationContinueRequest, ctx: AppContext = Depends(context_dep)) -> Any
  async def warm_conversation(conversation_id: str)


---
Filepath: app/routers/agent.py  [python]

  async def start_agent(agent_id: str, request: AgentStartRequest, ctx: AppContext = Depends(context_dep)) -> Any
  async def warm_agent(agent_id: str)
  async def cancel_request(request_id: str, ctx: AppContext = Depends(context_dep))


---
Filepath: app/models/__init__.py  [python]



---
Filepath: app/models/health.py  [python]

  class HealthStatus(BaseModel):
      # fields: status: str, version: str, environment: str, checks: dict[str, Any] = {}


---
Filepath: app/models/tool.py  [python]

  class ToolParameter(BaseModel):
      # fields: name: str, type: str, description: str, required: bool = True, default: Any = None
  class ToolDefinition(BaseModel):
      # fields: name: str, description: str, parameters: list[ToolParameter] = list(), metadata: dict[str, Any] = dict()
  class ToolCallRequest(BaseModel):
      # fields: tool_name: str, arguments: dict[str, Any] = dict(), call_id: str | None = None, metadata: dict[str, Any] = dict()
  class ToolCallResult(BaseModel):
      # fields: call_id: str | None = None, tool_name: str, result: Any, error: str | None = None, elapsed_ms: float | None = None


---
Filepath: app/models/chat.py  [python]

  class ChatRequest(BaseModel):
      # fields: ai_model_id: str, messages: list[dict[str, Any]], conversation_id: str | None = None, max_iterations: int = 20, max_retries_per_iteration: int = 2, stream: bool = True, debug: bool = False, system_instruction: str | None = None, max_output_tokens: int | None = None, temperature: float | None = None, top_p: float | None = None, top_k: int | None = None, tools: list[str] | None = None, tool_choice: Any | None = None, parallel_tool_calls: bool = True, reasoning_effort: str | None = None, reasoning_summary: str | None = None, thinking_level: str | None = None, include_thoughts: bool | None = None, thinking_budget: int | None = None, response_format: dict[str, Any] | None = None, stop_sequences: list[str] | None = None, internal_web_search: bool | None = None, internal_url_context: bool | None = None, size: str | None = None, quality: str | None = None, count: int = 1, audio_voice: str | None = None, audio_format: str | None = None, seconds: str | None = None, fps: int | None = None, steps: int | None = None, seed: int | None = None, guidance_scale: int | None = None, output_quality: int | None = None, negative_prompt: str | None = None, output_format: str | None = None, width: int | None = None, height: int | None = None, frame_images: list | None = None, reference_images: list | None = None, disable_safety_checker: bool | None = None, metadata: dict[str, Any] | None = None, store: bool = True
      def coerce_response_format(cls, v: Any) -> Any


---
Filepath: app/models/conversation.py  [python]

  class ConversationContinueRequest(BaseModel):
      # fields: user_input: str | list[dict[str, Any]], config_overrides: dict[str, Any] | None = None, stream: bool = True, debug: bool = False


---
Filepath: app/models/agent.py  [python]

  class AgentStatus(StrEnum):
  class AgentStartRequest(BaseModel):
      # fields: user_input: str | list[dict[str, Any]] | None = None, variables: dict[str, Any] | None = None, config_overrides: dict[str, Any] | None = None, stream: bool = True, debug: bool = False
  class AgentInfo(BaseModel):
      # fields: agent_id: str, status: AgentStatus, created_at: str, metadata: dict[str, Any] = dict()


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

  class RequestContextMiddleware(BaseHTTPMiddleware):
      async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response


---
Filepath: app/core/ai_task.py  [python]

  async def run_ai_task(emitter: StreamEmitter, config: UnifiedConfig, max_iterations: int = 20, max_retries_per_iteration: int = 2) -> None
  def _update_cache(completed: CompletedRequest) -> None
  async def _emit_completion(emitter: StreamEmitter, completed: CompletedRequest) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** fastapi, jwt, matrx_utils, orjson, pydantic, pydantic_settings, sentry_sdk, sse_starlette, starlette, uvicorn, uvloop
**Internal modules:** agents.cache, agents.definition, agents.resolver, config.unified_config, context.app_context, context.emitter_protocol, context.events, context.stream_emitter, orchestrator, orchestrator.requests, tools.handle_tool_calls
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "app",
  "mode": "signatures",
  "scope": [
    "handle_tool_calls",
    "executor",
    "registry",
    "guardrails"
  ],
  "project_noise": null,
  "include_call_graph": true,
  "entry_points": [
    "handle_tool_calls_v2",
    "initialize_tool_system",
    "initialize_tool_system_sync",
    "cleanup_conversation"
  ],
  "call_graph_exclude": null
}
```
<!-- /AUTO:config -->
