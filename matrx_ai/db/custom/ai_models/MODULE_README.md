# `db.custom.ai_models` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `db/custom/ai_models` |
| Last generated | 2026-03-01 00:10 |
| Output file | `db/custom/ai_models/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py db/custom/ai_models --mode signatures
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
db/custom/ai_models/
├── MODULE_README.md
├── __init__.py
├── ai_model_base.py
├── ai_model_dto.py
├── ai_model_manager.py
├── ai_model_validator.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
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
Filepath: db/custom/ai_models/ai_model_base.py  [python]

  class AiModelBase(BaseManager[AiModel]):
      def __init__(self, dto_class: type[Any] | None = None, view_class: type[Any] | None = None, fetch_on_init_limit: int = 200, fetch_on_init_with_warnings_off: str = 'YES_I_KNOW_WHAT_IM_DOING_TURN_OFF_WARNINGS_FOR_LIMIT_100') -> None
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
  async def main()


---
Filepath: db/custom/ai_models/ai_model_dto.py  [python]

  DEFAULT_MAX_TOKENS = 4096
  class AiModelDTO(BaseDTO):
      async def _initialize_dto(self, model: AiModel) -> None
      async def _process_core_data(self, ai_model_item: AiModel) -> None
      async def _process_metadata(self, ai_model_item)
      async def _initial_validation(self, ai_model_item)
      async def _final_validation(self)
      async def get_validated_dict(self)


---
Filepath: db/custom/ai_models/ai_model_manager.py  [python]

  class AiModelManager(AiModelBase):
      def __new__(cls, *args: Any, **kwargs: Any) -> AiModelManager
      def __init__(self) -> None
      async def _initialize_runtime_data(self, item: AiModel) -> None
      async def load_all_models(self, update_data_in_code: bool = False)
      async def load_model(self, id_or_name: str) -> AiModel | None
      async def load_model_get_string_uuid(self, id_or_name: str) -> str | None
      async def load_model_by_id(self, model_id: str) -> AiModel | None
      async def load_models_by_name(self, model_name: str) -> list[AiModel]
      async def load_models_by_provider(self, provider: str) -> list[AiModel]
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `db/custom/tests/ai_model_tests.py` | `AiModelManager()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** matrix, matrx_orm, matrx_utils
**Internal modules:** db.models
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "db/custom/ai_models",
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
