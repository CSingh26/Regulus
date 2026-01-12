#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if command -v pytest >/dev/null 2>&1; then
  if [ -d "$ROOT_DIR/services/api/tests" ] && rg --files -g 'test_*.py' "$ROOT_DIR/services/api/tests" >/dev/null 2>&1; then
    pytest
  else
    echo "no python tests found; skipping pytest"
  fi
else
  echo "pytest not installed; skipping python tests"
fi

if [ -f "$ROOT_DIR/apps/web/package.json" ]; then
  if node -e "const pkg=require('./apps/web/package.json'); process.exit(pkg.scripts && pkg.scripts.test ? 0 : 1)"; then
    pnpm -C "$ROOT_DIR/apps/web" run -s test
  else
    echo "apps/web test script not configured; skipping"
  fi
else
  echo "apps/web not initialized; skipping web tests"
fi
