# `context` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `context` |
| Last generated | 2026-02-28 13:39 |
| Output file | `context/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py context --mode signatures \
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

> Auto-generated. 7 files across 1 directories.

```
context/
├── MODULE_README.md
├── __init__.py
├── app_context.py
├── console_emitter.py
├── emitter_protocol.py
├── events.py
├── stream_emitter.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: context/__init__.py  [python]



---
Filepath: context/events.py  [python]

  ToolEventType = Literal['tool_started', 'tool_progress', 'tool_step', 'tool_result_preview', 'tool_completed', 'tool_error']
  class EventType(StrEnum):
  class ChunkPayload(BaseModel):
      # fields: text: str
  class StatusUpdatePayload(BaseModel):
      # fields: status: str, system_message: str | None = None, user_message: str | None = None, metadata: dict[str, Any] | None = None
  class DataPayload(BaseModel):
  class CompletionPayload(BaseModel):
      # fields: status: Literal['complete', 'failed', 'max_iterations_exceeded'] = 'complete', output: Any = None, iterations: int | None = None, total_usage: dict[str, Any] | None = None, timing_stats: dict[str, Any] | None = None, tool_call_stats: dict[str, Any] | None = None, finish_reason: str | None = None, metadata: dict[str, Any] | None = None
  class ErrorPayload(BaseModel):
      # fields: error_type: str, message: str, user_message: str = 'Sorry. An error occurred.', code: str | None = None, details: dict[str, Any] | None = None
  class ToolEventPayload(BaseModel):
      # fields: event: ToolEventType, call_id: str, tool_name: str, timestamp: float = time(), message: str | None = None, show_spinner: bool = True, data: dict[str, Any] = dict()
  class BrokerPayload(BaseModel):
      # fields: broker_id: str, value: Any, source: str | None = None, source_id: str | None = None
  class HeartbeatPayload(BaseModel):
      # fields: timestamp: float = time()
  class EndPayload(BaseModel):
      # fields: reason: str = 'complete'
  class StreamEvent(BaseModel):
      # fields: event: EventType, data: dict[str, Any]
      def to_jsonl(self) -> str
  class InvalidEventError(Exception):
  def build_event(event_type: EventType, payload: BaseModel) -> StreamEvent
  def validate_event_dict(event_name: str, data: dict[str, Any]) -> StreamEvent


---
Filepath: context/stream_emitter.py  [python]

  class StreamEmitter:
      def __init__(self, debug: bool = False, heartbeat_interval: float = 5.0)
      def set_task(self, task: asyncio.Task[None]) -> None
      def start_heartbeat(self) -> None
      def _stop_heartbeat(self) -> None
      async def _heartbeat_loop(self) -> None
      async def generate(self)
      def _serialize(self, data: Any) -> Any
      async def _emit_event(self, event: StreamEvent) -> None
      async def _emit_raw(self, event_type: EventType, data: dict[str, Any]) -> None
      async def send_chunk(self, text: str) -> None
      async def send_status_update(self, status: str, system_message: str | None = None, user_message: str | None = None, metadata: dict[str, Any] | None = None) -> None
      async def send_data(self, data: Any) -> None
      async def send_completion(self, payload: CompletionPayload) -> None
      async def send_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None
      async def send_tool_event(self, event_data: ToolEventPayload | dict[str, Any]) -> None
      async def send_broker(self, broker: BrokerPayload) -> None
      async def send_end(self, reason: str = 'complete') -> None
      async def send_cancelled(self) -> None
      async def fatal_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None


---
Filepath: context/console_emitter.py  [python]

  TEMP_DIR = Path(__file__).resolve().parent.parent.parent.parent / 'temp'
  DEFAULT_SAVE_DIR = TEMP_DIR / 'emitter_responses'
  class ConsoleEmitter:
      def __init__(self, label: str = 'console', debug: bool = False, accumulate: bool = True)
      async def send_chunk(self, text: str) -> None
      async def send_status_update(self, status: str, system_message: str | None = None, user_message: str | None = None, metadata: dict[str, Any] | None = None) -> None
      async def send_data(self, data: Any) -> None
      async def send_completion(self, payload: CompletionPayload) -> None
      async def send_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None
      async def send_tool_event(self, event_data: ToolEventPayload | dict[str, Any]) -> None
      async def send_broker(self, broker: BrokerPayload) -> None
      async def send_end(self, reason: str = 'complete') -> None
      async def send_cancelled(self) -> None
      async def fatal_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None
      async def _save_accumulated(self) -> None


---
Filepath: context/app_context.py  [python]

  class AppContext:
      def extend(self, **kwargs: Any) -> AppContext
      def fork_for_child_agent(self, new_conversation_id: str) -> AppContext
  def set_app_context(ctx: AppContext) -> Token
  def get_app_context() -> AppContext
  def try_get_app_context() -> AppContext | None
  def clear_app_context(token: Token) -> None
  def context_dep(request: Request) -> AppContext


---
Filepath: context/emitter_protocol.py  [python]

  class Emitter(Protocol):
      async def send_chunk(self, text: str) -> None
      async def send_status_update(self, status: str, system_message: str | None = None, user_message: str | None = None, metadata: dict[str, Any] | None = None) -> None
      async def send_data(self, data: Any) -> None
      async def send_completion(self, payload: CompletionPayload) -> None
      async def send_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None
      async def send_tool_event(self, event_data: ToolEventPayload) -> None
      async def send_broker(self, broker: BrokerPayload) -> None
      async def send_end(self, reason: str = 'complete') -> None
      async def send_cancelled(self) -> None
      async def fatal_error(self, error_type: str, message: str, user_message: str | None = None, code: str | None = None, details: dict[str, Any] | None = None) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-generated. Shows which files import and call the listed entry points.
> Update `ENTRY_POINTS` in `generate_readme.py` to control which functions are tracked.

| Caller | Calls |
|--------|-------|
| `orchestrator/executor.py` | `handle_tool_calls_v2()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** fastapi, matrx_utils, pydantic
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "context",
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
