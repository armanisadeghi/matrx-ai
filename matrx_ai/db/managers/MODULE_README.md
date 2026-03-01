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
| Last generated | 2026-03-01 00:10 |
| Output file | `db/managers/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db/managers --mode signatures
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

> Auto-generated. 18 files across 1 directories.

```
db/managers/
├── MODULE_README.md
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
# excluded: 1 .md
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

  class ContentBlocksView(ModelView[ContentBlocks]):
  class ContentBlocksDTO(BaseDTO[ContentBlocks]):
      async def _initialize_dto(self, model: ContentBlocks) -> None
      async def _process_core_data(self, model: ContentBlocks) -> None
      async def _process_metadata(self, model: ContentBlocks) -> None
      async def _initial_validation(self, model: ContentBlocks) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class ContentBlocksBase(BaseManager[ContentBlocks]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None
      async def create_content_blocks(self, **data: Any) -> ContentBlocks
      async def delete_content_blocks(self, id: Any) -> bool
      async def get_content_blocks_with_all_related(self, id: Any) -> tuple[ContentBlocks, Any]
      async def load_content_blocks_by_id(self, id: Any) -> ContentBlocks
      async def load_content_blocks(self, use_cache: bool = True, **kwargs: Any) -> ContentBlocks
      async def update_content_blocks(self, id: Any, **updates: Any) -> ContentBlocks
      async def load_content_block(self, **kwargs: Any) -> list[ContentBlocks]
      async def filter_content_block(self, **kwargs: Any) -> list[ContentBlocks]
      async def get_or_create_content_blocks(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ContentBlocks | None
      async def get_content_blocks_with_shortcut_categories(self, id: Any) -> tuple[Any, Any]
      async def get_content_block_with_shortcut_categories(self) -> list[Any]
      async def load_content_block_by_category_id(self, category_id: Any) -> list[Any]
      async def filter_content_block_by_category_id(self, category_id: Any) -> list[Any]
      async def load_content_block_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_content_blocks_ids(self) -> set[Any]
  class ContentBlocksManager(ContentBlocksBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> ContentBlocksManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: ContentBlocks) -> None


---
Filepath: db/managers/cx_message.py  [python]

  class CxMessageView(ModelView[CxMessage]):
  class CxMessageDTO(BaseDTO[CxMessage]):
      async def _initialize_dto(self, model: CxMessage) -> None
      async def _process_core_data(self, model: CxMessage) -> None
      async def _process_metadata(self, model: CxMessage) -> None
      async def _initial_validation(self, model: CxMessage) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxMessageBase(BaseManager[CxMessage]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxMessage) -> None
      async def create_cx_message(self, **data: Any) -> CxMessage
      async def delete_cx_message(self, id: Any) -> bool
      async def get_cx_message_with_all_related(self, id: Any) -> tuple[CxMessage, Any]
      async def load_cx_message_by_id(self, id: Any) -> CxMessage
      async def load_cx_message(self, use_cache: bool = True, **kwargs: Any) -> CxMessage
      async def update_cx_message(self, id: Any, **updates: Any) -> CxMessage
      async def load_cx_messages(self, **kwargs: Any) -> list[CxMessage]
      async def filter_cx_messages(self, **kwargs: Any) -> list[CxMessage]
      async def get_or_create_cx_message(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxMessage | None
      async def get_cx_message_with_cx_conversation(self, id: Any) -> tuple[Any, Any]
      async def get_cx_messages_with_cx_conversation(self) -> list[Any]
      async def get_cx_message_with_cx_tool_call(self, id: Any) -> tuple[Any, Any]
      async def get_cx_messages_with_cx_tool_call(self) -> list[Any]
      async def load_cx_messages_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def filter_cx_messages_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def load_cx_messages_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_message_ids(self) -> set[Any]
  class CxMessageManager(CxMessageBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxMessageManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxMessage) -> None


---
Filepath: db/managers/table_data.py  [python]

  class TableDataView(ModelView[TableData]):
  class TableDataDTO(BaseDTO[TableData]):
      async def _initialize_dto(self, model: TableData) -> None
      async def _process_core_data(self, model: TableData) -> None
      async def _process_metadata(self, model: TableData) -> None
      async def _initial_validation(self, model: TableData) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class TableDataBase(BaseManager[TableData]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: TableData) -> None
      async def create_table_data(self, **data: Any) -> TableData
      async def delete_table_data(self, id: Any) -> bool
      async def get_table_data_with_all_related(self, id: Any) -> tuple[TableData, Any]
      async def load_table_data_by_id(self, id: Any) -> TableData
      async def load_table_data(self, use_cache: bool = True, **kwargs: Any) -> TableData
      async def update_table_data(self, id: Any, **updates: Any) -> TableData
      async def load_table_datas(self, **kwargs: Any) -> list[TableData]
      async def filter_table_datas(self, **kwargs: Any) -> list[TableData]
      async def get_or_create_table_data(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> TableData | None
      async def get_table_data_with_user_tables(self, id: Any) -> tuple[Any, Any]
      async def get_table_datas_with_user_tables(self) -> list[Any]
      async def load_table_datas_by_table_id(self, table_id: Any) -> list[Any]
      async def filter_table_datas_by_table_id(self, table_id: Any) -> list[Any]
      async def load_table_datas_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_table_datas_by_user_id(self, user_id: Any) -> list[Any]
      async def load_table_datas_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_table_data_ids(self) -> set[Any]
  class TableDataManager(TableDataBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> TableDataManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: TableData) -> None


---
Filepath: db/managers/tools.py  [python]

  class ToolsView(ModelView[Tools]):
  class ToolsDTO(BaseDTO[Tools]):
      async def _initialize_dto(self, model: Tools) -> None
      async def _process_core_data(self, model: Tools) -> None
      async def _process_metadata(self, model: Tools) -> None
      async def _initial_validation(self, model: Tools) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class ToolsBase(BaseManager[Tools]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: Tools) -> None
      async def create_tools(self, **data: Any) -> Tools
      async def delete_tools(self, id: Any) -> bool
      async def get_tools_with_all_related(self, id: Any) -> tuple[Tools, Any]
      async def load_tools_by_id(self, id: Any) -> Tools
      async def load_tools(self, use_cache: bool = True, **kwargs: Any) -> Tools
      async def update_tools(self, id: Any, **updates: Any) -> Tools
      async def load_tool(self, **kwargs: Any) -> list[Tools]
      async def filter_tool(self, **kwargs: Any) -> list[Tools]
      async def get_or_create_tools(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Tools | None
      async def get_tools_with_tool_test_samples(self, id: Any) -> tuple[Any, Any]
      async def get_tool_with_tool_test_samples(self) -> list[Any]
      async def get_tools_with_tool_ui_components(self, id: Any) -> tuple[Any, Any]
      async def get_tool_with_tool_ui_components(self) -> list[Any]
      async def load_tool_by_tags(self, tags: Any) -> list[Any]
      async def filter_tool_by_tags(self, tags: Any) -> list[Any]
      async def load_tool_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_tools_ids(self) -> set[Any]
  class ToolsManager(ToolsBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> ToolsManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: Tools) -> None


---
Filepath: db/managers/cx_user_request.py  [python]

  class CxUserRequestView(ModelView[CxUserRequest]):
  class CxUserRequestDTO(BaseDTO[CxUserRequest]):
      async def _initialize_dto(self, model: CxUserRequest) -> None
      async def _process_core_data(self, model: CxUserRequest) -> None
      async def _process_metadata(self, model: CxUserRequest) -> None
      async def _initial_validation(self, model: CxUserRequest) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxUserRequestBase(BaseManager[CxUserRequest]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None
      async def create_cx_user_request(self, **data: Any) -> CxUserRequest
      async def delete_cx_user_request(self, id: Any) -> bool
      async def get_cx_user_request_with_all_related(self, id: Any) -> tuple[CxUserRequest, Any]
      async def load_cx_user_request_by_id(self, id: Any) -> CxUserRequest
      async def load_cx_user_request(self, use_cache: bool = True, **kwargs: Any) -> CxUserRequest
      async def update_cx_user_request(self, id: Any, **updates: Any) -> CxUserRequest
      async def load_cx_user_requests(self, **kwargs: Any) -> list[CxUserRequest]
      async def filter_cx_user_requests(self, **kwargs: Any) -> list[CxUserRequest]
      async def get_or_create_cx_user_request(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxUserRequest | None
      async def get_cx_user_request_with_ai_model(self, id: Any) -> tuple[Any, Any]
      async def get_cx_user_requests_with_ai_model(self) -> list[Any]
      async def get_cx_user_request_with_cx_conversation(self, id: Any) -> tuple[Any, Any]
      async def get_cx_user_requests_with_cx_conversation(self) -> list[Any]
      async def get_cx_user_request_with_cx_tool_call(self, id: Any) -> tuple[Any, Any]
      async def get_cx_user_requests_with_cx_tool_call(self) -> list[Any]
      async def get_cx_user_request_with_cx_request(self, id: Any) -> tuple[Any, Any]
      async def get_cx_user_requests_with_cx_request(self) -> list[Any]
      async def load_cx_user_requests_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def filter_cx_user_requests_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def load_cx_user_requests_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_cx_user_requests_by_user_id(self, user_id: Any) -> list[Any]
      async def load_cx_user_requests_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def filter_cx_user_requests_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def load_cx_user_requests_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_user_request_ids(self) -> set[Any]
  class CxUserRequestManager(CxUserRequestBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxUserRequestManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxUserRequest) -> None


---
Filepath: db/managers/ai_model.py  [python]

  class AiModelView(ModelView[AiModel]):
  class AiModelDTO(BaseDTO[AiModel]):
      async def _initialize_dto(self, model: AiModel) -> None
      async def _process_core_data(self, model: AiModel) -> None
      async def _process_metadata(self, model: AiModel) -> None
      async def _initial_validation(self, model: AiModel) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class AiModelBase(BaseManager[AiModel]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: AiModel) -> None
      async def create_ai_model(self, **data: Any) -> AiModel
      async def delete_ai_model(self, id: Any) -> bool
      async def get_ai_model_with_all_related(self, id: Any) -> tuple[AiModel, Any]
      async def load_ai_model_by_id(self, id: Any) -> AiModel
      async def load_ai_model(self, use_cache: bool = True, **kwargs: Any) -> AiModel
      async def update_ai_model(self, id: Any, **updates: Any) -> AiModel
      async def load_ai_models(self, **kwargs: Any) -> list[AiModel]
      async def filter_ai_models(self, **kwargs: Any) -> list[AiModel]
      async def get_or_create_ai_model(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> AiModel | None
      async def get_ai_model_with_ai_provider(self, id: Any) -> tuple[Any, Any]
      async def get_ai_models_with_ai_provider(self) -> list[Any]
      async def get_ai_model_with_ai_model_endpoint(self, id: Any) -> tuple[Any, Any]
      async def get_ai_models_with_ai_model_endpoint(self) -> list[Any]
      async def get_ai_model_with_ai_settings(self, id: Any) -> tuple[Any, Any]
      async def get_ai_models_with_ai_settings(self) -> list[Any]
      async def get_ai_model_with_recipe_model(self, id: Any) -> tuple[Any, Any]
      async def get_ai_models_with_recipe_model(self) -> list[Any]
      async def load_ai_models_by_name(self, name: Any) -> list[Any]
      async def filter_ai_models_by_name(self, name: Any) -> list[Any]
      async def load_ai_models_by_common_name(self, common_name: Any) -> list[Any]
      async def filter_ai_models_by_common_name(self, common_name: Any) -> list[Any]
      async def load_ai_models_by_provider(self, provider: Any) -> list[Any]
      async def filter_ai_models_by_provider(self, provider: Any) -> list[Any]
      async def load_ai_models_by_model_class(self, model_class: Any) -> list[Any]
      async def filter_ai_models_by_model_class(self, model_class: Any) -> list[Any]
      async def load_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]
      async def filter_ai_models_by_model_provider(self, model_provider: Any) -> list[Any]
      async def load_ai_models_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_ai_model_ids(self) -> set[Any]
  class AiModelManager(AiModelBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> AiModelManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: AiModel) -> None


---
Filepath: db/managers/cx_media.py  [python]

  class CxMediaView(ModelView[CxMedia]):
  class CxMediaDTO(BaseDTO[CxMedia]):
      async def _initialize_dto(self, model: CxMedia) -> None
      async def _process_core_data(self, model: CxMedia) -> None
      async def _process_metadata(self, model: CxMedia) -> None
      async def _initial_validation(self, model: CxMedia) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxMediaBase(BaseManager[CxMedia]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxMedia) -> None
      async def create_cx_media(self, **data: Any) -> CxMedia
      async def delete_cx_media(self, id: Any) -> bool
      async def get_cx_media_with_all_related(self, id: Any) -> tuple[CxMedia, Any]
      async def load_cx_media_by_id(self, id: Any) -> CxMedia
      async def load_cx_media(self, use_cache: bool = True, **kwargs: Any) -> CxMedia
      async def update_cx_media(self, id: Any, **updates: Any) -> CxMedia
      async def load_cx_medias(self, **kwargs: Any) -> list[CxMedia]
      async def filter_cx_medias(self, **kwargs: Any) -> list[CxMedia]
      async def get_or_create_cx_media(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxMedia | None
      async def get_cx_media_with_cx_conversation(self, id: Any) -> tuple[Any, Any]
      async def get_cx_medias_with_cx_conversation(self) -> list[Any]
      async def load_cx_medias_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def filter_cx_medias_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def load_cx_medias_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_cx_medias_by_user_id(self, user_id: Any) -> list[Any]
      async def load_cx_medias_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_media_ids(self) -> set[Any]
  class CxMediaManager(CxMediaBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxMediaManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxMedia) -> None


---
Filepath: db/managers/shortcut_categories.py  [python]

  class ShortcutCategoriesView(ModelView[ShortcutCategories]):
  class ShortcutCategoriesDTO(BaseDTO[ShortcutCategories]):
      async def _initialize_dto(self, model: ShortcutCategories) -> None
      async def _process_core_data(self, model: ShortcutCategories) -> None
      async def _process_metadata(self, model: ShortcutCategories) -> None
      async def _initial_validation(self, model: ShortcutCategories) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class ShortcutCategoriesBase(BaseManager[ShortcutCategories]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: ShortcutCategories) -> None
      async def create_shortcut_categories(self, **data: Any) -> ShortcutCategories
      async def delete_shortcut_categories(self, id: Any) -> bool
      async def get_shortcut_categories_with_all_related(self, id: Any) -> tuple[ShortcutCategories, Any]
      async def load_shortcut_categories_by_id(self, id: Any) -> ShortcutCategories
      async def load_shortcut_categories(self, use_cache: bool = True, **kwargs: Any) -> ShortcutCategories
      async def update_shortcut_categories(self, id: Any, **updates: Any) -> ShortcutCategories
      async def load_shortcut_category(self, **kwargs: Any) -> list[ShortcutCategories]
      async def filter_shortcut_category(self, **kwargs: Any) -> list[ShortcutCategories]
      async def get_or_create_shortcut_categories(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> ShortcutCategories | None
      async def get_shortcut_categories_with_self_reference(self, id: Any) -> tuple[Any, Any]
      async def get_shortcut_category_with_self_reference(self) -> list[Any]
      async def get_shortcut_categories_with_content_blocks(self, id: Any) -> tuple[Any, Any]
      async def get_shortcut_category_with_content_blocks(self) -> list[Any]
      async def get_shortcut_categories_with_prompt_shortcuts(self, id: Any) -> tuple[Any, Any]
      async def get_shortcut_category_with_prompt_shortcuts(self) -> list[Any]
      async def get_shortcut_categories_with_system_prompts_new(self, id: Any) -> tuple[Any, Any]
      async def get_shortcut_category_with_system_prompts_new(self) -> list[Any]
      async def load_shortcut_category_by_parent_category_id(self, parent_category_id: Any) -> list[Any]
      async def filter_shortcut_category_by_parent_category_id(self, parent_category_id: Any) -> list[Any]
      async def load_shortcut_category_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_shortcut_categories_ids(self) -> set[Any]
  class ShortcutCategoriesManager(ShortcutCategoriesBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> ShortcutCategoriesManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: ShortcutCategories) -> None


---
Filepath: db/managers/cx_request.py  [python]

  class CxRequestView(ModelView[CxRequest]):
  class CxRequestDTO(BaseDTO[CxRequest]):
      async def _initialize_dto(self, model: CxRequest) -> None
      async def _process_core_data(self, model: CxRequest) -> None
      async def _process_metadata(self, model: CxRequest) -> None
      async def _initial_validation(self, model: CxRequest) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxRequestBase(BaseManager[CxRequest]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxRequest) -> None
      async def create_cx_request(self, **data: Any) -> CxRequest
      async def delete_cx_request(self, id: Any) -> bool
      async def get_cx_request_with_all_related(self, id: Any) -> tuple[CxRequest, Any]
      async def load_cx_request_by_id(self, id: Any) -> CxRequest
      async def load_cx_request(self, use_cache: bool = True, **kwargs: Any) -> CxRequest
      async def update_cx_request(self, id: Any, **updates: Any) -> CxRequest
      async def load_cx_requests(self, **kwargs: Any) -> list[CxRequest]
      async def filter_cx_requests(self, **kwargs: Any) -> list[CxRequest]
      async def get_or_create_cx_request(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxRequest | None
      async def get_cx_request_with_ai_model(self, id: Any) -> tuple[Any, Any]
      async def get_cx_requests_with_ai_model(self) -> list[Any]
      async def get_cx_request_with_cx_conversation(self, id: Any) -> tuple[Any, Any]
      async def get_cx_requests_with_cx_conversation(self) -> list[Any]
      async def get_cx_request_with_cx_user_request(self, id: Any) -> tuple[Any, Any]
      async def get_cx_requests_with_cx_user_request(self) -> list[Any]
      async def load_cx_requests_by_user_request_id(self, user_request_id: Any) -> list[Any]
      async def filter_cx_requests_by_user_request_id(self, user_request_id: Any) -> list[Any]
      async def load_cx_requests_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def filter_cx_requests_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def load_cx_requests_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def filter_cx_requests_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def load_cx_requests_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_request_ids(self) -> set[Any]
  class CxRequestManager(CxRequestBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxRequestManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxRequest) -> None


---
Filepath: db/managers/cx_tool_call.py  [python]

  class CxToolCallView(ModelView[CxToolCall]):
  class CxToolCallDTO(BaseDTO[CxToolCall]):
      async def _initialize_dto(self, model: CxToolCall) -> None
      async def _process_core_data(self, model: CxToolCall) -> None
      async def _process_metadata(self, model: CxToolCall) -> None
      async def _initial_validation(self, model: CxToolCall) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxToolCallBase(BaseManager[CxToolCall]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxToolCall) -> None
      async def create_cx_tool_call(self, **data: Any) -> CxToolCall
      async def delete_cx_tool_call(self, id: Any) -> bool
      async def get_cx_tool_call_with_all_related(self, id: Any) -> tuple[CxToolCall, Any]
      async def load_cx_tool_call_by_id(self, id: Any) -> CxToolCall
      async def load_cx_tool_call(self, use_cache: bool = True, **kwargs: Any) -> CxToolCall
      async def update_cx_tool_call(self, id: Any, **updates: Any) -> CxToolCall
      async def load_cx_tool_calls(self, **kwargs: Any) -> list[CxToolCall]
      async def filter_cx_tool_calls(self, **kwargs: Any) -> list[CxToolCall]
      async def get_or_create_cx_tool_call(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxToolCall | None
      async def get_cx_tool_call_with_cx_conversation(self, id: Any) -> tuple[Any, Any]
      async def get_cx_tool_calls_with_cx_conversation(self) -> list[Any]
      async def get_cx_tool_call_with_cx_message(self, id: Any) -> tuple[Any, Any]
      async def get_cx_tool_calls_with_cx_message(self) -> list[Any]
      async def get_cx_tool_call_with_cx_user_request(self, id: Any) -> tuple[Any, Any]
      async def get_cx_tool_calls_with_cx_user_request(self) -> list[Any]
      async def get_cx_tool_call_with_self_reference(self, id: Any) -> tuple[Any, Any]
      async def get_cx_tool_calls_with_self_reference(self) -> list[Any]
      async def load_cx_tool_calls_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def filter_cx_tool_calls_by_conversation_id(self, conversation_id: Any) -> list[Any]
      async def load_cx_tool_calls_by_message_id(self, message_id: Any) -> list[Any]
      async def filter_cx_tool_calls_by_message_id(self, message_id: Any) -> list[Any]
      async def load_cx_tool_calls_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_cx_tool_calls_by_user_id(self, user_id: Any) -> list[Any]
      async def load_cx_tool_calls_by_request_id(self, request_id: Any) -> list[Any]
      async def filter_cx_tool_calls_by_request_id(self, request_id: Any) -> list[Any]
      async def load_cx_tool_calls_by_parent_call_id(self, parent_call_id: Any) -> list[Any]
      async def filter_cx_tool_calls_by_parent_call_id(self, parent_call_id: Any) -> list[Any]
      async def load_cx_tool_calls_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_tool_call_ids(self) -> set[Any]
  class CxToolCallManager(CxToolCallBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxToolCallManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxToolCall) -> None


---
Filepath: db/managers/cx_agent_memory.py  [python]

  class CxAgentMemoryView(ModelView[CxAgentMemory]):
  class CxAgentMemoryDTO(BaseDTO[CxAgentMemory]):
      async def _initialize_dto(self, model: CxAgentMemory) -> None
      async def _process_core_data(self, model: CxAgentMemory) -> None
      async def _process_metadata(self, model: CxAgentMemory) -> None
      async def _initial_validation(self, model: CxAgentMemory) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxAgentMemoryBase(BaseManager[CxAgentMemory]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None
      async def create_cx_agent_memory(self, **data: Any) -> CxAgentMemory
      async def delete_cx_agent_memory(self, id: Any) -> bool
      async def get_cx_agent_memory_with_all_related(self, id: Any) -> tuple[CxAgentMemory, Any]
      async def load_cx_agent_memory_by_id(self, id: Any) -> CxAgentMemory
      async def load_cx_agent_memory(self, use_cache: bool = True, **kwargs: Any) -> CxAgentMemory
      async def update_cx_agent_memory(self, id: Any, **updates: Any) -> CxAgentMemory
      async def load_cx_agent_memories(self, **kwargs: Any) -> list[CxAgentMemory]
      async def filter_cx_agent_memories(self, **kwargs: Any) -> list[CxAgentMemory]
      async def get_or_create_cx_agent_memory(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxAgentMemory | None
      async def load_cx_agent_memories_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_cx_agent_memories_by_user_id(self, user_id: Any) -> list[Any]
      async def load_cx_agent_memories_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_agent_memory_ids(self) -> set[Any]
  class CxAgentMemoryManager(CxAgentMemoryBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxAgentMemoryManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxAgentMemory) -> None


---
Filepath: db/managers/user_tables.py  [python]

  class UserTablesView(ModelView[UserTables]):
  class UserTablesDTO(BaseDTO[UserTables]):
      async def _initialize_dto(self, model: UserTables) -> None
      async def _process_core_data(self, model: UserTables) -> None
      async def _process_metadata(self, model: UserTables) -> None
      async def _initial_validation(self, model: UserTables) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class UserTablesBase(BaseManager[UserTables]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: UserTables) -> None
      async def create_user_tables(self, **data: Any) -> UserTables
      async def delete_user_tables(self, id: Any) -> bool
      async def get_user_tables_with_all_related(self, id: Any) -> tuple[UserTables, Any]
      async def load_user_tables_by_id(self, id: Any) -> UserTables
      async def load_user_tables(self, use_cache: bool = True, **kwargs: Any) -> UserTables
      async def update_user_tables(self, id: Any, **updates: Any) -> UserTables
      async def load_user_table(self, **kwargs: Any) -> list[UserTables]
      async def filter_user_table(self, **kwargs: Any) -> list[UserTables]
      async def get_or_create_user_tables(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> UserTables | None
      async def get_user_tables_with_table_data(self, id: Any) -> tuple[Any, Any]
      async def get_user_table_with_table_data(self) -> list[Any]
      async def get_user_tables_with_table_fields(self, id: Any) -> tuple[Any, Any]
      async def get_user_table_with_table_fields(self) -> list[Any]
      async def load_user_table_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_user_table_by_user_id(self, user_id: Any) -> list[Any]
      async def load_user_table_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_user_tables_ids(self) -> set[Any]
  class UserTablesManager(UserTablesBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> UserTablesManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: UserTables) -> None


---
Filepath: db/managers/cx_conversation.py  [python]

  class CxConversationView(ModelView[CxConversation]):
  class CxConversationDTO(BaseDTO[CxConversation]):
      async def _initialize_dto(self, model: CxConversation) -> None
      async def _process_core_data(self, model: CxConversation) -> None
      async def _process_metadata(self, model: CxConversation) -> None
      async def _initial_validation(self, model: CxConversation) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class CxConversationBase(BaseManager[CxConversation]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: CxConversation) -> None
      async def create_cx_conversation(self, **data: Any) -> CxConversation
      async def delete_cx_conversation(self, id: Any) -> bool
      async def get_cx_conversation_with_all_related(self, id: Any) -> tuple[CxConversation, Any]
      async def load_cx_conversation_by_id(self, id: Any) -> CxConversation
      async def load_cx_conversation(self, use_cache: bool = True, **kwargs: Any) -> CxConversation
      async def update_cx_conversation(self, id: Any, **updates: Any) -> CxConversation
      async def load_cx_conversations(self, **kwargs: Any) -> list[CxConversation]
      async def filter_cx_conversations(self, **kwargs: Any) -> list[CxConversation]
      async def get_or_create_cx_conversation(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> CxConversation | None
      async def get_cx_conversation_with_ai_model(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_ai_model(self) -> list[Any]
      async def get_cx_conversation_with_self_reference(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_self_reference(self) -> list[Any]
      async def get_cx_conversation_with_cx_tool_call(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_cx_tool_call(self) -> list[Any]
      async def get_cx_conversation_with_cx_message(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_cx_message(self) -> list[Any]
      async def get_cx_conversation_with_cx_media(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_cx_media(self) -> list[Any]
      async def get_cx_conversation_with_cx_user_request(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_cx_user_request(self) -> list[Any]
      async def get_cx_conversation_with_cx_request(self, id: Any) -> tuple[Any, Any]
      async def get_cx_conversations_with_cx_request(self) -> list[Any]
      async def load_cx_conversations_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_cx_conversations_by_user_id(self, user_id: Any) -> list[Any]
      async def load_cx_conversations_by_forked_from_id(self, forked_from_id: Any) -> list[Any]
      async def filter_cx_conversations_by_forked_from_id(self, forked_from_id: Any) -> list[Any]
      async def load_cx_conversations_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def filter_cx_conversations_by_ai_model_id(self, ai_model_id: Any) -> list[Any]
      async def load_cx_conversations_by_parent_conversation_id(self, parent_conversation_id: Any) -> list[Any]
      async def filter_cx_conversations_by_parent_conversation_id(self, parent_conversation_id: Any) -> list[Any]
      async def load_cx_conversations_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_cx_conversation_ids(self) -> set[Any]
  class CxConversationManager(CxConversationBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> CxConversationManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: CxConversation) -> None


---
Filepath: db/managers/ai_provider.py  [python]

  class AiProviderView(ModelView[AiProvider]):
  class AiProviderDTO(BaseDTO[AiProvider]):
      async def _initialize_dto(self, model: AiProvider) -> None
      async def _process_core_data(self, model: AiProvider) -> None
      async def _process_metadata(self, model: AiProvider) -> None
      async def _initial_validation(self, model: AiProvider) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class AiProviderBase(BaseManager[AiProvider]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: AiProvider) -> None
      async def create_ai_provider(self, **data: Any) -> AiProvider
      async def delete_ai_provider(self, id: Any) -> bool
      async def get_ai_provider_with_all_related(self, id: Any) -> tuple[AiProvider, Any]
      async def load_ai_provider_by_id(self, id: Any) -> AiProvider
      async def load_ai_provider(self, use_cache: bool = True, **kwargs: Any) -> AiProvider
      async def update_ai_provider(self, id: Any, **updates: Any) -> AiProvider
      async def load_ai_providers(self, **kwargs: Any) -> list[AiProvider]
      async def filter_ai_providers(self, **kwargs: Any) -> list[AiProvider]
      async def get_or_create_ai_provider(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> AiProvider | None
      async def get_ai_provider_with_ai_settings(self, id: Any) -> tuple[Any, Any]
      async def get_ai_providers_with_ai_settings(self) -> list[Any]
      async def get_ai_provider_with_ai_model(self, id: Any) -> tuple[Any, Any]
      async def get_ai_providers_with_ai_model(self) -> list[Any]
      async def load_ai_providers_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_ai_provider_ids(self) -> set[Any]
  class AiProviderManager(AiProviderBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> AiProviderManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: AiProvider) -> None


---
Filepath: db/managers/prompt_builtins.py  [python]

  class PromptBuiltinsView(ModelView[PromptBuiltins]):
  class PromptBuiltinsDTO(BaseDTO[PromptBuiltins]):
      async def _initialize_dto(self, model: PromptBuiltins) -> None
      async def _process_core_data(self, model: PromptBuiltins) -> None
      async def _process_metadata(self, model: PromptBuiltins) -> None
      async def _initial_validation(self, model: PromptBuiltins) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class PromptBuiltinsBase(BaseManager[PromptBuiltins]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: PromptBuiltins) -> None
      async def create_prompt_builtins(self, **data: Any) -> PromptBuiltins
      async def delete_prompt_builtins(self, id: Any) -> bool
      async def get_prompt_builtins_with_all_related(self, id: Any) -> tuple[PromptBuiltins, Any]
      async def load_prompt_builtins_by_id(self, id: Any) -> PromptBuiltins
      async def load_prompt_builtins(self, use_cache: bool = True, **kwargs: Any) -> PromptBuiltins
      async def update_prompt_builtins(self, id: Any, **updates: Any) -> PromptBuiltins
      async def load_prompt_builtin(self, **kwargs: Any) -> list[PromptBuiltins]
      async def filter_prompt_builtin(self, **kwargs: Any) -> list[PromptBuiltins]
      async def get_or_create_prompt_builtins(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> PromptBuiltins | None
      async def get_prompt_builtins_with_prompts(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_builtin_with_prompts(self) -> list[Any]
      async def get_prompt_builtins_with_prompt_shortcuts(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_builtin_with_prompt_shortcuts(self) -> list[Any]
      async def get_prompt_builtins_with_prompt_actions(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_builtin_with_prompt_actions(self) -> list[Any]
      async def load_prompt_builtin_by_created_by_user_id(self, created_by_user_id: Any) -> list[Any]
      async def filter_prompt_builtin_by_created_by_user_id(self, created_by_user_id: Any) -> list[Any]
      async def load_prompt_builtin_by_source_prompt_id(self, source_prompt_id: Any) -> list[Any]
      async def filter_prompt_builtin_by_source_prompt_id(self, source_prompt_id: Any) -> list[Any]
      async def load_prompt_builtin_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_prompt_builtins_ids(self) -> set[Any]
  class PromptBuiltinsManager(PromptBuiltinsBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> PromptBuiltinsManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: PromptBuiltins) -> None


---
Filepath: db/managers/prompts.py  [python]

  class PromptsView(ModelView[Prompts]):
  class PromptsDTO(BaseDTO[Prompts]):
      async def _initialize_dto(self, model: Prompts) -> None
      async def _process_core_data(self, model: Prompts) -> None
      async def _process_metadata(self, model: Prompts) -> None
      async def _initial_validation(self, model: Prompts) -> None
      async def _final_validation(self) -> bool
      async def get_validated_dict(self) -> dict[str, Any]
  class PromptsBase(BaseManager[Prompts]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None) -> None
      def _initialize_manager(self) -> None
      async def _initialize_runtime_data(self, item: Prompts) -> None
      async def create_prompts(self, **data: Any) -> Prompts
      async def delete_prompts(self, id: Any) -> bool
      async def get_prompts_with_all_related(self, id: Any) -> tuple[Prompts, Any]
      async def load_prompts_by_id(self, id: Any) -> Prompts
      async def load_prompts(self, use_cache: bool = True, **kwargs: Any) -> Prompts
      async def update_prompts(self, id: Any, **updates: Any) -> Prompts
      async def load_prompt(self, **kwargs: Any) -> list[Prompts]
      async def filter_prompt(self, **kwargs: Any) -> list[Prompts]
      async def get_or_create_prompts(self, defaults: dict[str, Any] | None = None, **kwargs: Any) -> Prompts | None
      async def get_prompts_with_prompt_apps(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_with_prompt_apps(self) -> list[Any]
      async def get_prompts_with_system_prompts_new(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_with_system_prompts_new(self) -> list[Any]
      async def get_prompts_with_prompt_builtins(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_with_prompt_builtins(self) -> list[Any]
      async def get_prompts_with_prompt_actions(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_with_prompt_actions(self) -> list[Any]
      async def get_prompts_with_system_prompts(self, id: Any) -> tuple[Any, Any]
      async def get_prompt_with_system_prompts(self) -> list[Any]
      async def load_prompt_by_user_id(self, user_id: Any) -> list[Any]
      async def filter_prompt_by_user_id(self, user_id: Any) -> list[Any]
      async def load_prompt_by_ids(self, ids: list[Any]) -> list[Any]
      def add_computed_field(self, field: str) -> None
      def add_relation_field(self, field: str) -> None
      def active_prompts_ids(self) -> set[Any]
  class PromptsManager(PromptsBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> PromptsManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: Prompts) -> None
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrx_orm, matrx_utils
**Internal modules:** db.models
<!-- /AUTO:dependencies -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `db/custom/ai_model_manager.py` | `AiModelBase()` |
| `instructions/content_blocks_manager.py` | `ContentBlocksDTO()` |
| `db/custom/cx_managers.py` | `CxAgentMemoryBase()` |
| `db/custom/cx_managers.py` | `CxConversationBase()` |
| `db/custom/cx_managers.py` | `CxMediaBase()` |
| `db/custom/cx_managers.py` | `CxMessageBase()` |
| `db/custom/cx_managers.py` | `CxRequestBase()` |
| `db/custom/cx_managers.py` | `CxToolCallBase()` |
| `db/custom/cx_managers.py` | `CxUserRequestBase()` |
| `agents/manager.py` | `PromptBuiltinsBase()` |
| `agents/manager.py` | `PromptsBase()` |
| `tools/tools_db.py` | `ToolsBase()` |
<!-- /AUTO:callers -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "db/managers",
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
