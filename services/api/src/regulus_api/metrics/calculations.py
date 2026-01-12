from __future__ import annotations

from pathlib import Path

from regulus_api.db.models import File, GraphEdge, GraphNode
from regulus_api.metrics.git_history import FileChurn


def compute_centrality(nodes: list[GraphNode], edges: list[GraphEdge]) -> dict[int, float]:
    degrees: dict[int, int] = {}
    for node in nodes:
        if node.id is None:
            continue
        degrees[node.id] = 0

    for edge in edges:
        if edge.from_node_id is not None:
            degrees[edge.from_node_id] = degrees.get(edge.from_node_id, 0) + 1
        if edge.to_node_id is not None:
            degrees[edge.to_node_id] = degrees.get(edge.to_node_id, 0) + 1

    max_degree = max(degrees.values(), default=1)
    centrality_by_file: dict[int, float] = {}
    for node in nodes:
        if node.id is None or node.file_id is None:
            continue
        centrality_by_file[node.file_id] = degrees.get(node.id, 0) / max_degree
    return centrality_by_file


def build_ownership(
    files: list[File],
    churn_map: dict[str, FileChurn],
    repo_root: Path,
) -> list[dict]:
    ownership: list[dict] = []
    for file in files:
        if file.id is None:
            continue
        try:
            relative = Path(file.path).resolve().relative_to(repo_root).as_posix()
        except ValueError:
            relative = Path(file.path).name
        churn = churn_map.get(relative)
        if churn is None:
            ownership.append(
                {
                    "path": relative,
                    "primary_owner": "unknown",
                    "owner_share": 0.0,
                    "authors": [],
                    "churn": 0,
                }
            )
            continue
        total_commits = sum(churn.authors.values())
        primary_owner = max(churn.authors, key=lambda author: churn.authors[author])
        owner_share = churn.authors[primary_owner] / max(total_commits, 1)
        ownership.append(
            {
                "path": relative,
                "primary_owner": primary_owner,
                "owner_share": round(owner_share, 3),
                "authors": sorted(churn.authors.items(), key=lambda item: item[1], reverse=True)[
                    :5
                ],
                "churn": churn.churn,
            }
        )
    return ownership


def build_hotspots(
    files: list[File],
    churn_map: dict[str, FileChurn],
    centrality_by_file: dict[int, float],
    repo_root: Path,
) -> list[dict]:
    hotspots: list[dict] = []
    for file in files:
        if file.id is None:
            continue
        try:
            relative = Path(file.path).resolve().relative_to(repo_root).as_posix()
        except ValueError:
            relative = Path(file.path).name
        churn = churn_map.get(relative)
        churn_value = churn.churn if churn else 0
        centrality = centrality_by_file.get(file.id, 0.0)
        score = churn_value * max(file.loc, 1) * (1 + centrality)
        hotspots.append(
            {
                "path": relative,
                "score": round(score, 3),
                "churn": churn_value,
                "loc": file.loc,
                "centrality": round(centrality, 3),
            }
        )
    hotspots.sort(key=lambda item: item["score"], reverse=True)
    return hotspots
