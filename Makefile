.PHONY: install dev run lint fmt typecheck test

install:
	uv sync

dev:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --loop uvloop

run:
	uv run python -m app.main

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
