# `config` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `config` |
| Last generated | 2026-03-01 00:10 |
| Output file | `config/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py config --mode signatures
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

> Auto-generated. 13 files across 1 directories.

```
config/
├── MODULE_README.md
├── __init__.py
├── config_utils.py
├── enums.py
├── extra_config.py
├── finish_reason.py
├── media_config.py
├── message_config.py
├── thinking_config.py
├── tools_config.py
├── unified_config.py
├── unified_content.py
├── usage_config.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: config/enums.py  [python]

  class Role(str, Enum):
      def __str__(self) -> str
  class ContentType(str, Enum):
      def __str__(self) -> str
  class Provider(str, Enum):
      def __str__(self) -> str


---
Filepath: config/__init__.py  [python]



---
Filepath: config/unified_config.py  [python]

  class UnifiedConfig:
      def __post_init__(self)
      def _resolve_message_patterns(self) -> None
      def _resolve_system_instruction(raw: str | dict | SystemInstruction | None) -> str | None
      def from_dict(cls, data: dict[str, Any]) -> 'UnifiedConfig'
      def _normalize_tool_choice(self, tool_choice: Any) -> Literal['none', 'auto', 'required'] | None
      def to_dict(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def append_user_message(self, text: str, **kwargs) -> None
      def append_or_extend_user_text(self, text: str, **kwargs) -> None
      def append_or_extend_user_input(self, user_input: str | list[dict[str, Any]]) -> None
      def replace_variables(self, variables: dict[str, Any]) -> None
      def get_last_output(self) -> str
  class UnifiedResponse:
      def __post_init__(self)
      def to_dict(self) -> dict[str, Any]


---
Filepath: config/usage_config.py  [python]

  class PricingTier:
  class ModelPricing:
      def get_tier(self, total_input_tokens: int) -> PricingTier | None
  class ModelUsageSummary:
  class UsageTotals:
  class AggregatedUsage:
      def to_dict(self) -> dict[str, Any]
  class TokenUsage:
      def total_tokens(self) -> int
      def calculate_cost(self, pricing_lookup: dict[str, ModelPricing] | None = None) -> float | None
      def __add__(self, other: 'TokenUsage') -> 'TokenUsage'
      def from_gemini(cls, usage_metadata: dict[str, Any], matrx_model_name: str = '', provider_model_name: str = '', response_id: str = '') -> 'TokenUsage'
      def from_openai(cls, usage: OpenAIResponseUsage, matrx_model_name: str, provider_model_name: str, response_id: str = '') -> 'TokenUsage'
      def from_anthropic(cls, usage: AnthropicUsage, matrx_model_name: str, response_id: str = '') -> 'TokenUsage'
      def aggregate_by_model(usage_list: list['TokenUsage']) -> AggregatedUsage


---
Filepath: config/finish_reason.py  [python]

  class FinishReason(str, Enum):
      def __str__(self) -> str
      def is_success(self) -> bool
      def is_retryable(self) -> bool
      def is_error(self) -> bool
      def from_google(cls, google_reason: Any) -> 'FinishReason'
      def from_anthropic(cls, stop_reason: str) -> 'FinishReason'
      def to_anthropic(cls, finish_reason: 'FinishReason') -> str


---
Filepath: config/extra_config.py  [python]

  class CodeExecutionContent:
      def to_google(self) -> dict[str, Any]
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def to_storage_dict(self) -> dict[str, Any]
      def from_google(cls, part: Part) -> 'CodeExecutionContent | None'
  class CodeExecutionResultContent:
      def to_google(self) -> dict[str, Any]
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def to_storage_dict(self) -> dict[str, Any]
      def from_google(cls, part: Part) -> 'CodeExecutionResultContent | None'
  class WebSearchCallContent:
      def get_output(self) -> str | None
      def from_openai(cls, content_item: OpenAIResponseFunctionWebSearch) -> 'WebSearchCallContent | None'
      def to_openai(self) -> dict[str, Any]
      def to_anthropic(self) -> dict[str, Any]
      def to_google(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]


---
Filepath: config/thinking_config.py  [python]

  class ThinkingConfig:
      def to_openai_reasoning(self) -> Reasoning
      def to_google_thinking_legacy(self) -> dict[str, Any]
      def to_google_thinking_3(self, model_name: str | None = None) -> dict[str, Any]
      def to_anthropic_thinking(self, current_max_tokens: int | None = None) -> dict[str, Any] | None
      def to_anthropic_adaptive_thinking(self, current_max_tokens: int | None = None) -> dict[str, Any] | None
      def to_cerebras_reasoning(self) -> str | None
      def from_settings(cls, settings: Any) -> 'ThinkingConfig'


---
Filepath: config/media_config.py  [python]

  MediaKind = Literal['image', 'audio', 'video', 'document', 'youtube']
  MediaContent = ImageContent | AudioContent | VideoContent | YouTubeVideoContent | DocumentContent
  class ImageContent:
      def __post_init__(self)
      def get_output(self) -> str | None
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'ImageContent | None'
      def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
  class AudioContent:
      def __post_init__(self)
      def get_output(self) -> str | None
      def get_transcription(self, force_refresh: bool = False) -> str | None
      def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'AudioContent | None'
  class VideoContent:
      def __post_init__(self)
      def get_output(self) -> str | None
      def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'VideoContent | None'
  class YouTubeVideoContent:
      def get_output(self) -> str
      def to_storage_dict(self) -> dict[str, Any]
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'YouTubeVideoContent | None'
  class DocumentContent:
      def __post_init__(self)
      def get_output(self) -> str | None
      def to_dict(self, truncate_base64: bool = True) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'DocumentContent | None'
  def reconstruct_media_content(block: dict[str, Any]) -> MediaContent | None


---
Filepath: config/message_config.py  [python]

  class UnifiedMessage:
      def parse_content(content_data: str | list[Any]) -> list[UnifiedContent]
      def from_dict(cls, data: dict[str, Any]) -> 'UnifiedMessage'
      def from_cx_message(cls, message: CxMessage) -> 'UnifiedMessage'
      def from_openai_item(cls, item: OpenAIResponseOutputItem) -> 'UnifiedMessage | None'
      def from_anthropic_content(cls, role: str, content: list[dict[str, Any]], id: str) -> 'UnifiedMessage | None'
      def to_google_content(self) -> dict[str, Any] | None
      def to_openai_items(self) -> list[dict[str, Any]] | dict[str, Any] | None
      def to_anthropic_blocks(self) -> list[dict[str, Any]]
      def replace_variables(self, variables: dict[str, Any]) -> None
      def to_storage_dict(self) -> dict[str, Any]
      def get_output(self) -> str
  class MessageList:
      def __post_init__(self)
      def __iter__(self)
      def __len__(self)
      def __getitem__(self, index)
      def __setitem__(self, index, value)
      def append(self, message: 'UnifiedMessage | dict[str, Any]') -> None
      def extend(self, messages: 'list[UnifiedMessage] | MessageList') -> None
      def insert(self, index: int, message: 'UnifiedMessage | dict[str, Any]') -> None
      def pop(self, index: int = -1) -> 'UnifiedMessage'
      def remove(self, message: 'UnifiedMessage') -> None
      def clear(self) -> None
      def filter_by_role(self, *roles: str) -> 'MessageList'
      def exclude_roles(self, *roles: str) -> 'MessageList'
      def has_role(self, role: str) -> bool
      def get_last_by_role(self, role: str) -> 'UnifiedMessage | None'
      def get_last_output(self) -> str
      def count_by_role(self, role: str) -> int
      def append_user_text(self, text: str, **kwargs) -> None
      def append_or_extend_user_text(self, text: str, **kwargs) -> None
      def append_or_extend_user_items(self, items: list[dict[str, Any]]) -> None
      def append_or_extend_user_input(self, user_input: str | list[dict[str, Any]]) -> None
      def _is_last_message_user(self) -> bool
      def append_assistant_text(self, text: str, **kwargs) -> None
      def to_list(self) -> list['UnifiedMessage']
      def to_dict_list(self) -> list[dict[str, Any]]
      def replace_variables(self, variables: dict[str, Any]) -> None


---
Filepath: config/config_utils.py  [python]

  def truncate_base64_in_dict(d: Any, min_length: int = 100) -> Any


---
Filepath: config/tools_config.py  [python]

  class ToolCallContent:
      def get_output(self) -> str
      def to_google(self) -> dict[str, Any]
      def to_openai(self) -> dict[str, Any]
      def to_anthropic(self) -> dict[str, Any]
      def _sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]
      def to_dict(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def from_google(cls, part: Part) -> 'ToolCallContent | None'
      def from_openai(cls, item: OpenAIResponseFunctionToolCall) -> 'ToolCallContent | None'
      def from_anthropic(cls, content_block: dict[str, Any]) -> 'ToolCallContent | None'
  class ToolResultContent:
      def get_output(self) -> str
      def to_google(self) -> dict[str, Any]
      def to_openai(self) -> dict[str, Any]
      def to_anthropic(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def from_google(cls, part: Part) -> 'ToolResultContent | None'


---
Filepath: config/unified_content.py  [python]

  UnifiedContent = TextContent | ImageContent | AudioContent | VideoContent | YouTubeVideoContent | DocumentContent | ToolCallContent | Too ...
  class TextContent:
      def get_output(self) -> str
      def replace_variables(self, variables: dict[str, Any]) -> None
      def append_text(self, text: str, separator: str = '\n') -> None
      def to_google(self) -> dict[str, Any]
      def to_openai(self, role: str | None = None) -> dict[str, Any]
      def to_anthropic(self) -> dict[str, Any]
      def _sanitize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]
      def to_dict(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def from_openai(cls, content_item: OpenAIResponseOutputText, id: str) -> 'TextContent | None'
      def from_google(cls, part: Part) -> 'TextContent | None'
      def from_anthropic(cls, content_block: dict[str, Any]) -> 'TextContent | None'
  class ThinkingContent:
      def get_output(self) -> str
      def _sanitize_signature(self) -> str
      def to_dict(self) -> dict[str, Any]
      def to_storage_dict(self) -> dict[str, Any]
      def __repr__(self) -> str
      def to_google(self) -> dict[str, Any] | None
      def to_openai(self) -> dict[str, Any] | None
      def to_anthropic(self) -> dict[str, Any] | None
      def from_google(cls, part: Part) -> 'ThinkingContent | None'
      def from_anthropic(cls, content_block: dict[str, Any]) -> 'ThinkingContent | None'
      def from_openai(cls, item: OpenAIResponseReasoningItem) -> 'ThinkingContent | None'
  def reconstruct_content(block: dict[str, Any]) -> UnifiedContent
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `agents/definition.py` | `AggregatedUsage()` |
| `orchestrator/requests.py` | `AggregatedUsage()` |
| `processing/audio/audio_preprocessing.py` | `AudioContent()` |
| `providers/google/translator.py` | `AudioContent()` |
| `tests/ai/groq_transcription_test.py` | `AudioContent()` |
| `providers/google/translator.py` | `CodeExecutionContent()` |
| `providers/google/translator.py` | `CodeExecutionResultContent()` |
| `providers/google/translator.py` | `DocumentContent()` |
| `orchestrator/recovery_logic.py` | `FinishReason()` |
| `providers/anthropic/translator.py` | `FinishReason()` |
| `providers/cerebras/translator.py` | `FinishReason()` |
| `providers/google/translator.py` | `FinishReason()` |
| `providers/groq/groq_api.py` | `FinishReason()` |
| `providers/groq/translator.py` | `FinishReason()` |
| `providers/openai/translator.py` | `FinishReason()` |
| `providers/together/together_api.py` | `FinishReason()` |
| `providers/together/translator.py` | `FinishReason()` |
| `providers/xai/translator.py` | `FinishReason()` |
| `providers/xai/xai_api.py` | `FinishReason()` |
| `providers/google/translator.py` | `ImageContent()` |
| `orchestrator/requests.py` | `MessageList()` |
| `processing/audio/audio_preprocessing.py` | `MessageList()` |
| `processing/audio/audio_preprocessing.py` | `TextContent()` |
| `providers/cerebras/cerebras_api.py` | `TextContent()` |
| `providers/cerebras/translator.py` | `TextContent()` |
| `providers/google/translator.py` | `TextContent()` |
| `providers/groq/groq_api.py` | `TextContent()` |
| `providers/groq/translator.py` | `TextContent()` |
| `providers/together/together_api.py` | `TextContent()` |
| `providers/together/translator.py` | `TextContent()` |
| `providers/xai/translator.py` | `TextContent()` |
| `providers/xai/xai_api.py` | `TextContent()` |
| `tests/ai/groq_transcription_test.py` | `TextContent()` |
| `tests/openai/openai_translation_test.py` | `TextContent()` |
| `providers/anthropic/translator.py` | `ThinkingConfig()` |
| `providers/google/translator.py` | `ThinkingConfig()` |
| `providers/openai/translator.py` | `ThinkingConfig()` |
| `providers/cerebras/cerebras_api.py` | `ThinkingContent()` |
| `providers/cerebras/translator.py` | `ThinkingContent()` |
| `providers/google/translator.py` | `ThinkingContent()` |
| `tests/openai/openai_translation_test.py` | `ThinkingContent()` |
| `agent_runners/research.py` | `TokenUsage()` |
| `agents/definition.py` | `TokenUsage()` |
| `orchestrator/executor.py` | `TokenUsage()` |
| `orchestrator/requests.py` | `TokenUsage()` |
| `processing/audio/audio_preprocessing.py` | `TokenUsage()` |
| `providers/anthropic/translator.py` | `TokenUsage()` |
| `providers/cerebras/translator.py` | `TokenUsage()` |
| `providers/google/translator.py` | `TokenUsage()` |
| `providers/groq/groq_api.py` | `TokenUsage()` |
| `providers/groq/translator.py` | `TokenUsage()` |
| `providers/openai/translator.py` | `TokenUsage()` |
| `providers/together/together_api.py` | `TokenUsage()` |
| `providers/together/translator.py` | `TokenUsage()` |
| `providers/xai/translator.py` | `TokenUsage()` |
| `providers/xai/xai_api.py` | `TokenUsage()` |
| `tools/handle_tool_calls.py` | `TokenUsage()` |
| `tools/implementations/_summarize_helper.py` | `TokenUsage()` |
| `tools/models.py` | `TokenUsage()` |
| `tools/tests/mimic_model_tests.py` | `TokenUsage()` |
| `orchestrator/executor.py` | `ToolCallContent()` |
| `providers/cerebras/cerebras_api.py` | `ToolCallContent()` |
| `providers/cerebras/translator.py` | `ToolCallContent()` |
| `providers/google/translator.py` | `ToolCallContent()` |
| `providers/groq/groq_api.py` | `ToolCallContent()` |
| `providers/groq/translator.py` | `ToolCallContent()` |
| `providers/together/together_api.py` | `ToolCallContent()` |
| `providers/together/translator.py` | `ToolCallContent()` |
| `providers/xai/translator.py` | `ToolCallContent()` |
| `providers/xai/xai_api.py` | `ToolCallContent()` |
| `tests/openai/openai_translation_test.py` | `ToolCallContent()` |
| `orchestrator/executor.py` | `ToolResultContent()` |
| `orchestrator/requests.py` | `ToolResultContent()` |
| `providers/cerebras/translator.py` | `ToolResultContent()` |
| `providers/google/translator.py` | `ToolResultContent()` |
| `providers/groq/translator.py` | `ToolResultContent()` |
| `providers/together/translator.py` | `ToolResultContent()` |
| `providers/xai/translator.py` | `ToolResultContent()` |
| `tests/openai/openai_translation_test.py` | `ToolResultContent()` |
| `agents/definition.py` | `UnifiedConfig()` |
| `agents/manager.py` | `UnifiedConfig()` |
| `agents/resolver.py` | `UnifiedConfig()` |
| `agents/types.py` | `UnifiedConfig()` |
| `app/core/ai_task.py` | `UnifiedConfig()` |
| `app/routers/chat.py` | `UnifiedConfig()` |
| `db/custom/cx_managers.py` | `UnifiedConfig()` |
| `orchestrator/executor.py` | `UnifiedConfig()` |
| `orchestrator/requests.py` | `UnifiedConfig()` |
| `providers/anthropic/anthropic_api.py` | `UnifiedConfig()` |
| `providers/anthropic/translator.py` | `UnifiedConfig()` |
| `providers/cerebras/cerebras_api.py` | `UnifiedConfig()` |
| `providers/cerebras/translator.py` | `UnifiedConfig()` |
| `providers/google/google_api.py` | `UnifiedConfig()` |
| `providers/google/translator.py` | `UnifiedConfig()` |
| `providers/groq/groq_api.py` | `UnifiedConfig()` |
| `providers/groq/translator.py` | `UnifiedConfig()` |
| `providers/openai/openai_api.py` | `UnifiedConfig()` |
| `providers/openai/translator.py` | `UnifiedConfig()` |
| `providers/together/together_api.py` | `UnifiedConfig()` |
| `providers/together/translator.py` | `UnifiedConfig()` |
| `providers/xai/translator.py` | `UnifiedConfig()` |
| `providers/xai/xai_api.py` | `UnifiedConfig()` |
| `tests/ai/execution_test.py` | `UnifiedConfig()` |
| `tests/openai/openai_translation_test.py` | `UnifiedConfig()` |
| `tools/implementations/_summarize_helper.py` | `UnifiedConfig()` |
| `agents/definition.py` | `UnifiedMessage()` |
| `db/custom/conversation_rebuild.py` | `UnifiedMessage()` |
| `orchestrator/executor.py` | `UnifiedMessage()` |
| `orchestrator/requests.py` | `UnifiedMessage()` |
| `processing/audio/audio_preprocessing.py` | `UnifiedMessage()` |
| `providers/anthropic/translator.py` | `UnifiedMessage()` |
| `providers/cerebras/translator.py` | `UnifiedMessage()` |
| `providers/google/translator.py` | `UnifiedMessage()` |
| `providers/groq/groq_api.py` | `UnifiedMessage()` |
| `providers/groq/translator.py` | `UnifiedMessage()` |
| `providers/openai/translator.py` | `UnifiedMessage()` |
| `providers/together/together_api.py` | `UnifiedMessage()` |
| `providers/together/translator.py` | `UnifiedMessage()` |
| `providers/xai/translator.py` | `UnifiedMessage()` |
| `providers/xai/xai_api.py` | `UnifiedMessage()` |
| `tests/ai/groq_transcription_test.py` | `UnifiedMessage()` |
| `tests/openai/openai_small_tests.py` | `UnifiedMessage()` |
| `tests/openai/openai_translation_test.py` | `UnifiedMessage()` |
| `orchestrator/executor.py` | `UnifiedResponse()` |
| `orchestrator/recovery_logic.py` | `UnifiedResponse()` |
| `orchestrator/requests.py` | `UnifiedResponse()` |
| `providers/anthropic/anthropic_api.py` | `UnifiedResponse()` |
| `providers/anthropic/translator.py` | `UnifiedResponse()` |
| `providers/cerebras/cerebras_api.py` | `UnifiedResponse()` |
| `providers/cerebras/translator.py` | `UnifiedResponse()` |
| `providers/google/google_api.py` | `UnifiedResponse()` |
| `providers/google/translator.py` | `UnifiedResponse()` |
| `providers/groq/groq_api.py` | `UnifiedResponse()` |
| `providers/groq/translator.py` | `UnifiedResponse()` |
| `providers/openai/openai_api.py` | `UnifiedResponse()` |
| `providers/openai/translator.py` | `UnifiedResponse()` |
| `providers/together/together_api.py` | `UnifiedResponse()` |
| `providers/together/translator.py` | `UnifiedResponse()` |
| `providers/unified_client.py` | `UnifiedResponse()` |
| `providers/xai/translator.py` | `UnifiedResponse()` |
| `providers/xai/xai_api.py` | `UnifiedResponse()` |
| `providers/google/translator.py` | `VideoContent()` |
| `tests/openai/openai_translation_test.py` | `WebSearchCallContent()` |
| `providers/cerebras/translator.py` | `YouTubeVideoContent()` |
| `providers/google/translator.py` | `YouTubeVideoContent()` |
| `providers/groq/translator.py` | `YouTubeVideoContent()` |
| `providers/together/translator.py` | `YouTubeVideoContent()` |
| `providers/xai/translator.py` | `YouTubeVideoContent()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** anthropic, google, matrx_utils, openai
**Internal modules:** db.models, instructions.core, instructions.pattern_parser, media, processing.audio
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "config",
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
