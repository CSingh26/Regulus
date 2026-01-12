from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlmodel import Session, select

from regulus_api.core.config import get_settings
from regulus_api.db.models import JobStatus, Repo
from regulus_api.db.session import get_session
from regulus_api.jobs.queue import get_queue
from regulus_api.jobs.tasks import index_repo

router = APIRouter()
settings = get_settings()


def is_allowed_path(repo_path: Path) -> bool:
    resolved_path = repo_path.resolve()
    for root in settings.regulus_allowed_roots:
        try:
            if resolved_path.is_relative_to(root.resolve()):
                return True
        except FileNotFoundError:
            continue
    return False


class RepoRegisterRequest(BaseModel):
    name: str
    path: str


class RepoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    path: str
    created_at: datetime
    updated_at: datetime
    last_indexed_at: datetime | None
    index_status: JobStatus
    graph_status: JobStatus
    embedding_status: JobStatus
    security_status: JobStatus
    metrics_status: JobStatus
    last_error: str | None


class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str


@router.post("/register", response_model=RepoResponse, status_code=status.HTTP_201_CREATED)
def register_repo(payload: RepoRegisterRequest, session: Session = Depends(get_session)) -> Repo:
    repo_path = Path(payload.path)
    if not repo_path.exists():
        raise HTTPException(status_code=400, detail="path does not exist")
    if not is_allowed_path(repo_path):
        raise HTTPException(status_code=403, detail="path is not within allowed roots")

    existing = session.exec(select(Repo).where(Repo.path == str(repo_path))).first()
    if existing:
        return existing

    repo = Repo(name=payload.name, path=str(repo_path))
    session.add(repo)
    session.commit()
    session.refresh(repo)
    return repo


@router.get("/{repo_id}/status", response_model=RepoResponse)
def repo_status(repo_id: int, session: Session = Depends(get_session)) -> Repo:
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    return repo


@router.post(
    "/{repo_id}/index", response_model=JobEnqueueResponse, status_code=status.HTTP_202_ACCEPTED
)
def enqueue_index(repo_id: int, session: Session = Depends(get_session)) -> JobEnqueueResponse:
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    queue = get_queue()
    job = queue.enqueue(index_repo, repo_id)
    return JobEnqueueResponse(job_id=job.id, status="queued")
