#!/bin/bash

set -e

echo "Starting application..."

cd code

exec uv run uvicorn api.web.app:app --host 0.0.0.0 --port 8000 --log-level info
