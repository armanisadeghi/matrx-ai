# `db` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `db` |
| Last generated | 2026-03-01 00:10 |
| Output file | `db/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`db/custom/MODULE_README.md`](db/custom/MODULE_README.md) | last generated 2026-03-01 00:10 |
| [`db/managers/MODULE_README.md`](db/managers/MODULE_README.md) | last generated 2026-03-01 00:10 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db --mode signatures
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

> Auto-generated. 38 files across 6 directories.

```
db/
├── MODULE_README.md
├── __init__.py
├── custom/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── ai_model_manager.py
│   ├── ai_models/
│   │   ├── __init__.py
│   │   ├── ai_model_base.py
│   │   ├── ai_model_dto.py
│   │   ├── ai_model_manager.py
│   │   ├── ai_model_validator.py
│   ├── conversation_gate.py
│   ├── conversation_rebuild.py
│   ├── cx_managers.py
│   ├── persistence.py
│   ├── tests/
│   │   ├── ai_model_tests.py
│   │   ├── cx_manager_tests.py
├── generate.py
├── helpers/
│   ├── auto_config.py
├── managers/
│   ├── MODULE_README.md
│   ├── __init__.py
│   ├── ai_model.py
│   ├── ai_provider.py
│   ├── content_blocks.py
│   ├── cx_agent_memory.py
│   ├── cx_conversation.py
│   ├── cx_media.py
│   ├── cx_message.py
│   ├── cx_request.py
│   ├── cx_tool_call.py
│   ├── cx_user_request.py
│   ├── prompt_builtins.py
│   ├── prompts.py
│   ├── shortcut_categories.py
│   ├── table_data.py
│   ├── tools.py
│   ├── user_tables.py
├── models.py
├── run_migrations.py
# excluded: 5 .md, 1 .yaml
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="{mode}"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.
> Submodules with their own `MODULE_README.md` are collapsed to a single stub line.

```
---
Filepath: db/__init__.py  [python]




---
Filepath: db/run_migrations.py  [python]

  DATABASE = 'supabase_automation_matrix'
  MIGRATIONS_DIR = 'migrations'
  MANAGED_TABLES = {8 items}
  async def make(name: str | None = None) -> None
  async def apply() -> None
  async def rollback_last(steps: int = 1) -> None
  async def status() -> None
  async def empty(name: str = 'custom') -> None
  def _usage() -> None



---
Filepath: db/generate.py  [python]




---
Filepath: db/models.py  [python]

  class Users(Model):
  class AiProvider(Model):
  class CxAgentMemory(Model):
  class Prompts(Model):
  class ShortcutCategories(Model):
  class Tools(Model):
  class UserTables(Model):
  class AiModel(Model):
  class ContentBlocks(Model):
  class PromptBuiltins(Model):
  class TableData(Model):
  class CxConversation(Model):
  class CxMedia(Model):
  class CxMessage(Model):
  class CxUserRequest(Model):
  class CxRequest(Model):
  class CxToolCall(Model):
  class AiProviderDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class AiProviderManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: AiProvider) -> None
  class CxAgentMemoryDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxAgentMemoryManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None
  class PromptsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class PromptsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: Prompts) -> None
  class ShortcutCategoriesDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ShortcutCategoriesManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ShortcutCategories) -> None
  class ToolsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ToolsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: Tools) -> None
  class UserTablesDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class UserTablesManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: UserTables) -> None
  class AiModelDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class AiModelManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: AiModel) -> None
  class ContentBlocksDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ContentBlocksManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None
  class PromptBuiltinsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class PromptBuiltinsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: PromptBuiltins) -> None
  class TableDataDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class TableDataManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: TableData) -> None
  class CxConversationDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxConversationManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxConversation) -> None
  class CxMediaDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxMediaManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxMedia) -> None
  class CxMessageDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxMessageManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxMessage) -> None
  class CxUserRequestDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxUserRequestManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None
  class CxRequestDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxRequestManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxRequest) -> None
  class CxToolCallDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxToolCallManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxToolCall) -> None



---
Filepath: db/helpers/auto_config.py  [python]




---
Submodule: db/managers/  [17 files — full detail in db/managers/MODULE_README.md]

---
Submodule: db/custom/  [13 files — full detail in db/custom/MODULE_README.md]

```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `providers/unified_client.py` | `AiModel()` |
| `instructions/content_blocks_manager.py` | `ContentBlocks()` |
| `instructions/matrx_fetcher.py` | `ContentBlocks()` |
| `instructions/tests/direct_fetch_test.py` | `ContentBlocks()` |
| `instructions/content_blocks_manager.py` | `ContentBlocksDTO()` |
| `config/message_config.py` | `CxMessage()` |
| `agents/manager.py` | `PromptBuiltins()` |
| `agents/manager.py` | `PromptBuiltinsBase()` |
| `agents/manager.py` | `Prompts()` |
| `tests/prompts/prompt_to_config.py` | `Prompts()` |
| `agents/manager.py` | `PromptsBase()` |
| `instructions/tests/user_table_data_test.py` | `TableData()` |
| `tools/tools_db.py` | `ToolsBase()` |
| `orchestrator/executor.py` | `create_pending_user_request()` |
| `orchestrator/executor.py` | `ensure_conversation_exists()` |
| `orchestrator/executor.py` | `persist_completed_request()` |
| `orchestrator/executor.py` | `update_conversation_status()` |
| `orchestrator/executor.py` | `update_user_request_status()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** dotenv, matrix, matrx_orm, matrx_utils
**Internal modules:** config.message_config, config.unified_config, context.app_context, orchestrator.requests, providers.openai, tools.handle_tool_calls
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "db",
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
