# `processing.audio` — Module Overview

> This document is partially auto-generated. Sections tagged `<!-- AUTO:id -->` are refreshed by the generator.
> Everything else is yours to edit freely and will never be overwritten.

<!-- AUTO:meta -->
## About This Document

This file is **partially auto-generated**. Sections wrapped in `<!-- AUTO:id -->` tags
are overwritten each time the generator runs. Everything else is yours to edit freely.

| Field | Value |
|-------|-------|
| Module | `processing/audio` |
| Last generated | 2026-03-01 00:10 |
| Output file | `processing/audio/MODULE_README.md` |
| Signature mode | `signatures` |

**To refresh auto-sections:**
```bash
python utils/code_context/generate_module_readme.py processing/audio --mode signatures
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
processing/audio/
├── MODULE_README.md
├── __init__.py
├── audio_preprocessing.py
├── audio_support.py
├── groq_transcription.py
├── transcription_cache.py
# excluded: 1 .md
```
<!-- /AUTO:tree -->

<!-- AUTO:signatures -->
## API Signatures

> Auto-generated via `output_mode="signatures"`. ~5-10% token cost vs full source.
> For full source, open the individual files directly.

```
---
Filepath: processing/audio/__init__.py  [python]



---
Filepath: processing/audio/transcription_cache.py  [python]

  class CachedTranscription:
  class TranscriptionCache:
      def __init__(self)
      def _generate_key(self, audio_source: str, model: str, language: str | None) -> str
      def get(self, audio_source: str, model: str, language: str | None) -> CachedTranscription | None
      def set(self, audio_source: str, model: str, language: str | None, text: str, metadata: dict[str, Any]) -> None
      def clear(self) -> None
      def size(self) -> int
  def get_cache() -> TranscriptionCache
  def clear_cache() -> None


---
Filepath: processing/audio/audio_preprocessing.py  [python]

  def preprocess_audio_in_messages(messages: MessageList, api_class: str, debug: bool = False) -> tuple[MessageList, list[TokenUsage]]
  def should_preprocess_audio(messages: MessageList, api_class: str) -> bool


---
Filepath: processing/audio/audio_support.py  [python]

  def api_supports_audio(api: str) -> bool
  def api_class_supports_audio(api_class: str) -> bool
  def should_transcribe_audio(audio_auto_transcribe: bool, api_class: str, explicit_flag: bool = True) -> bool


---
Filepath: processing/audio/groq_transcription.py  [python]

  class TranscriptionUsage:
      def __post_init__(self)
      def to_dict(self) -> dict[str, Any]
  class TranscriptionResult:
      def to_dict(self) -> dict[str, Any]
  class GroqTranscription:
      def __init__(self, api_key: str | None = None, default_model: str = 'whisper-large-v3-turbo', debug: bool = False)
      def transcribe(self, audio_source: str | bytes | io.BytesIO, model: str | None = None, language: str | None = None, prompt: str | None = None, response_format: Literal['json', 'verbose_json', 'text'] = 'verbose_json', temperature: float = 0.0, timestamp_granularities: list | None = None) -> TranscriptionResult
      def translate(self, audio_source: str | bytes | io.BytesIO, model: str | None = None, prompt: str | None = None, response_format: Literal['json', 'text'] = 'json', temperature: float = 0.0) -> TranscriptionResult
      def _prepare_audio_file(self, audio_source: str | bytes | io.BytesIO) -> tuple
      def _parse_response(self, response: Any, model: str, operation: Literal['transcription', 'translation'], file_size_mb: float, response_format: str) -> TranscriptionResult
      def _calculate_quality_metrics(self, segments: list) -> dict[str, Any]
```
<!-- /AUTO:signatures -->

<!-- AUTO:callers -->
## Upstream Callers

> Auto-discovered by scanning all project files that import from this module.
> Set `ENTRY_POINTS` in `generate_readme.py` to pin specific functions.

| Caller | Calls |
|--------|-------|
| `processing/__init__.py` | `CachedTranscription()` |
| `config/media_config.py` | `GroqTranscription()` |
| `processing/__init__.py` | `GroqTranscription()` |
| `processing/__init__.py` | `TranscriptionCache()` |
| `processing/__init__.py` | `TranscriptionResult()` |
| `processing/__init__.py` | `TranscriptionUsage()` |
| `processing/__init__.py` | `api_class_supports_audio()` |
| `providers/unified_client.py` | `api_class_supports_audio()` |
| `processing/__init__.py` | `api_supports_audio()` |
| `processing/__init__.py` | `clear_cache()` |
| `config/media_config.py` | `get_cache()` |
| `processing/__init__.py` | `get_cache()` |
| `processing/__init__.py` | `preprocess_audio_in_messages()` |
| `providers/unified_client.py` | `preprocess_audio_in_messages()` |
| `processing/__init__.py` | `should_preprocess_audio()` |
| `providers/unified_client.py` | `should_preprocess_audio()` |
<!-- /AUTO:callers -->

<!-- AUTO:dependencies -->
## Dependencies

**External packages:** groq, matrx_utils
**Internal modules:** config, media
<!-- /AUTO:dependencies -->

<!-- AUTO:config -->
## Generation Config

> Auto-managed. Contains the exact parameters used to generate this README.
> Used by parent modules to auto-refresh this file when it is stale.
> Do not edit manually — changes will be overwritten on the next run.

```json
{
  "subdirectory": "processing/audio",
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
