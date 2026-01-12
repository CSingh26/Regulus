from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from regulus_api.db.models import File

KNOWN_EXTENSIONS = {
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".toml",
}

INDEX_FILENAMES = {
    "index.ts",
    "index.tsx",
    "index.js",
    "index.jsx",
    "index.py",
    "__init__.py",
}


def module_keys_for_path(path: Path, repo_root: Path) -> list[str]:
    relative = path.resolve().relative_to(repo_root)
    no_ext = relative.with_suffix("")
    keys = [no_ext.as_posix()]
    if path.name in INDEX_FILENAMES:
        keys.append(relative.parent.as_posix())
    return list(dict.fromkeys(keys))


def build_module_map(files: Sequence[File], repo_root: Path) -> dict[str, File]:
    module_map: dict[str, File] = {}
    for file in files:
        path = Path(file.path)
        try:
            keys = module_keys_for_path(path, repo_root)
        except ValueError:
            continue
        for key in keys:
            module_map.setdefault(key, file)
    return module_map


def normalize_spec(spec: str) -> str:
    spec = spec.strip().replace("\\", "/")
    if spec.startswith("@/"):
        spec = spec[2:]
    if spec.startswith("./"):
        spec = spec[2:]
    for ext in KNOWN_EXTENSIONS:
        if spec.endswith(ext):
            spec = spec[: -len(ext)]
            break
    return spec.strip("/")


def resolve_import(
    spec: str,
    source_path: Path,
    repo_root: Path,
    module_map: dict[str, File],
) -> File | None:
    if not spec:
        return None

    if spec.startswith("."):
        candidate = (source_path.parent / spec).resolve()
        try:
            relative = candidate.relative_to(repo_root)
        except ValueError:
            return None
        key = normalize_spec(relative.as_posix())
        return module_map.get(key) or module_map.get(f"{key}/index")

    key = normalize_spec(spec)
    return module_map.get(key) or module_map.get(f"{key}/index")
