#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v ruff >/dev/null 2>&1; then
  if rg --files -g '*.py' "$ROOT_DIR/services" >/dev/null 2>&1; then
    python3 -m ruff check "$ROOT_DIR/services"
  else
    echo "no python files found; skipping ruff lint"
  fi
else
  echo "ruff not installed; skipping python lint"
fi

if command -v mypy >/dev/null 2>&1; then
  if rg --files -g '*.py' "$ROOT_DIR/services" >/dev/null 2>&1; then
    mypy "$ROOT_DIR/services"
  else
    echo "no python files found; skipping mypy"
  fi
else
  echo "mypy not installed; skipping type check"
fi

if [ -f "$ROOT_DIR/apps/web/package.json" ]; then
  if node -e "const pkg=require('./apps/web/package.json'); process.exit(pkg.scripts && pkg.scripts.lint ? 0 : 1)"; then
    pnpm -C "$ROOT_DIR/apps/web" run -s lint
  else
    echo "apps/web lint script not configured; skipping"
  fi
else
  echo "apps/web not initialized; skipping web lint"
fi
