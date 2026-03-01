.PHONY: install dev run lint fmt typecheck test

install:
	uv sync --extra server

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

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
