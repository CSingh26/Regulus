#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
REPO_PATH="${REPO_PATH:-$(pwd)}"
REPO_NAME="${REPO_NAME:-$(basename "${REPO_PATH}")}"
echo "Registering ${REPO_NAME} at ${REPO_PATH}..."
response=$(curl -s -X POST "${API_URL}/v1/repos/register" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"${REPO_NAME}\",\"path\":\"${REPO_PATH}\"}")

repo_id=$(python3 - <<'PY'
import json,sys
payload=json.loads(sys.stdin.read())
print(payload["id"])
PY
<<< "$response")

echo "Repo ID: ${repo_id}"

echo "Queueing indexing..."
curl -s -X POST "${API_URL}/v1/repos/${repo_id}/index" | cat

echo "Queueing graph build..."
curl -s -X POST "${API_URL}/v1/repos/${repo_id}/graph" | cat

echo "Queueing embeddings..."
curl -s -X POST "${API_URL}/v1/repos/${repo_id}/embeddings" | cat

echo "Queueing metrics..."
curl -s -X POST "${API_URL}/v1/metrics/${repo_id}/compute" | cat

echo "Done. Open the dashboard at http://localhost:3000/repo/${repo_id}/map"
