from __future__ import annotations

import subprocess
from pathlib import Path


def collect_cochanges(repo_path: Path, target_files: set[str]) -> dict[str, int]:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "--name-only", "--pretty=format:@@@"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")

    cochange_counts: dict[str, int] = {}
    current_files: list[str] = []

    def flush_commit() -> None:
        if not current_files:
            return
        if not target_files.intersection(current_files):
            return
        for path in current_files:
            if path in target_files:
                continue
            cochange_counts[path] = cochange_counts.get(path, 0) + 1

    for line in result.stdout.splitlines():
        if line.startswith("@@@"):
            flush_commit()
            current_files = []
            continue
        if line.strip():
            current_files.append(line.strip())

    flush_commit()
    return cochange_counts
