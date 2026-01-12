from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import requests  # type: ignore[import-untyped]

from regulus_api.core.config import get_settings


@dataclass
class FileDiffStats:
    path: str
    additions: int
    deletions: int


@dataclass
class DiffSummary:
    summary: str
    files: list[FileDiffStats]
    risk_bullets: list[str]


def get_local_diff(repo_path: Path, base_ref: str, head_ref: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "diff", f"{base_ref}..{head_ref}"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff failed")
    return result.stdout


def fetch_github_pr_diff(repo: str, pr_number: int) -> str:
    settings = get_settings()
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN not configured")

    response = requests.get(
        f"https://api.github.com/repos/{repo}/pulls/{pr_number}",
        headers={
            "Authorization": f"Bearer {settings.github_token}",
            "Accept": "application/vnd.github.v3.diff",
        },
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"GitHub API error: {response.status_code} {response.text}")
    return str(response.text)


def summarize_diff(diff_text: str) -> DiffSummary:
    files: dict[str, FileDiffStats] = {}
    current_file: str | None = None

    for line in diff_text.splitlines():
        if line.startswith("diff --git "):
            parts = line.split(" ")
            if len(parts) >= 4:
                current_file = parts[3].replace("b/", "", 1)
                files.setdefault(current_file, FileDiffStats(current_file, 0, 0))
            continue
        if line.startswith("+++ b/"):
            current_file = line.replace("+++ b/", "", 1)
            files.setdefault(current_file, FileDiffStats(current_file, 0, 0))
            continue
        if current_file is None:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            files[current_file].additions += 1
        elif line.startswith("-") and not line.startswith("---"):
            files[current_file].deletions += 1

    total_add = sum(stat.additions for stat in files.values())
    total_del = sum(stat.deletions for stat in files.values())
    summary = f"Changed {len(files)} files (+{total_add}/-{total_del})."

    risk_bullets = []
    risky_paths = ("migrations", "infra", "security", "auth", "payments", "db", "api")
    if any(path for path in files if path.startswith(risky_paths)):
        risk_bullets.append("Touches sensitive areas (db/api/infra). Review carefully.")
    if total_add + total_del > 500:
        risk_bullets.append("Large diff size; consider splitting for reviewability.")
    if not risk_bullets:
        risk_bullets.append("No obvious risk heuristics triggered.")

    return DiffSummary(summary=summary, files=list(files.values()), risk_bullets=risk_bullets)
