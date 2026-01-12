from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class Repo(SQLModel, table=True):
    __tablename__ = "repos"

    id: int | None = Field(default=None, primary_key=True)
    name: str
    path: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    last_indexed_at: datetime | None = None
    index_status: JobStatus = Field(default=JobStatus.pending)
    graph_status: JobStatus = Field(default=JobStatus.pending)
    embedding_status: JobStatus = Field(default=JobStatus.pending)
    security_status: JobStatus = Field(default=JobStatus.pending)
    metrics_status: JobStatus = Field(default=JobStatus.pending)
    last_error: str | None = None
