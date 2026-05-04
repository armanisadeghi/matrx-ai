#!/bin/bash
set +e

source /app/.venv/bin/activate

if [ -f /app/.env ]; then
    echo "Loading environment variables from /app/.env"
    set -o allexport
    source /app/.env
    set +o allexport
else
    echo "/app/.env not found, proceeding with existing environment variables."
fi

echo "Starting Matrx AI..."
exec uvicorn matrx_ai.app.main:app --host "${HOST:-0.0.0.0}" --port "${PORT:-8000}" --loop uvloop --no-access-log
