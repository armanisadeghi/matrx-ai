# `db.managers` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `db/managers` |
| Last generated | 2026-02-28 12:20 |
| Output file | `db/managers/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db/managers --mode signatures \
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

> Auto-generated. 17 files across 1 directories.

```
db/managers/
├── __init__.py
├── ai_model.py
├── ai_provider.py
├── content_blocks.py
├── cx_agent_memory.py
├── cx_conversation.py
├── cx_media.py
├── cx_message.py
├── cx_request.py
├── cx_tool_call.py
├── cx_user_request.py
├── prompt_builtins.py
├── prompts.py
├── shortcut_categories.py
├── table_data.py
├── tools.py
├── user_tables.py
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: db/managers/__init__.py  [python]



---
Filepath: db/managers/content_blocks.py  [python]

  class ContentBlocksView(ModelView):
  class ContentBlocksDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class ContentBlocksBase(BaseManager[ContentBlocks]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None
      async def create_content_blocks(self, **data)
      async def delete_content_blocks(self, id)
      async def get_content_blocks_with_all_related(self, id)
      async def load_content_blocks_by_id(self, id)
      async def load_content_blocks(self, use_cache = True, **kwargs)
      async def update_content_blocks(self, id, **updates)
      async def load_content_block(self, **kwargs)
      async def filter_content_block(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_content_blocks_with_shortcut_categories(self, id)
      async def get_content_block_with_shortcut_categories(self)
      async def load_content_block_by_category_id(self, category_id)
      async def filter_content_block_by_category_id(self, category_id)
      async def load_content_block_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_content_blocks_ids(self)
  class ContentBlocksManager(ContentBlocksBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None


---
Filepath: db/managers/cx_message.py  [python]

  class CxMessageView(ModelView):
  class CxMessageDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxMessageBase(BaseManager[CxMessage]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxMessage) -> None
      async def create_cx_message(self, **data)
      async def delete_cx_message(self, id)
      async def get_cx_message_with_all_related(self, id)
      async def load_cx_message_by_id(self, id)
      async def load_cx_message(self, use_cache = True, **kwargs)
      async def update_cx_message(self, id, **updates)
      async def load_cx_messages(self, **kwargs)
      async def filter_cx_messages(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_message_with_cx_conversation(self, id)
      async def get_cx_messages_with_cx_conversation(self)
      async def get_cx_message_with_cx_tool_call(self, id)
      async def get_cx_messages_with_cx_tool_call(self)
      async def load_cx_messages_by_conversation_id(self, conversation_id)
      async def filter_cx_messages_by_conversation_id(self, conversation_id)
      async def load_cx_messages_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_message_ids(self)
  class CxMessageManager(CxMessageBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxMessage) -> None


---
Filepath: db/managers/table_data.py  [python]

  class TableDataView(ModelView):
  class TableDataDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class TableDataBase(BaseManager[TableData]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: TableData) -> None
      async def create_table_data(self, **data)
      async def delete_table_data(self, id)
      async def get_table_data_with_all_related(self, id)
      async def load_table_data_by_id(self, id)
      async def load_table_data(self, use_cache = True, **kwargs)
      async def update_table_data(self, id, **updates)
      async def load_table_datas(self, **kwargs)
      async def filter_table_datas(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_table_data_with_user_tables(self, id)
      async def get_table_datas_with_user_tables(self)
      async def load_table_datas_by_table_id(self, table_id)
      async def filter_table_datas_by_table_id(self, table_id)
      async def load_table_datas_by_user_id(self, user_id)
      async def filter_table_datas_by_user_id(self, user_id)
      async def load_table_datas_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_table_data_ids(self)
  class TableDataManager(TableDataBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: TableData) -> None


---
Filepath: db/managers/tools.py  [python]

  class ToolsView(ModelView):
  class ToolsDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class ToolsBase(BaseManager[Tools]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: Tools) -> None
      async def create_tools(self, **data)
      async def delete_tools(self, id)
      async def get_tools_with_all_related(self, id)
      async def load_tools_by_id(self, id)
      async def load_tools(self, use_cache = True, **kwargs)
      async def update_tools(self, id, **updates)
      async def load_tool(self, **kwargs)
      async def filter_tool(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_tools_with_tool_test_samples(self, id)
      async def get_tool_with_tool_test_samples(self)
      async def get_tools_with_tool_ui_components(self, id)
      async def get_tool_with_tool_ui_components(self)
      async def load_tool_by_tags(self, tags)
      async def filter_tool_by_tags(self, tags)
      async def load_tool_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_tools_ids(self)
  class ToolsManager(ToolsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: Tools) -> None


---
Filepath: db/managers/cx_user_request.py  [python]

  class CxUserRequestView(ModelView):
  class CxUserRequestDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxUserRequestBase(BaseManager[CxUserRequest]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None
      async def create_cx_user_request(self, **data)
      async def delete_cx_user_request(self, id)
      async def get_cx_user_request_with_all_related(self, id)
      async def load_cx_user_request_by_id(self, id)
      async def load_cx_user_request(self, use_cache = True, **kwargs)
      async def update_cx_user_request(self, id, **updates)
      async def load_cx_user_requests(self, **kwargs)
      async def filter_cx_user_requests(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_user_request_with_ai_model(self, id)
      async def get_cx_user_requests_with_ai_model(self)
      async def get_cx_user_request_with_cx_conversation(self, id)
      async def get_cx_user_requests_with_cx_conversation(self)
      async def get_cx_user_request_with_cx_tool_call(self, id)
      async def get_cx_user_requests_with_cx_tool_call(self)
      async def get_cx_user_request_with_cx_request(self, id)
      async def get_cx_user_requests_with_cx_request(self)
      async def load_cx_user_requests_by_conversation_id(self, conversation_id)
      async def filter_cx_user_requests_by_conversation_id(self, conversation_id)
      async def load_cx_user_requests_by_user_id(self, user_id)
      async def filter_cx_user_requests_by_user_id(self, user_id)
      async def load_cx_user_requests_by_ai_model_id(self, ai_model_id)
      async def filter_cx_user_requests_by_ai_model_id(self, ai_model_id)
      async def load_cx_user_requests_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_user_request_ids(self)
  class CxUserRequestManager(CxUserRequestBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None


---
Filepath: db/managers/ai_model.py  [python]

  class AiModelView(ModelView):
  class AiModelDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class AiModelBase(BaseManager[AiModel]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: AiModel) -> None
      async def create_ai_model(self, **data)
      async def delete_ai_model(self, id)
      async def get_ai_model_with_all_related(self, id)
      async def load_ai_model_by_id(self, id)
      async def load_ai_model(self, use_cache = True, **kwargs)
      async def update_ai_model(self, id, **updates)
      async def load_ai_models(self, **kwargs)
      async def filter_ai_models(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
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
  class AiModelManager(AiModelBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: AiModel) -> None


---
Filepath: db/managers/cx_media.py  [python]

  class CxMediaView(ModelView):
  class CxMediaDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxMediaBase(BaseManager[CxMedia]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxMedia) -> None
      async def create_cx_media(self, **data)
      async def delete_cx_media(self, id)
      async def get_cx_media_with_all_related(self, id)
      async def load_cx_media_by_id(self, id)
      async def load_cx_media(self, use_cache = True, **kwargs)
      async def update_cx_media(self, id, **updates)
      async def load_cx_medias(self, **kwargs)
      async def filter_cx_medias(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_media_with_cx_conversation(self, id)
      async def get_cx_medias_with_cx_conversation(self)
      async def load_cx_medias_by_conversation_id(self, conversation_id)
      async def filter_cx_medias_by_conversation_id(self, conversation_id)
      async def load_cx_medias_by_user_id(self, user_id)
      async def filter_cx_medias_by_user_id(self, user_id)
      async def load_cx_medias_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_media_ids(self)
  class CxMediaManager(CxMediaBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxMedia) -> None


---
Filepath: db/managers/shortcut_categories.py  [python]

  class ShortcutCategoriesView(ModelView):
  class ShortcutCategoriesDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class ShortcutCategoriesBase(BaseManager[ShortcutCategories]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: ShortcutCategories) -> None
      async def create_shortcut_categories(self, **data)
      async def delete_shortcut_categories(self, id)
      async def get_shortcut_categories_with_all_related(self, id)
      async def load_shortcut_categories_by_id(self, id)
      async def load_shortcut_categories(self, use_cache = True, **kwargs)
      async def update_shortcut_categories(self, id, **updates)
      async def load_shortcut_category(self, **kwargs)
      async def filter_shortcut_category(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_shortcut_categories_with_self_reference(self, id)
      async def get_shortcut_category_with_self_reference(self)
      async def get_shortcut_categories_with_content_blocks(self, id)
      async def get_shortcut_category_with_content_blocks(self)
      async def get_shortcut_categories_with_prompt_shortcuts(self, id)
      async def get_shortcut_category_with_prompt_shortcuts(self)
      async def get_shortcut_categories_with_system_prompts_new(self, id)
      async def get_shortcut_category_with_system_prompts_new(self)
      async def load_shortcut_category_by_parent_category_id(self, parent_category_id)
      async def filter_shortcut_category_by_parent_category_id(self, parent_category_id)
      async def load_shortcut_category_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_shortcut_categories_ids(self)
  class ShortcutCategoriesManager(ShortcutCategoriesBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: ShortcutCategories) -> None


---
Filepath: db/managers/cx_request.py  [python]

  class CxRequestView(ModelView):
  class CxRequestDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxRequestBase(BaseManager[CxRequest]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxRequest) -> None
      async def create_cx_request(self, **data)
      async def delete_cx_request(self, id)
      async def get_cx_request_with_all_related(self, id)
      async def load_cx_request_by_id(self, id)
      async def load_cx_request(self, use_cache = True, **kwargs)
      async def update_cx_request(self, id, **updates)
      async def load_cx_requests(self, **kwargs)
      async def filter_cx_requests(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_request_with_ai_model(self, id)
      async def get_cx_requests_with_ai_model(self)
      async def get_cx_request_with_cx_conversation(self, id)
      async def get_cx_requests_with_cx_conversation(self)
      async def get_cx_request_with_cx_user_request(self, id)
      async def get_cx_requests_with_cx_user_request(self)
      async def load_cx_requests_by_user_request_id(self, user_request_id)
      async def filter_cx_requests_by_user_request_id(self, user_request_id)
      async def load_cx_requests_by_conversation_id(self, conversation_id)
      async def filter_cx_requests_by_conversation_id(self, conversation_id)
      async def load_cx_requests_by_ai_model_id(self, ai_model_id)
      async def filter_cx_requests_by_ai_model_id(self, ai_model_id)
      async def load_cx_requests_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_request_ids(self)
  class CxRequestManager(CxRequestBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxRequest) -> None


---
Filepath: db/managers/cx_tool_call.py  [python]

  class CxToolCallView(ModelView):
  class CxToolCallDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxToolCallBase(BaseManager[CxToolCall]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxToolCall) -> None
      async def create_cx_tool_call(self, **data)
      async def delete_cx_tool_call(self, id)
      async def get_cx_tool_call_with_all_related(self, id)
      async def load_cx_tool_call_by_id(self, id)
      async def load_cx_tool_call(self, use_cache = True, **kwargs)
      async def update_cx_tool_call(self, id, **updates)
      async def load_cx_tool_calls(self, **kwargs)
      async def filter_cx_tool_calls(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_tool_call_with_cx_conversation(self, id)
      async def get_cx_tool_calls_with_cx_conversation(self)
      async def get_cx_tool_call_with_cx_message(self, id)
      async def get_cx_tool_calls_with_cx_message(self)
      async def get_cx_tool_call_with_cx_user_request(self, id)
      async def get_cx_tool_calls_with_cx_user_request(self)
      async def get_cx_tool_call_with_self_reference(self, id)
      async def get_cx_tool_calls_with_self_reference(self)
      async def load_cx_tool_calls_by_conversation_id(self, conversation_id)
      async def filter_cx_tool_calls_by_conversation_id(self, conversation_id)
      async def load_cx_tool_calls_by_message_id(self, message_id)
      async def filter_cx_tool_calls_by_message_id(self, message_id)
      async def load_cx_tool_calls_by_user_id(self, user_id)
      async def filter_cx_tool_calls_by_user_id(self, user_id)
      async def load_cx_tool_calls_by_request_id(self, request_id)
      async def filter_cx_tool_calls_by_request_id(self, request_id)
      async def load_cx_tool_calls_by_parent_call_id(self, parent_call_id)
      async def filter_cx_tool_calls_by_parent_call_id(self, parent_call_id)
      async def load_cx_tool_calls_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_tool_call_ids(self)
  class CxToolCallManager(CxToolCallBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxToolCall) -> None


---
Filepath: db/managers/cx_agent_memory.py  [python]

  class CxAgentMemoryView(ModelView):
  class CxAgentMemoryDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxAgentMemoryBase(BaseManager[CxAgentMemory]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None
      async def create_cx_agent_memory(self, **data)
      async def delete_cx_agent_memory(self, id)
      async def get_cx_agent_memory_with_all_related(self, id)
      async def load_cx_agent_memory_by_id(self, id)
      async def load_cx_agent_memory(self, use_cache = True, **kwargs)
      async def update_cx_agent_memory(self, id, **updates)
      async def load_cx_agent_memories(self, **kwargs)
      async def filter_cx_agent_memories(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def load_cx_agent_memories_by_user_id(self, user_id)
      async def filter_cx_agent_memories_by_user_id(self, user_id)
      async def load_cx_agent_memories_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_agent_memory_ids(self)
  class CxAgentMemoryManager(CxAgentMemoryBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None


---
Filepath: db/managers/user_tables.py  [python]

  class UserTablesView(ModelView):
  class UserTablesDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class UserTablesBase(BaseManager[UserTables]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: UserTables) -> None
      async def create_user_tables(self, **data)
      async def delete_user_tables(self, id)
      async def get_user_tables_with_all_related(self, id)
      async def load_user_tables_by_id(self, id)
      async def load_user_tables(self, use_cache = True, **kwargs)
      async def update_user_tables(self, id, **updates)
      async def load_user_table(self, **kwargs)
      async def filter_user_table(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_user_tables_with_table_data(self, id)
      async def get_user_table_with_table_data(self)
      async def get_user_tables_with_table_fields(self, id)
      async def get_user_table_with_table_fields(self)
      async def load_user_table_by_user_id(self, user_id)
      async def filter_user_table_by_user_id(self, user_id)
      async def load_user_table_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_user_tables_ids(self)
  class UserTablesManager(UserTablesBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: UserTables) -> None


---
Filepath: db/managers/cx_conversation.py  [python]

  class CxConversationView(ModelView):
  class CxConversationDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class CxConversationBase(BaseManager[CxConversation]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: CxConversation) -> None
      async def create_cx_conversation(self, **data)
      async def delete_cx_conversation(self, id)
      async def get_cx_conversation_with_all_related(self, id)
      async def load_cx_conversation_by_id(self, id)
      async def load_cx_conversation(self, use_cache = True, **kwargs)
      async def update_cx_conversation(self, id, **updates)
      async def load_cx_conversations(self, **kwargs)
      async def filter_cx_conversations(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_cx_conversation_with_ai_model(self, id)
      async def get_cx_conversations_with_ai_model(self)
      async def get_cx_conversation_with_self_reference(self, id)
      async def get_cx_conversations_with_self_reference(self)
      async def get_cx_conversation_with_cx_tool_call(self, id)
      async def get_cx_conversations_with_cx_tool_call(self)
      async def get_cx_conversation_with_cx_message(self, id)
      async def get_cx_conversations_with_cx_message(self)
      async def get_cx_conversation_with_cx_media(self, id)
      async def get_cx_conversations_with_cx_media(self)
      async def get_cx_conversation_with_cx_user_request(self, id)
      async def get_cx_conversations_with_cx_user_request(self)
      async def get_cx_conversation_with_cx_request(self, id)
      async def get_cx_conversations_with_cx_request(self)
      async def load_cx_conversations_by_user_id(self, user_id)
      async def filter_cx_conversations_by_user_id(self, user_id)
      async def load_cx_conversations_by_forked_from_id(self, forked_from_id)
      async def filter_cx_conversations_by_forked_from_id(self, forked_from_id)
      async def load_cx_conversations_by_ai_model_id(self, ai_model_id)
      async def filter_cx_conversations_by_ai_model_id(self, ai_model_id)
      async def load_cx_conversations_by_parent_conversation_id(self, parent_conversation_id)
      async def filter_cx_conversations_by_parent_conversation_id(self, parent_conversation_id)
      async def load_cx_conversations_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_cx_conversation_ids(self)
  class CxConversationManager(CxConversationBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: CxConversation) -> None


---
Filepath: db/managers/ai_provider.py  [python]

  class AiProviderView(ModelView):
  class AiProviderDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class AiProviderBase(BaseManager[AiProvider]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: AiProvider) -> None
      async def create_ai_provider(self, **data)
      async def delete_ai_provider(self, id)
      async def get_ai_provider_with_all_related(self, id)
      async def load_ai_provider_by_id(self, id)
      async def load_ai_provider(self, use_cache = True, **kwargs)
      async def update_ai_provider(self, id, **updates)
      async def load_ai_providers(self, **kwargs)
      async def filter_ai_providers(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_ai_provider_with_ai_settings(self, id)
      async def get_ai_providers_with_ai_settings(self)
      async def get_ai_provider_with_ai_model(self, id)
      async def get_ai_providers_with_ai_model(self)
      async def load_ai_providers_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_ai_provider_ids(self)
  class AiProviderManager(AiProviderBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: AiProvider) -> None


---
Filepath: db/managers/prompt_builtins.py  [python]

  class PromptBuiltinsView(ModelView):
  class PromptBuiltinsDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class PromptBuiltinsBase(BaseManager[PromptBuiltins]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: PromptBuiltins) -> None
      async def create_prompt_builtins(self, **data)
      async def delete_prompt_builtins(self, id)
      async def get_prompt_builtins_with_all_related(self, id)
      async def load_prompt_builtins_by_id(self, id)
      async def load_prompt_builtins(self, use_cache = True, **kwargs)
      async def update_prompt_builtins(self, id, **updates)
      async def load_prompt_builtin(self, **kwargs)
      async def filter_prompt_builtin(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_prompt_builtins_with_prompts(self, id)
      async def get_prompt_builtin_with_prompts(self)
      async def get_prompt_builtins_with_prompt_shortcuts(self, id)
      async def get_prompt_builtin_with_prompt_shortcuts(self)
      async def get_prompt_builtins_with_prompt_actions(self, id)
      async def get_prompt_builtin_with_prompt_actions(self)
      async def load_prompt_builtin_by_created_by_user_id(self, created_by_user_id)
      async def filter_prompt_builtin_by_created_by_user_id(self, created_by_user_id)
      async def load_prompt_builtin_by_source_prompt_id(self, source_prompt_id)
      async def filter_prompt_builtin_by_source_prompt_id(self, source_prompt_id)
      async def load_prompt_builtin_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_prompt_builtins_ids(self)
  class PromptBuiltinsManager(PromptBuiltinsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: PromptBuiltins) -> None


---
Filepath: db/managers/prompts.py  [python]

  class PromptsView(ModelView):
  class PromptsDTO(BaseDTO):
      async def _initialize_dto(self, model)
      async def _process_core_data(self, model)
      async def _process_metadata(self, model)
      async def _initial_validation(self, model)
      async def _final_validation(self)
      async def get_validated_dict(self)
  class PromptsBase(BaseManager[Prompts]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None)
      def _initialize_manager(self)
      async def _initialize_runtime_data(self, item: Prompts) -> None
      async def create_prompts(self, **data)
      async def delete_prompts(self, id)
      async def get_prompts_with_all_related(self, id)
      async def load_prompts_by_id(self, id)
      async def load_prompts(self, use_cache = True, **kwargs)
      async def update_prompts(self, id, **updates)
      async def load_prompt(self, **kwargs)
      async def filter_prompt(self, **kwargs)
      async def get_or_create(self, defaults = None, **kwargs)
      async def get_prompts_with_prompt_apps(self, id)
      async def get_prompt_with_prompt_apps(self)
      async def get_prompts_with_system_prompts_new(self, id)
      async def get_prompt_with_system_prompts_new(self)
      async def get_prompts_with_prompt_builtins(self, id)
      async def get_prompt_with_prompt_builtins(self)
      async def get_prompts_with_prompt_actions(self, id)
      async def get_prompt_with_prompt_actions(self)
      async def get_prompts_with_system_prompts(self, id)
      async def get_prompt_with_system_prompts(self)
      async def load_prompt_by_user_id(self, user_id)
      async def filter_prompt_by_user_id(self, user_id)
      async def load_prompt_by_ids(self, ids)
      def add_computed_field(self, field)
      def add_relation_field(self, field)
      def active_prompts_ids(self)
  class PromptsManager(PromptsBase):
      def __new__(cls, *args, **kwargs)
      def __init__(self)
      async def _initialize_runtime_data(self, item: Prompts) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils
**Internal modules:** db.models
<!-- /AUTO:dependencies -->
