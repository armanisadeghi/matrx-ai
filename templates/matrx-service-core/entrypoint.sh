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

# TODO: Update the module path to match your service package name
echo "Starting Matrx Service..."
exec uvicorn matrx_service.app.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --loop uvloop \
    --no-access-log
