from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from typing import Any, cast

from sqlmodel import Session, select

from regulus_api.blast.history import collect_cochanges
from regulus_api.blast.tests import suggest_tests
from regulus_api.db.models import File, GraphEdge, GraphNode, Repo
from regulus_api.db.session import engine
from regulus_api.metrics.calculations import compute_centrality


def predict_blast_radius(repo_id: int, changed_files: list[str]) -> dict:
    with Session(engine) as session:
        repo = session.get(Repo, repo_id)
        if repo is None:
            raise ValueError(f"repo {repo_id} not found")
        files = list(session.exec(select(File).where(File.repo_id == repo_id)).all())
        nodes = list(session.exec(select(GraphNode).where(GraphNode.repo_id == repo_id)).all())
        edges = list(session.exec(select(GraphEdge).where(GraphEdge.repo_id == repo_id)).all())

    repo_root = Path(repo.path).resolve()
    return compute_blast_radius(repo_root, changed_files, files, nodes, edges)


def compute_blast_radius(
    repo_root: Path,
    changed_files: list[str],
    files: list[File],
    nodes: list[GraphNode],
    edges: list[GraphEdge],
) -> dict:
    file_by_rel: dict[str, File] = {}
    rel_by_file_id: dict[int, str] = {}
    for file in files:
        if file.id is None:
            continue
        try:
            relative = Path(file.path).resolve().relative_to(repo_root).as_posix()
        except ValueError:
            relative = Path(file.path).name
        file_by_rel[relative] = file
        rel_by_file_id[file.id] = relative

    changed_rel = normalize_paths(changed_files, repo_root)
    changed_file_ids: set[int] = set()
    for path in changed_rel:
        file_record = file_by_rel.get(path)
        if file_record is None or file_record.id is None:
            continue
        changed_file_ids.add(file_record.id)

    node_by_file: dict[int, int] = {}
    for node in nodes:
        if node.file_id is None or node.id is None:
            continue
        node_by_file[node.file_id] = node.id

    reverse_edges: dict[int, set[int]] = defaultdict(set)
    for edge in edges:
        if edge.from_node_id is None or edge.to_node_id is None:
            continue
        reverse_edges[edge.to_node_id].add(edge.from_node_id)

    impacted_node_ids: set[int] = set()
    queue: deque[int] = deque()
    for file_id in changed_file_ids:
        node_id = node_by_file.get(file_id)
        if node_id is not None:
            queue.append(node_id)
            impacted_node_ids.add(node_id)

    while queue:
        node_id = queue.popleft()
        for dependent in reverse_edges.get(node_id, set()):
            if dependent not in impacted_node_ids:
                impacted_node_ids.add(dependent)
                queue.append(dependent)

    impacted_paths = {
        rel_by_file_id[file_id]
        for file_id, node_id in node_by_file.items()
        if node_id in impacted_node_ids and file_id in rel_by_file_id
    }

    cochange_counts = collect_cochanges(repo_root, set(changed_rel))
    max_cochange = max(cochange_counts.values(), default=1)
    centrality_by_file = compute_centrality(nodes, edges)

    candidate_paths = impacted_paths.union(cochange_counts.keys())
    impacts = []
    for path in sorted(candidate_paths):
        if path in changed_rel:
            continue
        file_record = file_by_rel.get(path)
        if file_record is None or file_record.id is None:
            continue
        reasons = []
        reachability = path in impacted_paths
        if reachability:
            reasons.append("Dependency reachability from changed modules")

        cochange_count = cochange_counts.get(path, 0)
        if cochange_count:
            reasons.append(f"Co-changed {cochange_count}x with touched files")

        centrality = centrality_by_file.get(file_record.id, 0.0)
        if centrality >= 0.25:
            reasons.append(f"High centrality ({centrality:.2f})")

        confidence = 0.0
        if reachability:
            confidence += 0.5
        if cochange_count:
            confidence += 0.3 * (cochange_count / max_cochange)
        if centrality:
            confidence += 0.2 * centrality
        confidence = min(1.0, round(confidence, 3))

        impacts.append(
            {
                "path": path,
                "confidence": confidence,
                "reasons": reasons or ["Low-signal impact"],
                "signals": {
                    "reachability": reachability,
                    "cochange": cochange_count,
                    "centrality": round(centrality, 3),
                },
            }
        )

    impacts.sort(key=lambda item: float(cast(Any, item["confidence"])), reverse=True)
    test_suggestions = suggest_tests(changed_rel, set(file_by_rel.keys()))

    return {
        "impacts": impacts,
        "tests": test_suggestions,
    }


def normalize_paths(paths: list[str], repo_root: Path) -> list[str]:
    normalized = []
    for path in paths:
        candidate = Path(path)
        if candidate.is_absolute():
            try:
                candidate = candidate.resolve().relative_to(repo_root)
            except ValueError:
                continue
        normalized.append(candidate.as_posix())
    return normalized
