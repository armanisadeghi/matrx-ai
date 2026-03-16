# matrx-ai

Matrx AI Engine — unified AI orchestration backend with multi-provider LLM support, streaming, tool execution, and conversation persistence.

## Installation

```bash
# Core library only (AI providers, tools, conversation management)
pip install matrx-ai

# With the FastAPI server layer
pip install "matrx-ai[server]"

# Or with uv
uv add matrx-ai
uv add "matrx-ai[server]"
```

## Quick Start (library)

```python
import matrx_ai

# Initialize once at startup (registers the database connection)
matrx_ai.initialize()

# Use the AI engine directly
from matrx_ai.orchestrator import execute_ai_request
from matrx_ai.config.unified_config import UnifiedConfig
```

## Quick Start (server)

```bash
uv sync --extra server   # install with server deps
cp .env.example .env     # fill in your API keys
make dev                 # start dev server on :8000
```

## Environment Variables

Copy `.env.example` to `.env` and fill in the required keys:

- AI provider keys: `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY`, etc.
- Supabase: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_MATRIX_*`

## Common Commands

```bash
make dev        # dev server with reload on :8000
make run        # production mode (matrx-ai-server)
make lint       # ruff check
make fmt        # ruff format
make typecheck  # pyright
make test       # pytest -v
```

## Publishing a New Release

```bash
./scripts/publish.sh              # patch bump  (e.g. 1.2.3 → 1.2.4)
./scripts/publish.sh --minor      # minor bump  (e.g. 1.2.3 → 1.3.0)
./scripts/publish.sh --major      # major bump  (e.g. 1.2.3 → 2.0.0)
./scripts/publish.sh --message "feat: add new provider"
./scripts/publish.sh --dry-run    # preview without committing
```

## Version History

| Version | Highlights |
|---|---|
| **v0.1.22** | Patch release |
| **v0.1.21** | Patch release |
| **v0.1.20** | Patch release |
| **v0.1.19** | Patch release |
| **v0.1.18** | Patch release |
| **v0.1.17** | Patch release |
| **v0.1.16** | Patch release |
| **v0.1.15** | Patch release |
| **v0.1.14** | Patch release |
| **v0.1.13** | Patch release |
| **v0.1.12** | Patch release |
| **v0.1.11** | Patch release |
| **v0.1.10** | Patch release |
| **v0.1.9** | Patch release |
| **v0.1.8** | Patch release |
| **v0.1.7** | Patch release |
| **v0.1.6** | Patch release |
| **v0.1.5** | Patch release |
| **v0.1.4** | Patch release |
| **v0.1.3** | Patch release |
| **v0.1.2** | Patch release |
| **v0.1.1** | Patch release |
| **v0.1.0** | Initial release — multi-provider AI orchestration, streaming, tool system, conversation persistence |
