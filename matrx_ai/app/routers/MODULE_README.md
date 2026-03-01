# `app.routers` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `app/routers` |
| Last generated | 2026-03-01 00:10 |
| Output file | `app/routers/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py app/routers --mode signatures
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
app/routers/
├── MODULE_README.md
├── __init__.py
├── agent.py
├── chat.py
├── conversation.py
├── health.py
├── tool.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
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
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `app/main.py` | `chat()` |
| `app/main.py` | `health()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** fastapi, matrx_utils
**Internal modules:** agents.resolver, app.config, app.core, app.models, config.unified_config, context.app_context
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "app/routers",
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
