from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, select

from regulus_api.db.models import (
    File,
    GraphEdge,
    GraphNode,
    JobStatus,
    MetricSnapshot,
    Repo,
    utc_now,
)
from regulus_api.db.session import engine
from regulus_api.metrics.calculations import build_hotspots, build_ownership, compute_centrality
from regulus_api.metrics.git_history import collect_file_churn


def compute_metrics(repo_id: int) -> dict:
    try:
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is None:
                raise ValueError(f"repo {repo_id} not found")

            repo_path = repo.path
            repo.metrics_status = JobStatus.running
            repo.last_error = None
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

            files = list(session.exec(select(File).where(File.repo_id == repo_id)).all())
            nodes = list(session.exec(select(GraphNode).where(GraphNode.repo_id == repo_id)).all())
            edges = list(session.exec(select(GraphEdge).where(GraphEdge.repo_id == repo_id)).all())

        repo_root = Path(repo_path).resolve()
        churn_map = collect_file_churn(repo_root)
        centrality_by_file = compute_centrality(nodes, edges)
        ownership = build_ownership(files, churn_map, repo_root)
        hotspots = build_hotspots(files, churn_map, centrality_by_file, repo_root)

        centrality_by_path = {}
        for file in files:
            if file.id is None:
                continue
            try:
                relative = Path(file.path).resolve().relative_to(repo_root).as_posix()
            except ValueError:
                relative = Path(file.path).name
            centrality_by_path[relative] = round(centrality_by_file.get(file.id, 0.0), 3)

        snapshot_data = {
            "ownership": ownership,
            "hotspots": hotspots,
            "centrality": centrality_by_path,
        }

        with Session(engine) as session:
            session.add(
                MetricSnapshot(
                    repo_id=repo_id,
                    kind="analytics",
                    data=snapshot_data,
                    created_at=utc_now(),
                )
            )
            repo = session.get(Repo, repo_id)
            if repo is not None:
                repo.metrics_status = JobStatus.completed
                repo.updated_at = utc_now()
                session.add(repo)
            session.commit()

        return snapshot_data
    except Exception as exc:  # pragma: no cover - status update
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is not None:
                repo.metrics_status = JobStatus.failed
                repo.last_error = str(exc)[:2000]
                repo.updated_at = utc_now()
                session.add(repo)
                session.commit()
        raise
