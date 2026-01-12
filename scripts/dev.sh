#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export PYTHONPATH="$ROOT_DIR/services/api/src"

echo "Starting Regulus dev stack..."

python3 -m uvicorn regulus_api.main:app --reload --host 0.0.0.0 --port 8000 &
API_PID=$!

python3 "$ROOT_DIR/services/worker/worker.py" &
WORKER_PID=$!

pnpm -C "$ROOT_DIR/apps/web" dev &
WEB_PID=$!

trap 'kill $API_PID $WORKER_PID $WEB_PID' EXIT

wait $API_PID $WORKER_PID $WEB_PID
