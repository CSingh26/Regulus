from __future__ import annotations

from pathlib import Path

from sqlmodel import Session, delete, select

from regulus_api.db.models import Chunk, Embedding, File, Finding, JobStatus, Repo, Scan, utc_now
from regulus_api.db.session import engine
from regulus_api.graph.builder import build_dependency_graph
from regulus_api.indexing.indexer import index_repository
from regulus_api.metrics.compute import compute_metrics
from regulus_api.rag.provider import get_embedding_provider
from regulus_api.security.runner import run_npm_audit, run_pip_audit, run_semgrep


def index_repo(repo_id: int) -> dict[str, int]:
    total_chunks = 0
    try:
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is None:
                raise ValueError(f"repo {repo_id} not found")

            repo.index_status = JobStatus.running
            repo.last_error = None
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

            session.exec(delete(Chunk).where(Chunk.repo_id == repo_id))  # type: ignore[call-overload,arg-type]
            session.exec(delete(File).where(File.repo_id == repo_id))  # type: ignore[call-overload,arg-type]
            session.commit()

            file_records = index_repository(Path(repo.path))
            for idx, record in enumerate(file_records, start=1):
                file_row = File(
                    repo_id=repo_id,
                    path=record.path,
                    language=record.language,
                    size_bytes=record.size_bytes,
                    loc=record.loc,
                    sha=record.sha,
                    updated_at=utc_now(),
                )
                session.add(file_row)
                session.flush()
                for chunk in record.chunks:
                    session.add(
                        Chunk(
                            repo_id=repo_id,
                            file_id=file_row.id,
                            content=chunk.content,
                            start_line=chunk.start_line,
                            end_line=chunk.end_line,
                            token_count=chunk.token_count,
                        )
                    )
                total_chunks += len(record.chunks)
                if idx % 50 == 0:
                    session.commit()

            repo.index_status = JobStatus.completed
            repo.last_indexed_at = utc_now()
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

        return {"files": len(file_records), "chunks": total_chunks}
    except Exception as exc:  # pragma: no cover - best-effort status update
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is not None:
                repo.index_status = JobStatus.failed
                repo.last_error = str(exc)[:2000]
                repo.updated_at = utc_now()
                session.add(repo)
                session.commit()
        raise


def build_graph(repo_id: int) -> dict[str, int]:
    return build_dependency_graph(repo_id)


def build_embeddings(repo_id: int) -> dict[str, int]:
    provider = get_embedding_provider()
    try:
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is None:
                raise ValueError(f"repo {repo_id} not found")

            repo.embedding_status = JobStatus.running
            repo.last_error = None
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

            session.exec(delete(Embedding).where(Embedding.repo_id == repo_id))  # type: ignore[call-overload,arg-type]
            session.commit()

            chunks = list(session.exec(select(Chunk).where(Chunk.repo_id == repo_id)).all())
            total_embeddings = 0
            batch_size = 64
            for offset in range(0, len(chunks), batch_size):
                batch = chunks[offset : offset + batch_size]
                texts = [chunk.content for chunk in batch]
                vectors = provider.embed(texts)
                for chunk, vector in zip(batch, vectors, strict=False):
                    if chunk.id is None:
                        continue
                    session.add(
                        Embedding(
                            repo_id=repo_id,
                            chunk_id=chunk.id,
                            provider=provider.name,
                            model=provider.model,
                            dim=provider.dim,
                            embedding=vector,
                            created_at=utc_now(),
                        )
                    )
                    total_embeddings += 1
                session.commit()

            repo.embedding_status = JobStatus.completed
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

        return {"embeddings": total_embeddings}
    except Exception as exc:  # pragma: no cover - status update
        with Session(engine) as session:
            repo = session.get(Repo, repo_id)
            if repo is not None:
                repo.embedding_status = JobStatus.failed
                repo.last_error = str(exc)[:2000]
                repo.updated_at = utc_now()
                session.add(repo)
                session.commit()
        raise


def compute_repo_metrics(repo_id: int) -> dict:
    return compute_metrics(repo_id)


def run_security_scans(repo_id: int) -> dict[str, int]:
    repo_path: str | None = None
    with Session(engine) as session:
        repo = session.get(Repo, repo_id)
        if repo is None:
            raise ValueError(f"repo {repo_id} not found")
        repo_path = repo.path
        repo.security_status = JobStatus.running
        repo.last_error = None
        repo.updated_at = utc_now()
        session.add(repo)
        session.commit()

    if repo_path is None:
        raise ValueError("repo path missing")

    tool_runners = [run_semgrep, run_pip_audit, run_npm_audit]
    total_findings = 0
    failures = 0

    for runner in tool_runners:
        with Session(engine) as session:
            scan_record = Scan(
                repo_id=repo_id,
                tool=runner.__name__.replace("run_", ""),
                status=JobStatus.running,
            )
            session.add(scan_record)
            session.commit()
            session.refresh(scan_record)
            scan_id = scan_record.id

        try:
            result = runner(Path(repo_path))
            with Session(engine) as session:
                scan_lookup = session.get(Scan, scan_id) if scan_id is not None else None
                if scan_lookup is not None:
                    scan_lookup.status = JobStatus.completed
                    scan_lookup.finished_at = utc_now()
                    scan_lookup.summary = result.summary
                    session.add(scan_lookup)
                for finding in result.findings:
                    session.add(
                        Finding(
                            scan_id=scan_id,
                            repo_id=repo_id,
                            tool=finding.tool,
                            severity=finding.severity,
                            file_path=finding.file_path,
                            line=finding.line,
                            message=finding.message,
                            rule_id=finding.rule_id,
                            details=finding.metadata,
                            created_at=utc_now(),
                        )
                    )
                session.commit()
            total_findings += len(result.findings)
        except Exception as exc:  # pragma: no cover - external tool failures
            failures += 1
            with Session(engine) as session:
                scan_lookup = session.get(Scan, scan_id) if scan_id is not None else None
                if scan_lookup is not None:
                    scan_lookup.status = JobStatus.failed
                    scan_lookup.finished_at = utc_now()
                    scan_lookup.summary = {"error": str(exc)[:2000]}
                    session.add(scan_lookup)
                    session.commit()

    with Session(engine) as session:
        repo = session.get(Repo, repo_id)
        if repo is not None:
            repo.security_status = JobStatus.failed if failures else JobStatus.completed
            repo.updated_at = utc_now()
            session.add(repo)
            session.commit()

    return {"findings": total_findings, "failures": failures}
