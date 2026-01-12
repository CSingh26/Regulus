from __future__ import annotations

from pathlib import Path

TEST_SUFFIXES = ("_test.py", "test_", ".test.ts", ".spec.ts", ".test.tsx", ".spec.tsx")


def suggest_tests(changed_files: list[str], all_files: set[str]) -> list[str]:
    suggestions: set[str] = set()
    all_paths = {Path(path) for path in all_files}

    for changed in changed_files:
        changed_path = Path(changed)
        base = changed_path.stem
        if not base:
            continue

        candidate_paths = [
            Path("tests") / f"test_{base}.py",
            Path("tests") / f"{base}_test.py",
            Path("tests") / f"test_{base}.ts",
            Path("tests") / f"test_{base}.tsx",
        ]
        for candidate in candidate_paths:
            if candidate.as_posix() in all_files:
                suggestions.add(candidate.as_posix())

        for suffix in (".test.ts", ".spec.ts", ".test.tsx", ".spec.tsx"):
            candidate_str = changed_path.with_suffix("").as_posix() + suffix
            if candidate_str in all_files:
                suggestions.add(candidate_str)

        for sibling in all_paths:
            if sibling.parent != changed_path.parent:
                continue
            if base in sibling.name and sibling.name.endswith(TEST_SUFFIXES):
                suggestions.add(sibling.as_posix())

    return sorted(suggestions)
