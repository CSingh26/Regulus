#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: ./scripts/release.sh <version> [title]
Example: ./scripts/release.sh 1.0.0 "Regulus v1.0.0 - Live Demo + Local Mode (Zero Cloud Cost)"
USAGE
}

if [ $# -lt 1 ]; then
  usage
  exit 1
fi

version="$1"
shift
custom_title="${1:-}"

root_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root_dir"

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI not found. Install it first:"
  echo "  macOS: brew install gh"
  echo "  Ubuntu: sudo apt-get update && sudo apt-get install -y gh"
  exit 1
fi

tag="v${version}"
notes_dir="release-notes"
template_path="${notes_dir}/TEMPLATE.md"
notes_path="${notes_dir}/${tag}.md"

if [ ! -f "$template_path" ]; then
  echo "Missing release notes template at ${template_path}"
  exit 1
fi

if [ -f "$notes_path" ]; then
  echo "Release notes already exist at ${notes_path}"
  exit 1
fi

project_name="${PROJECT_NAME:-}"
if [ -z "$project_name" ] && [ -f package.json ]; then
  project_name=$(python3 - <<'PY'
import json
from pathlib import Path
path = Path("package.json")
if not path.exists():
    raise SystemExit(1)
print(json.loads(path.read_text()).get("name", ""))
PY
  ) || true
fi

if [ -z "$project_name" ]; then
  project_name="Regulus"
fi

date_value="${DATE:-$(date +%Y-%m-%d)}"
demo_url="${DEMO_URL:-https://demo.example.com}"
local_api_url="${LOCAL_API_URL:-http://localhost:8000}"
local_ui_url="${LOCAL_UI_URL:-http://localhost:3000}"

release_title="$custom_title"
if [ -z "$release_title" ]; then
  release_title="${project_name} ${tag} - Live Demo + Local Mode (Zero Cloud Cost)"
fi

mkdir -p "$notes_dir"

TEMPLATE_PATH="$template_path" NOTES_PATH="$notes_path" \
PROJECT_NAME="$project_name" VERSION="$version" TAG="$tag" DATE="$date_value" \
DEMO_URL="$demo_url" LOCAL_API_URL="$local_api_url" LOCAL_UI_URL="$local_ui_url" \
python3 - <<'PY'
import os
from pathlib import Path

content = Path(os.environ["TEMPLATE_PATH"]).read_text()
replacements = {
    "{{PROJECT_NAME}}": os.environ["PROJECT_NAME"],
    "{{VERSION}}": os.environ["VERSION"],
    "{{TAG}}": os.environ["TAG"],
    "{{DATE}}": os.environ["DATE"],
    "{{DEMO_URL}}": os.environ["DEMO_URL"],
    "{{LOCAL_API_URL}}": os.environ["LOCAL_API_URL"],
    "{{LOCAL_UI_URL}}": os.environ["LOCAL_UI_URL"],
}
for key, value in replacements.items():
    content = content.replace(key, value)

Path(os.environ["NOTES_PATH"]).write_text(content)
PY

if [ -f apps/web/package.json ]; then
  VERSION="$version" python3 - <<'PY'
import json
from pathlib import Path
import os

path = Path("apps/web/package.json")
if not path.exists():
    raise SystemExit(0)

payload = json.loads(path.read_text())
payload["version"] = os.environ["VERSION"]
path.write_text(json.dumps(payload, indent=2) + "\n")
PY
fi

if [ -f services/api/pyproject.toml ]; then
  VERSION="$version" python3 - <<'PY'
import os
import re
from pathlib import Path

path = Path("services/api/pyproject.toml")
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
new_text, count = re.subn(r'(?m)^version = "[^"]+"$', f'version = "{os.environ["VERSION"]}"', text, count=1)
if count == 0:
    raise SystemExit("Could not find version in services/api/pyproject.toml")
path.write_text(new_text)
PY
fi

git add "$notes_path"
if [ -f apps/web/package.json ]; then
  git add apps/web/package.json
fi
if [ -f services/api/pyproject.toml ]; then
  git add services/api/pyproject.toml
fi

git commit -m "chore(release): ${tag}"

git tag "${tag}"

git push

git push origin "${tag}"

gh release create "${tag}" -t "${release_title}" -F "${notes_path}"
