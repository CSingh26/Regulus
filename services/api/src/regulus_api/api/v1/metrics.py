from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import desc
from sqlmodel import Session, select

from regulus_api.db.models import MetricSnapshot, Repo
from regulus_api.db.session import engine, get_session
from regulus_api.jobs.queue import get_queue
from regulus_api.jobs.tasks import compute_repo_metrics
from regulus_api.metrics.compute import compute_metrics

router = APIRouter()


class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str


class OwnershipEntry(BaseModel):
    path: str
    primary_owner: str
    owner_share: float
    authors: list[tuple[str, int]]
    churn: int


class HotspotEntry(BaseModel):
    path: str
    score: float
    churn: int
    loc: int
    centrality: float


class OwnershipResponse(BaseModel):
    items: list[OwnershipEntry]


class HotspotResponse(BaseModel):
    items: list[HotspotEntry]


@router.post(
    "/metrics/{repo_id}/compute",
    response_model=JobEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_metrics(repo_id: int, session: Session = Depends(get_session)) -> JobEnqueueResponse:
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    queue = get_queue()
    job = queue.enqueue(compute_repo_metrics, repo_id)
    return JobEnqueueResponse(job_id=job.id, status="queued")


@router.get("/metrics/{repo_id}/hotspots", response_model=HotspotResponse)
def hotspots(repo_id: int, session: Session = Depends(get_session)) -> HotspotResponse:
    snapshot = latest_snapshot(session, repo_id)
    if snapshot is None:
        snapshot = compute_and_load(repo_id)
    hotspots_data = snapshot.data.get("hotspots", [])
    return HotspotResponse(items=[HotspotEntry(**item) for item in hotspots_data])


@router.get("/metrics/{repo_id}/ownership", response_model=OwnershipResponse)
def ownership(
    repo_id: int,
    path: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> OwnershipResponse:
    snapshot = latest_snapshot(session, repo_id)
    if snapshot is None:
        snapshot = compute_and_load(repo_id)
    ownership_data = snapshot.data.get("ownership", [])
    if path:
        ownership_data = [item for item in ownership_data if item.get("path") == path]
    return OwnershipResponse(items=[OwnershipEntry(**item) for item in ownership_data])


def latest_snapshot(session: Session, repo_id: int) -> MetricSnapshot | None:
    statement = (
        select(MetricSnapshot)
        .where(MetricSnapshot.repo_id == repo_id)
        .where(MetricSnapshot.kind == "analytics")
        .order_by(desc(cast(Any, MetricSnapshot.created_at)))
    )
    return session.exec(statement).first()


def compute_and_load(repo_id: int) -> MetricSnapshot:
    compute_metrics(repo_id)
    with Session(engine) as session:
        snapshot = latest_snapshot(session, repo_id)
        if snapshot is None:
            raise HTTPException(status_code=500, detail="metrics snapshot missing")
        return snapshot
