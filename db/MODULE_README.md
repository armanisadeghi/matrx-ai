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
| Last generated | 2026-02-28 12:20 |
| Output file | `db/MODULE_README.md` |
| Signature mode | `signatures` |


**Child READMEs detected** (signatures collapsed — see links for detail):

| README | |
|--------|---|
| [`db/custom/MODULE_README.md`](db/custom/MODULE_README.md) | last generated 2026-02-28 12:20 |
| [`db/managers/MODULE_README.md`](db/managers/MODULE_README.md) | last generated 2026-02-28 12:20 |
**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db --mode signatures \
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

> Auto-generated. 37 files across 5 directories.

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
│   │   ├── tests.py
│   ├── conversation_gate.py
│   ├── conversation_rebuild.py
│   ├── cx_managers.py
│   ├── persistence.py
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
# excluded: 4 .md, 1 .yaml
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
  MANAGED_TABLES = {'cx_conversation', 'cx_messages', 'cx_agent_memory', 'cx_media', 'cx_request', 'cx_tool_call', 'cx_user_request', 'ai_model'}
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
      async def _initialize_runtime_data(self, ai_provider)
  class CxAgentMemoryDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxAgentMemoryManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_agent_memory)
  class PromptsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class PromptsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, prompts)
  class ShortcutCategoriesDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ShortcutCategoriesManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, shortcut_categories)
  class ToolsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ToolsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, tools)
  class UserTablesDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class UserTablesManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, user_tables)
  class AiModelDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class AiModelManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, ai_model)
  class ContentBlocksDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class ContentBlocksManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, content_blocks)
  class PromptBuiltinsDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class PromptBuiltinsManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, prompt_builtins)
  class TableDataDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class TableDataManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, table_data)
  class CxConversationDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxConversationManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_conversation)
  class CxMediaDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxMediaManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_media)
  class CxMessageDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxMessageManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_message)
  class CxUserRequestDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxUserRequestManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_user_request)
  class CxRequestDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxRequestManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_request)
  class CxToolCallDTO(BaseDTO):
      async def from_model(cls, model: 'Model')
  class CxToolCallManager(BaseManager):
      def __init__(self)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, cx_tool_call)



---
Filepath: db/helpers/auto_config.py  [python]




---
Submodule: db/managers/  [17 files — full detail in db/managers/MODULE_README.md]

---
Submodule: db/custom/  [12 files — full detail in db/custom/MODULE_README.md]

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

**External packages:** dotenv, matrix, matrx_orm, matrx_utils
**Internal modules:** config.unified_config, context.app_context, orchestrator.requests, tools.handle_tool_calls
<!-- /AUTO:dependencies -->
