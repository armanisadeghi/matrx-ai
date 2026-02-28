# `orchestrator` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `orchestrator` |
| Last generated | 2026-02-28 13:39 |
| Output file | `orchestrator/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py orchestrator --mode signatures \
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

> Auto-generated. 6 files across 1 directories.

```
orchestrator/
├── MODULE_README.md
├── __init__.py
├── executor.py
├── recovery_logic.py
├── requests.py
├── tracking.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: orchestrator/__init__.py  [python]



---
Filepath: orchestrator/recovery_logic.py  [python]

  def handle_finish_reason(response: UnifiedResponse, request: AIMatrixRequest, retry_attempt: int, max_retries: int, debug: bool = False) -> Literal['continue', 'retry', 'stop']


---
Filepath: orchestrator/executor.py  [python]

  LOCAL_DEBUG = False
  async def execute_ai_request(config: UnifiedConfig, max_iterations: int = 20, max_retries_per_iteration: int = 2, metadata: dict[str, Any] | None = None) -> CompletedRequest
  async def handle_tool_calls(response: UnifiedResponse, request: AIMatrixRequest, iteration: int) -> tuple[list | None, ToolCallUsage | None, list[TokenUsage]]
  async def _finalize_and_persist(current_request: AIMatrixRequest, iteration: int, final_response: UnifiedResponse, metadata: dict[str, Any], trigger_position: int, pre_execution_message_count: int, conversation_id: str | None = None) -> CompletedRequest
  async def execute_until_complete(initial_request: AIMatrixRequest, client: UnifiedAIClient, max_iterations: int = 20, max_retries_per_iteration: int = 2) -> CompletedRequest


---
Filepath: orchestrator/requests.py  [python]

  class AIMatrixRequest:
      def __post_init__(self)
      def user_id(self) -> str
      def emitter(self) -> Emitter | None
      def total_usage(self) -> AggregatedUsage
      def timing_stats(self) -> dict[str, Any]
      def tool_call_stats(self) -> dict[str, Any]
      def add_usage(self, usage: TokenUsage | None) -> None
      def add_timing(self, timing: TimingUsage | None) -> None
      def add_tool_calls(self, tool_calls: ToolCallUsage | None) -> None
      def from_dict(cls, data: dict[str, Any], emitter: Emitter | None = None) -> 'AIMatrixRequest'
      def add_response(cls, original_request: 'AIMatrixRequest', response: UnifiedResponse, tool_results: list[ToolResultContent] | None = None) -> 'AIMatrixRequest'
      def to_dict(self) -> dict[str, Any]
  class CompletedRequest:
      def conversation_id(self) -> str
      def user_id(self) -> str
      def messages(self) -> MessageList
      def to_dict(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]


---
Filepath: orchestrator/tracking.py  [python]

  class ToolCallUsage:
      def aggregate(tool_call_list: list['ToolCallUsage']) -> dict[str, Any]
  class TimingUsage:
      def total_duration(self) -> float
      def processing_duration(self) -> float
      def aggregate(timings: list['TimingUsage']) -> dict[str, Any]
