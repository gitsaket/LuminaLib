#!/bin/sh
set -e

# Run DB migrations before starting the API
echo "[entrypoint] Running Alembic migrations..."
alembic upgrade head

echo "[entrypoint] Starting application..."
exec "$@"
