#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="$PWD/services/api"
.venv/bin/alembic -c services/api/alembic.ini upgrade head
.venv/bin/python scripts/seed.py
.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM
npm run dev --prefix apps/web