```
<!-- /AUTO:signatures -->

<!-- AUTO:call_graph -->
## Call Graph

> Auto-generated. Scoped to: `handle_tool_calls, executor, registry, guardrails`.
> Shows which functions call which. `async` prefix = caller is an async function.
> Method calls shown as `receiver.method()`. Private methods (`_`) excluded by default.

### Call graph: orchestrator.executor

```
async orchestrator.executor.execute_ai_request → orchestrator.executor.get_app_context() (line 67)
  async orchestrator.executor.execute_ai_request → orchestrator.executor.AIMatrixRequest() (line 73)
  async orchestrator.executor.execute_ai_request → orchestrator.executor.execute_until_complete(request, UnifiedAIClient(), max_iterations, max_retries_per_iteration) (line 81)
  async orchestrator.executor.execute_ai_request → orchestrator.executor.UnifiedAIClient() (line 83)
  async orchestrator.executor.handle_tool_calls → tool_calls.append(content) (line 106)
  async orchestrator.executor.handle_tool_calls → orchestrator.executor.handle_tool_calls_v2(raw_calls) (line 122)
  async orchestrator.executor.handle_tool_calls → orchestrator.executor.ToolResultContent() (line 127)
  async orchestrator.executor.handle_tool_calls → cr.get('is_error', False) (line 139)
  async orchestrator.executor.handle_tool_calls → orchestrator.executor.ToolCallUsage() (line 144)
  async orchestrator.executor._finalize_and_persist → orchestrator.executor.CompletedRequest() (line 188)
  async orchestrator.executor._finalize_and_persist → metadata.get('status') (line 207)
  async orchestrator.executor._finalize_and_persist → orchestrator.executor.update_conversation_status(conv_id, 'error') (line 209)
  async orchestrator.executor._finalize_and_persist → orchestrator.executor.update_user_request_status(req_id, 'failed') (line 211)
  async orchestrator.executor._finalize_and_persist → metadata.get('error') (line 214)
  async orchestrator.executor._finalize_and_persist → orchestrator.executor.persist_completed_request(completed) (line 219)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.get_app_context() (line 254)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.ensure_conversation_exists() (line 263)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.create_pending_user_request() (line 269)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.TimingUsage() (line 284)
  async orchestrator.executor.execute_until_complete → time.time() (line 284)
  async orchestrator.executor.execute_until_complete → time.time() (line 300)
  async orchestrator.executor.execute_until_complete → client.execute(current_request) (line 301)
  async orchestrator.executor.execute_until_complete → time.time() (line 302)
  async orchestrator.executor.execute_until_complete → current_request.add_usage(api_response.usage) (line 310)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.handle_finish_reason(api_response, current_request, retry_attempt, max_retries_per_iteration, debug) (line 313)
  async orchestrator.executor.execute_until_complete → ...send_status_update() (line 327)
  async orchestrator.executor.execute_until_complete → orchestrator.executor._finalize_and_persist() (line 343)
  async orchestrator.executor.execute_until_complete → ...lower() (line 378)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.classify_provider_error(provider, e) (line 386)
  async orchestrator.executor.execute_until_complete → error_info.get_backoff_delay(retry_attempt) (line 393)
  async orchestrator.executor.execute_until_complete → ...send_status_update() (line 406)
  async orchestrator.executor.execute_until_complete → asyncio.sleep(backoff_delay) (line 418)
  async orchestrator.executor.execute_until_complete → ...send_error() (line 435)
  async orchestrator.executor.execute_until_complete → time.time() (line 456)
  async orchestrator.executor.execute_until_complete → current_request.add_timing(current_timing) (line 457)
  async orchestrator.executor.execute_until_complete → orchestrator.executor._finalize_and_persist() (line 467)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.UnifiedResponse() (line 470)
  async orchestrator.executor.execute_until_complete → time.time() (line 485)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.handle_tool_calls(response, current_request, iteration) (line 486)
  async orchestrator.executor.execute_until_complete → time.time() (line 489)
  async orchestrator.executor.execute_until_complete → current_request.add_usage(child_usage) (line 493)
  async orchestrator.executor.execute_until_complete → time.time() (line 496)
  async orchestrator.executor.execute_until_complete → current_request.add_timing(current_timing) (line 497)
  async orchestrator.executor.execute_until_complete → current_request.add_tool_calls(tool_call_usage) (line 500)
  async orchestrator.executor.execute_until_complete → AIMatrixRequest.add_response() (line 503)
  async orchestrator.executor.execute_until_complete → orchestrator.executor._finalize_and_persist() (line 536)
  async orchestrator.executor.execute_until_complete → time.time() (line 561)
  async orchestrator.executor.execute_until_complete → current_request.add_timing(current_timing) (line 562)
  async orchestrator.executor.execute_until_complete → traceback.print_exc() (line 569)
  async orchestrator.executor.execute_until_complete → orchestrator.executor._finalize_and_persist() (line 589)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.UnifiedResponse() (line 592)
  async orchestrator.executor.execute_until_complete → orchestrator.executor._finalize_and_persist() (line 631)
  async orchestrator.executor.execute_until_complete → orchestrator.executor.UnifiedResponse() (line 634)
```
<!-- /AUTO:call_graph -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_utils
**Internal modules:** config, config.finish_reason, config.unified_config, config.usage_config, context.app_context, context.emitter_protocol, db.custom, providers, providers.errors, tools.handle_tool_calls
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "orchestrator",
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
