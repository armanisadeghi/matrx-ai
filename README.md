# matrx-ai

Matrx AI Engine — core FastAPI backend for AI orchestration.

## Setup

```bash
uv sync          # installs all dependencies + the project itself (editable)
cp .env.example .env  # then fill in your keys
make dev         # start dev server on :8000
```

`uv sync` is all that's needed. It installs the project as an editable package, which puts the project root on `sys.path` automatically — so all imports (`client`, `config`, `db`, `conversation`, etc.) resolve from any working directory, including VS Code's Run button and pytest.

## Environment variables

Copy `.env.example` to `.env` and fill in the required keys (AI provider keys, Supabase credentials). The `.env` file is never committed.

**If you have a `PYTHONPATH` set globally** (e.g. from another project in your shell config or another workspace's `.env`), it can shadow this project's packages. The `.vscode/settings.json` in this repo points VS Code at `.env` directly, which ensures the correct path is used when running files from the editor.

## Running tests

```bash
make test           # all tests via pytest
# or run a single file via VS Code's play button — works after uv sync
```

## Common commands

```bash
make dev        # dev server with reload
make run        # production mode
make lint       # ruff check
make fmt        # ruff format
make typecheck  # pyright
make test       # pytest -v
```
