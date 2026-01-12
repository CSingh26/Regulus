#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v pnpm >/dev/null 2>&1 && [ -d "$ROOT_DIR/node_modules" ]; then
  pnpm -C "$ROOT_DIR" exec prettier --write .
else
  echo "prettier not installed; skipping JS/JSON formatting check"
fi

if command -v ruff >/dev/null 2>&1; then
  if rg --files -g '*.py' "$ROOT_DIR/services" >/dev/null 2>&1; then
    python3 -m ruff format "$ROOT_DIR/services"
  else
    echo "no python files found; skipping ruff format"
  fi
else
  echo "ruff not installed; skipping python format"
fi
