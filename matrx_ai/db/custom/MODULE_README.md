# `db.custom` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `db/custom` |
| Last generated | 2026-03-01 00:10 |
| Output file | `db/custom/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`db/custom/ai_models/MODULE_README.md`](db/custom/ai_models/MODULE_README.md) | last generated 2026-03-01 00:10 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db/custom --mode signatures
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

> Auto-generated. 15 files across 3 directories.

```
db/custom/
├── MODULE_README.md
├── __init__.py
├── ai_model_manager.py
├── ai_models/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── ai_model_base.py
│   ├── ai_model_dto.py
│   ├── ai_model_manager.py
│   ├── ai_model_validator.py
├── conversation_gate.py
├── conversation_rebuild.py
├── cx_managers.py
├── persistence.py
├── tests/
│   ├── ai_model_tests.py
│   ├── cx_manager_tests.py
# excluded: 2 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: db/custom/__init__.py  [python]




---
Filepath: db/custom/cx_managers.py  [python]

  class CxToolCallManager(CxToolCallBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxToolCallManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxToolCall) -> None
  class CxConversationManager(CxConversationBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxConversationManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxConversation) -> None
  class CxMediaManager(CxMediaBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxMediaManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxMedia) -> None
  class CxMessageManager(CxMessageBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxMessageManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxMessage) -> None
  class CxUserRequestManager(CxUserRequestBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxUserRequestManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None
  class CxRequestManager(CxRequestBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxRequestManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxRequest) -> None
  class CxAgentMemoryManager(CxAgentMemoryBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxAgentMemoryManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None
  class CxManagers:
      def __new__(cls, *args: Any, **kwargs: Any) -> CxManagers
      def __init__(self) -> None
      async def get_conversation_data(self, conversation_id: str) -> dict[str, Any]
      async def get_unified_config(self, flat_data: dict[str, Any]) -> UnifiedConfig
      async def get_conversation_unified_config(self, conversation_id: str) -> UnifiedConfig
      async def get_full_conversation(self, conversation_id: str) -> dict[str, Any]



---
Filepath: db/custom/conversation_gate.py  [python]

  class ConversationGateError(Exception):
  def _is_valid_uuid(value: str | None) -> bool
  def _require_valid_user_id(user_id: str | None, context: str = '') -> str
  async def create_new_conversation(conversation_id: str, user_id: str, metadata: dict[str, Any] | None = None) -> None
  async def ensure_conversation_exists(conversation_id: str, user_id: str, parent_conversation_id: str | None = None) -> None
  async def verify_existing_conversation(conversation_id: str) -> dict[str, Any]
  async def update_conversation_status(conversation_id: str, status: str) -> None
  async def create_pending_user_request(request_id: str, conversation_id: str, user_id: str) -> None
  async def update_user_request_status(request_id: str, status: str, error: str | None = None) -> None
  def launch_conversation_gate(conversation_id: str, is_new_conversation: bool, execution_task: asyncio.Task[Any]) -> asyncio.Task[Any] | None
  async def _gate_task() -> None
  def _on_gate_done(t: asyncio.Task[Any]) -> None
  async def _send_fatal() -> None



---
Filepath: db/custom/ai_model_manager.py  [python]

  class AiModelManager(AiModelBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def load_all_models(self, update_data_in_code: bool = False)
      async def load_model(self, id_or_name: str)
      async def load_model_by_id(self, model_id: str)
      async def load_models_by_name(self, model_name: str)
      async def load_models_by_provider(self, provider: str)
      async def list_unique_model_providers(self, update_data_in_code: bool = False)
      async def update_data_in_code(self, data, variable_name)
  def get_ai_model_manager()



---
Filepath: db/custom/persistence.py  [python]

  def _is_valid_uuid(value: str | None) -> bool
  async def _backfill_tool_call_message_id(msg: dict[str, Any], message_id: str, conversation_id: str) -> None
  async def persist_completed_request(completed: CompletedRequest, conversation_id: str | None = None) -> dict[str, Any]



---
Filepath: db/custom/conversation_rebuild.py  [python]

  def _rebuild_tool_result_content(tool_calls: list[CxToolCall]) -> list[dict[str, Any]]
  async def _map_tool_calls_to_messages(messages: list[CxMessage], tool_calls: list[CxToolCall]) -> dict[str, list[dict[str, Any]]]
  async def rebuild_conversation_messages(raw_messages: list[CxMessage], tool_calls: list[CxToolCall], media: list[CxMedia]) -> list[CxMessage]



---
Filepath: db/custom/tests/cx_manager_tests.py  [python]

  async def test_load_conversation()
  async def test_get_conversation_data()
  async def test_get_conversation_unified_config()
  async def test_get_full_conversation()
  async def test_get_convo_to_openai_format()



---
Filepath: db/custom/tests/ai_model_tests.py  [python]

  async def local_test(test_type: str, **kwargs)



---
Submodule: db/custom/ai_models/  [5 files — full detail in db/custom/ai_models/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `orchestrator/executor.py` | `create_pending_user_request()` |
| `orchestrator/executor.py` | `ensure_conversation_exists()` |
| `orchestrator/executor.py` | `persist_completed_request()` |
| `orchestrator/executor.py` | `update_conversation_status()` |
| `orchestrator/executor.py` | `update_user_request_status()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrix, matrx_orm, matrx_utils
**Internal modules:** config.message_config, config.unified_config, context.app_context, db.managers, db.models, orchestrator.requests, providers.openai, tools.handle_tool_calls
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "db/custom",
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
