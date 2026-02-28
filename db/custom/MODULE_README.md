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
| Last generated | 2026-02-28 12:20 |
| Output file | `db/custom/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db/custom --mode signatures \
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

> Auto-generated. 12 files across 2 directories.

```
db/custom/
├── __init__.py
├── ai_model_manager.py
├── ai_models/
│   ├── __init__.py
│   ├── ai_model_base.py
│   ├── ai_model_dto.py
│   ├── ai_model_manager.py
│   ├── ai_model_validator.py
│   ├── tests.py
├── conversation_gate.py
├── conversation_rebuild.py
├── cx_managers.py
├── persistence.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: db/custom/__init__.py  [python]



---
Filepath: db/custom/cx_managers.py  [python]

  class CxToolCallManager(CxToolCallBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxToolCall) -> None
  class CxConversationManager(CxConversationBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxConversation) -> None
  class CxMediaManager(CxMediaBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxMedia) -> None
  class CxMessageManager(CxMessageBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxMessage) -> None
  class CxUserRequestManager(CxUserRequestBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None
  class CxRequestManager(CxRequestBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxRequest) -> None
  class CxAgentMemoryManager(CxAgentMemoryBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None
  class CxManagers:
      def __new__(cls, *args, **kwargs)
      def __init__(self)
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
Filepath: db/custom/ai_models/__init__.py  [python]



---
Filepath: db/custom/ai_models/ai_model_validator.py  [python]

  class AiModelValidator(AiModelManager):
      async def validate_data_integrity(self) -> Dict[str, List[str]]
      async def fix_malformed_endpoints(self) -> Dict[str, List[str]]
      def _validate_name(self, model: Any) -> str
      def _validate_model_class(self, model: Any, existing_names: set) -> str
      def _validate_endpoints(self, model: Any) -> str
      def _validate_model_provider(self, model: Any) -> str
      def _validate_max_tokens(self, model: Any) -> str
      def _validate_capabilities(self, model: Any) -> str
      def _print_validation_summary(self, report: Dict[str, List[str]]) -> None
      def _print_fix_summary(self, report: Dict[str, List[str]]) -> None
  async def validate_and_fix_endpoints()
  async def main()


---
Filepath: db/custom/ai_models/tests.py  [python]

  async def local_test(test_type: str, **kwargs)


---
Filepath: db/custom/ai_models/ai_model_base.py  [python]

  class AiModelBase(BaseManager[AiModel]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None, fetch_on_init_limit: int = 200, fetch_on_init_with_warnings_off: str = 'YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100')
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: AiModel) -> None
      async def create_ai_model(self, **data) -> AiModel
      async def delete_ai_model(self, id) -> None
      async def get_ai_model_with_all_related(self, id) -> AiModel
      async def load_ai_model_by_id(self, id) -> AiModel | None
      async def load_ai_model(self, use_cache = True, **kwargs) -> AiModel | None
      async def update_ai_model(self, id, **updates) -> AiModel
      async def load_ai_models(self, **kwargs) -> list[AiModel]
      async def filter_ai_models(self, **kwargs) -> list[AiModel]
      async def get_or_create(self, defaults = None, **kwargs) -> AiModel
      async def get_ai_model_with_ai_provider(self, id)
      async def get_ai_models_with_ai_provider(self)
      async def get_ai_model_with_ai_model_endpoint(self, id)
      async def get_ai_models_with_ai_model_endpoint(self)
      async def get_ai_model_with_ai_settings(self, id)
      async def get_ai_models_with_ai_settings(self)
      async def get_ai_model_with_recipe_model(self, id)
      async def get_ai_models_with_recipe_model(self)
      async def load_ai_models_by_name(self, name)
      async def filter_ai_models_by_name(self, name)
      async def load_ai_models_by_common_name(self, common_name)
      async def filter_ai_models_by_common_name(self, common_name)
      async def load_ai_models_by_provider(self, provider)
      async def filter_ai_models_by_provider(self, provider)
      async def load_ai_models_by_model_class(self, model_class)
      async def filter_ai_models_by_model_class(self, model_class)
      async def load_ai_models_by_model_provider(self, model_provider)
      async def filter_ai_models_by_model_provider(self, model_provider)
      async def load_ai_models_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_ai_model_ids(self)
  async def main()


---
Filepath: db/custom/ai_models/ai_model_dto.py  [python]

  DEFAULT_MAX_TOKENS = 4096
  class AiModelDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, ai_model_item)
      async def _process_metadata(self, ai_model_item)
      async def _initial_validation(self, ai_model_item)
      async def _final_validation(self)
      async def get_validated_dict(self)


---
Filepath: db/custom/ai_models/ai_model_manager.py  [python]

  class AiModelManager(AiModelBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def load_all_models(self, update_data_in_code: bool = False)
      async def load_model(self, id_or_name: str) -> AiModel | None
      async def load_model_get_string_uuid(self, id_or_name: str) -> str | None
      async def load_model_by_id(self, model_id: str) -> AiModel | None
      async def load_models_by_name(self, model_name: str) -> list[AiModel]
      async def load_models_by_provider(self, provider: str) -> list[AiModel]
  def get_ai_model_manager()
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

**External packages:** matrix, matrx_orm, matrx_utils
**Internal modules:** config.unified_config, context.app_context, db.managers, db.models, orchestrator.requests, tools.handle_tool_calls
<!-- /AUTO:dependencies -->
