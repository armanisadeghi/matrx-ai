.PHONY: install dev run lint fmt typecheck test \
        sync sync-dry sync-push sync-verify \
        sync-core sync-core-dry \
        sync-all sync-template sync-template-dry \
        clean

install:
	uv sync

dev:
	PYTHONUNBUFFERED=1 PYTHONUTF8=1 uv run uvicorn matrx_ai.app.main:app \
		--host 0.0.0.0 --port 8000 \
		--reload \
		--loop uvloop \
		--no-access-log \
		--log-level warning

run:
	PYTHONUNBUFFERED=1 PYTHONUTF8=1 uv run matrx-ai-server

lint:
	uv run ruff check matrx_ai tests

fmt:
	uv run ruff format matrx_ai tests

typecheck:
	uv run pyright

test:
	uv run pytest -v

## ── AI engine sync (aidream ↔ matrx-ai) ─────────────────────────────────────

# Pull AI engine updates from aidream → matrx-ai (default sync)
sync:
	python3 scripts/sync_from_aidream.py --modernize-types

# Dry-run preview of the above
sync-dry:
	python3 scripts/sync_from_aidream.py --dry-run

# Push AI engine changes from matrx-ai → aidream
sync-push:
	python3 scripts/sync_from_aidream.py --direction matrx-to-aidream

# Verify all aidream imports translate cleanly — run before/after adding new imports
sync-verify:
	python3 scripts/sync_from_aidream.py --verify

## ── API core sync (matrx-ai → aidream) ──────────────────────────────────────

# Push context/, app/core/, auth middleware/deps to aidream
sync-core:
	python3 scripts/sync_from_aidream.py --core-only

# Dry-run preview of the above
sync-core-dry:
	python3 scripts/sync_from_aidream.py --core-only --dry-run

# Push everything: AI engine + API core from matrx-ai → aidream
sync-all:
	python3 scripts/sync_from_aidream.py --direction matrx-to-aidream --sync-core

## ── Template sync (matrx-ai → matrx-service-core) ───────────────────────────

# Push context/ and app/core/ to the matrx-service-core template
sync-template:
	python3 scripts/sync_template.py

# Dry-run preview of the above
sync-template-dry:
	python3 scripts/sync_template.py --dry-run

## ── Housekeeping ─────────────────────────────────────────────────────────────

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
