from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, delete, select

from regulus_api.db.models import File, GraphEdge, GraphNode, JobStatus, Repo, utc_now
from regulus_api.db.session import engine
from regulus_api.graph.parsers import extract_imports
from regulus_api.graph.resolver import build_module_map, resolve_import


def build_dependency_graph(repo_id: int) -> dict[str, int]:
    edges_created = 0
    try:
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is None:
                raise ValueError(f"repo {repo_id} not found")

            repo.graph_status = JobStatus.running
            repo.last_error = None
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

            session.exec(delete(GraphEdge).where(GraphEdge.repo_id == repo_id))  # type: ignore[call-overload,arg-type]
            session.exec(delete(GraphNode).where(GraphNode.repo_id == repo_id))  # type: ignore[call-overload,arg-type]
            session.commit()

            files = list(session.exec(select(File).where(File.repo_id == repo_id)).all())
            repo_root = Path(repo.path).resolve()
            module_map = build_module_map(files, repo_root)

            node_map: dict[int, GraphNode] = {}
            for file in files:
                if file.id is None:
                    continue
                file_path = Path(file.path)
                try:
                    relative = file_path.resolve().relative_to(repo_root).as_posix()
                except ValueError:
                    relative = file_path.name
                node = GraphNode(
                    repo_id=repo_id,
                    file_id=file.id,
                    name=relative,
                    path=str(file_path),
                    kind="module",
                    loc=file.loc,
                )
                session.add(node)
                session.flush()
                node_map[file.id] = node
            session.commit()

            for file in files:
                if file.id is None:
                    continue
                source_node = node_map.get(file.id)
                if source_node is None:
                    continue
                if source_node.id is None:
                    continue
                file_path = Path(file.path)
                if not file_path.exists():
                    continue
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                imports = extract_imports(file.language, text)
                for spec in imports:
                    target_file = resolve_import(spec, file_path, repo_root, module_map)
                    if target_file is None:
                        continue
                    if target_file.id is None:
                        continue
                    target_node = node_map.get(target_file.id)
                    if target_node is None:
                        continue
                    if target_node.id is None:
                        continue
                    session.add(
                        GraphEdge(
                            repo_id=repo_id,
                            from_node_id=source_node.id,
                            to_node_id=target_node.id,
                            kind="import",
                            weight=1,
                        )
                    )
                    edges_created += 1
                    if edges_created % 200 == 0:
                        session.commit()

            repo.graph_status = JobStatus.completed
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

        return {"nodes": len(node_map), "edges": edges_created}
    except Exception as exc:  # pragma: no cover - status update
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is not None:
                repo.graph_status = JobStatus.failed
                repo.last_error = str(exc)[:2000]
                repo.updated_at = utc_now()
                session.add(repo)
                session.commit()
        raise
