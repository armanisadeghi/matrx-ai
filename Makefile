.PHONY: install dev run lint fmt typecheck test

install:
	uv sync

dev:
	PYTHONUNBUFFERED=1 PYTHONUTF8=1 uv run uvicorn app.main:app \
		--host 0.0.0.0 --port 8000 \
		--reload \
		--loop uvloop \
		--no-access-log \
		--log-level warning

run:
	PYTHONUNBUFFERED=1 PYTHONUTF8=1 uv run python -m app.main

lint:
	uv run ruff check app tests

fmt:
	uv run ruff format app tests

typecheck:
	uv run pyright

test:
	uv run pytest -v

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
