from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

MAX_FILE_SIZE_BYTES = 1_000_000
MAX_CHUNK_LINES = 200

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".vscode",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "venv",
}

LANGUAGE_BY_EXT = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".json": "json",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".md": "markdown",
    ".toml": "toml",
}


@dataclass
class ChunkRecord:
    content: str
    start_line: int
    end_line: int
    token_count: int


@dataclass
class FileRecord:
    path: str
    language: str
    size_bytes: int
    loc: int
    sha: str
    chunks: list[ChunkRecord]


def iter_repo_files(repo_path: Path) -> list[Path]:
    file_paths: list[Path] = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file_name in files:
            file_paths.append(Path(root) / file_name)
    return file_paths


def infer_language(path: Path) -> str:
    return LANGUAGE_BY_EXT.get(path.suffix.lower(), "unknown")


def chunk_text(text: str) -> list[ChunkRecord]:
    lines = text.splitlines()
    chunks: list[ChunkRecord] = []
    start = 0
    while start < len(lines):
        end = min(start + MAX_CHUNK_LINES, len(lines))
        chunk_lines = lines[start:end]
        content = "\n".join(chunk_lines)
        token_count = len(content.split())
        chunks.append(
            ChunkRecord(
                content=content,
                start_line=start + 1,
                end_line=end,
                token_count=token_count,
            )
        )
        start = end
    return chunks


def index_repository(repo_path: Path) -> list[FileRecord]:
    records: list[FileRecord] = []
    for path in iter_repo_files(repo_path):
        if not path.is_file():
            continue
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            continue
        language = infer_language(path)
        if language == "unknown":
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not text.strip():
            continue
        sha = hashlib.sha1(text.encode("utf-8")).hexdigest()
        loc = len(text.splitlines())
        chunks = chunk_text(text)
        records.append(
            FileRecord(
                path=str(path),
                language=language,
                size_bytes=path.stat().st_size,
                loc=loc,
                sha=sha,
                chunks=chunks,
            )
        )
    return records
