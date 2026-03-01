# `providers` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `providers` |
| Last generated | 2026-03-01 00:10 |
| Output file | `providers/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py providers --mode signatures
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

> Auto-generated. 25 files across 8 directories.

```
providers/
├── MODULE_README.md
├── __init__.py
├── anthropic/
│   ├── __init__.py
│   ├── anthropic_api.py
│   ├── translator.py
├── cerebras/
│   ├── __init__.py
│   ├── cerebras_api.py
│   ├── translator.py
├── errors.py
├── google/
│   ├── __init__.py
│   ├── google_api.py
│   ├── translator.py
├── groq/
│   ├── __init__.py
│   ├── groq_api.py
│   ├── translator.py
├── openai/
│   ├── __init__.py
│   ├── openai_api.py
│   ├── translator.py
├── together/
│   ├── __init__.py
│   ├── together_api.py
│   ├── translator.py
├── unified_client.py
├── xai/
│   ├── __init__.py
│   ├── translator.py
│   ├── xai_api.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: providers/__init__.py  [python]



---
Filepath: providers/errors.py  [python]

  class RetryableError:
      def get_backoff_delay(self, attempt: int) -> float
  def _extract_status_code(exception: Exception) -> int | None
  def _retry_after_from_status(status_code: int) -> float
  def _classify_by_status(status_code: int, provider: str, message: str) -> RetryableError
  def _fallback_classify(error_str: str, provider: str) -> RetryableError
  def classify_google_error(exception: Exception) -> RetryableError
  def classify_openai_error(exception: Exception) -> RetryableError
  def classify_anthropic_error(exception: Exception) -> RetryableError
  def classify_provider_error(provider: str, exception: Exception) -> RetryableError


---
Filepath: providers/unified_client.py  [python]

  API_CLASS_TO_ENDPOINT = {15 keys}
  class UnifiedAIClient:
      def __init__(self)
      async def execute(self, request: AIMatrixRequest) -> UnifiedResponse
      async def translate_request(self, request: AIMatrixRequest) -> dict[str, Any]
      def translate_response(self, provider: Literal['openai', 'anthropic', 'gemini', 'together', 'groq', 'xai', 'cerebras'], response: dict[str, Any]) -> UnifiedResponse


---
Filepath: providers/together/__init__.py  [python]



---
Filepath: providers/together/together_api.py  [python]

  DEBUG_OVERRIDE = False
  class TogetherChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: Any, model: str = '') -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse


---
Filepath: providers/together/translator.py  [python]

  class TogetherTranslator:
      def to_together(self, config: UnifiedConfig) -> dict[str, Any]
      def from_together(self, response: Any) -> UnifiedResponse


---
Filepath: providers/openai/__init__.py  [python]



---
Filepath: providers/openai/translator.py  [python]

  class OpenAITranslator:
      def to_openai(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def from_openai(self, response: OpenAIResponse, matrx_model_name: str) -> UnifiedResponse


---
Filepath: providers/openai/openai_api.py  [python]

  DEBUG_OVERRIDE = False
  class OpenAIChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: OpenAIResponse) -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, matrx_model_name: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, matrx_model_name: str) -> UnifiedResponse
      async def _handle_event(self, event: Any, emitter: Emitter)
      async def _debug_event(self, event: Any)


---
Filepath: providers/google/__init__.py  [python]



---
Filepath: providers/google/google_api.py  [python]

  LOCAL_DEBUG = False
  class GoogleChat:
      def __init__(self)
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _handle_part(self, part: Part, emitter: Emitter)
      async def _debug_part(self, part: Part)


---
Filepath: providers/google/translator.py  [python]

  class GoogleProviderConfig(TypedDict):
  class GoogleTranslator:
      def to_google(self, config: UnifiedConfig, api_class: str) -> GoogleProviderConfig
      def from_google(self, chunks: list[GenerateContentResponse], matrx_model_name: str) -> UnifiedResponse


---
Filepath: providers/anthropic/__init__.py  [python]



---
Filepath: providers/anthropic/translator.py  [python]

  class AnthropicTranslator:
      def to_anthropic(self, config: UnifiedConfig, api_class: str = 'anthropic_standard') -> dict[str, Any]
      def from_anthropic(self, response: dict[str, Any], matrx_model_name: str) -> UnifiedResponse


---
Filepath: providers/anthropic/anthropic_api.py  [python]

  DEBUG_OVERRIDE = False
  class AnthropicChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: Any, matrx_model_name: str = '') -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, matrx_model_name: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, matrx_model_name: str) -> UnifiedResponse
      async def _handle_event(self, event: Any, emitter: Emitter)
      async def _handle_content_block(self, block: Any, emitter: Emitter)
      async def _debug_event(self, event: Any)


---
Filepath: providers/groq/__init__.py  [python]



---
Filepath: providers/groq/groq_api.py  [python]

  DEBUG_OVERRIDE = False
  class GroqChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: Any, model: str = '') -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse


---
Filepath: providers/groq/translator.py  [python]

  class GroqTranslator:
      def to_groq(self, config: UnifiedConfig) -> dict[str, Any]
      def from_groq(self, response: Any) -> UnifiedResponse


---
Filepath: providers/cerebras/__init__.py  [python]



---
Filepath: providers/cerebras/cerebras_api.py  [python]

  DEBUG_OVERRIDE = False
  class CerebrasChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: Any, model: str = '') -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse


---
Filepath: providers/cerebras/translator.py  [python]

  class CerebrasTranslator:
      def to_cerebras(self, config: UnifiedConfig) -> dict[str, Any]
      def from_cerebras(self, response: Any) -> UnifiedResponse


---
Filepath: providers/xai/__init__.py  [python]



---
Filepath: providers/xai/xai_api.py  [python]

  DEBUG_OVERRIDE = False
  class XAIChat:
      def __init__(self, debug: bool = False)
      def to_provider_config(self, config: UnifiedConfig, api_class: str) -> dict[str, Any]
      def to_unified_response(self, response: Any, model: str = '') -> UnifiedResponse
      async def execute(self, unified_config: UnifiedConfig, api_class: str, debug: bool = False) -> UnifiedResponse
      async def _execute_non_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse
      async def _execute_streaming(self, config_data: dict[str, Any], emitter: Emitter, model: str) -> UnifiedResponse


---
Filepath: providers/xai/translator.py  [python]

  class XAITranslator:
      def to_xai(self, config: UnifiedConfig) -> dict[str, Any]
      def from_xai(self, response: Any) -> UnifiedResponse
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `db/custom/tests/cx_manager_tests.py` | `OpenAITranslator()` |
| `orchestrator/executor.py` | `RetryableError()` |
| `orchestrator/executor.py` | `UnifiedAIClient()` |
| `orchestrator/executor.py` | `classify_provider_error()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** anthropic, cerebras, google, groq, matrx_utils, openai, rich, together
**Internal modules:** config, context.app_context, context.emitter_protocol, db.custom, db.models, orchestrator.requests, processing.audio, tools.registry
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "providers",
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
