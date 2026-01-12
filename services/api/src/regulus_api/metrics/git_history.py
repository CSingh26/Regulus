from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileChurn:
    additions: int = 0
    deletions: int = 0
    authors: dict[str, int] = field(default_factory=dict)

    @property
    def churn(self) -> int:
        return self.additions + self.deletions


def collect_file_churn(repo_path: Path) -> dict[str, FileChurn]:
    result = subprocess.run(
        ["git", "-C", str(repo_path), "log", "--numstat", "--format=@@@%an"],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git log failed")

    churn_map: dict[str, FileChurn] = {}
    current_author = "unknown"
    for line in result.stdout.splitlines():
        if line.startswith("@@@"):
            current_author = line.replace("@@@", "", 1).strip() or "unknown"
            continue
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        additions, deletions, path = parts[0], parts[1], parts[2]
        if additions == "-" or deletions == "-":
            continue
        churn = churn_map.setdefault(path, FileChurn())
        churn.additions += int(additions)
        churn.deletions += int(deletions)
        churn.authors[current_author] = churn.authors.get(current_author, 0) + 1
    return churn_map
