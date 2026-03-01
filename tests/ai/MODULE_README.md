# `tests.ai` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `tests/ai` |
| Last generated | 2026-03-01 00:14 |
| Output file | `tests/ai/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py tests/ai --mode signatures
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

> Auto-generated. 8 files across 1 directories.

```
tests/ai/
├── MODULE_README.md
├── __init__.py
├── execution_test.py
├── groq_transcription_test.py
├── small_test.py
├── test_context.py
├── test_error_handling.py
├── test_translations.py
# excluded: 5 .json, 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: tests/ai/__init__.py  [python]



---
Filepath: tests/ai/test_error_handling.py  [python]

  def test_google_503_high_demand()
  def test_google_429_rate_limit()
  def test_google_500_server_error()
  def test_google_network_error()
  def test_google_non_retryable()
  def test_openai_rate_limit()
  def test_openai_server_error()
  def test_anthropic_overloaded()
  def test_backoff_calculation()
  def test_custom_retry_after()
  def test_provider_classification()
  def run_all_tests()


---
Filepath: tests/ai/groq_transcription_test.py  [python]

  def test_basic_transcription()
  def test_translation()
  def test_audio_content_integration()
  def test_unified_message_with_audio()
  def test_url_transcription()
  def test_quality_metrics_analysis()
  def test_model_comparison()


---
Filepath: tests/ai/test_context.py  [python]

  def _require_env(key: str, validator: callable | None = None, hint: str = '') -> str
  def _optional_env(key: str) -> str | None
  def _is_valid_uuid(val: str) -> bool
  def _is_valid_email(val: str) -> bool
  def get_developer_user_id() -> str
  def get_test_email() -> str
  def get_test_conversation_id() -> str
  def get_test_project_id() -> str | None
  def get_test_organization_id() -> str | None
  def create_test_app_context(*, conversation_id: str | None = None, project_id: str | None = None, organization_id: str | None = None, emitter: Emitter | None = None, label: str = 'test', debug: bool = True, is_admin: bool = False, new_conversation: bool = False) -> Token
  def create_test_tool_context(tool_name: str, *, call_id: str | None = None, iteration: int = 0, user_role: str = 'user', cost_budget_remaining: float | None = None) -> ToolContext


---
Filepath: tests/ai/execution_test.py  [python]

  LOCAL_USER_ID = os.getenv('LOCAL_USER_ID')
  async def register_all_tools()
  async def test_autonomous_execution(config: dict, conversation_id: str, new_conversation: bool = False, debug: bool = False)
  def clean_up_response(response)
  async def run()


---
Filepath: tests/ai/small_test.py  [python]

  DEBUG_OVERRIDE = False
  def test_debug_override(debug: bool = False)


---
Filepath: tests/ai/test_translations.py  [python]

  async def test_translation(settings_to_use)
  async def test_execution(settings_to_use)
```
<!-- /AUTO:signatures -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** client, dotenv, initialize_systems, matrx_utils, rich
**Internal modules:** config.unified_config, context.app_context, context.console_emitter, context.emitter_protocol, media.audio, orchestrator.executor, tools.models, tools.registry
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "tests/ai",
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
