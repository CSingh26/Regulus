from pathlib import Path

from pytest import MonkeyPatch

from regulus_api.blast import engine as blast_engine
from regulus_api.db.models import File, GraphEdge, GraphNode


def test_blast_radius_reachability_and_tests(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    repo_root = tmp_path
    file_a = File(
        id=1,
        repo_id=1,
        path=str(repo_root / "src/a.ts"),
        language="typescript",
        size_bytes=10,
        loc=10,
        sha="a",
    )
    file_b = File(
        id=2,
        repo_id=1,
        path=str(repo_root / "src/b.ts"),
        language="typescript",
        size_bytes=10,
        loc=10,
        sha="b",
    )
    file_test = File(
        id=3,
        repo_id=1,
        path=str(repo_root / "tests/test_b.ts"),
        language="typescript",
        size_bytes=10,
        loc=5,
        sha="t",
    )

    node_a = GraphNode(
        id=10,
        repo_id=1,
        file_id=1,
        name="src/a.ts",
        path=file_a.path,
        kind="module",
        loc=10,
    )
    node_b = GraphNode(
        id=11,
        repo_id=1,
        file_id=2,
        name="src/b.ts",
        path=file_b.path,
        kind="module",
        loc=10,
    )
    edge = GraphEdge(
        id=100,
        repo_id=1,
        from_node_id=10,
        to_node_id=11,
        kind="import",
        weight=1,
    )

    monkeypatch.setattr(blast_engine, "collect_cochanges", lambda *_: {})

    result = blast_engine.compute_blast_radius(
        repo_root,
        ["src/b.ts"],
        [file_a, file_b, file_test],
        [node_a, node_b],
        [edge],
    )

    impacted_paths = {impact["path"] for impact in result["impacts"]}
    assert "src/a.ts" in impacted_paths
    assert "tests/test_b.ts" in result["tests"]
