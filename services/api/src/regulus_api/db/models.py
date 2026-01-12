from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
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


class File(SQLModel, table=True):
    __tablename__ = "files"

    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repos.id", index=True)
    path: str = Field(index=True)
    language: str
    size_bytes: int
    loc: int
    sha: str
    updated_at: datetime = Field(default_factory=utc_now)


class Chunk(SQLModel, table=True):
    __tablename__ = "chunks"

    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repos.id", index=True)
    file_id: int = Field(foreign_key="files.id", index=True)
    content: str
    start_line: int
    end_line: int
    token_count: int
    created_at: datetime = Field(default_factory=utc_now)


class GraphNode(SQLModel, table=True):
    __tablename__ = "graph_nodes"

    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repos.id", index=True)
    file_id: int = Field(foreign_key="files.id", index=True)
    name: str
    path: str
    kind: str
    loc: int


class GraphEdge(SQLModel, table=True):
    __tablename__ = "graph_edges"

    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repos.id", index=True)
    from_node_id: int = Field(foreign_key="graph_nodes.id", index=True)
    to_node_id: int = Field(foreign_key="graph_nodes.id", index=True)
    kind: str
    weight: int = 1


class Embedding(SQLModel, table=True):
    __tablename__ = "embeddings"

    id: int | None = Field(default=None, primary_key=True)
    repo_id: int = Field(foreign_key="repos.id", index=True)
    chunk_id: int = Field(foreign_key="chunks.id", index=True)
    provider: str
    model: str
    dim: int
    embedding: list[float] = Field(sa_column=Column(Vector(1536)))
    created_at: datetime = Field(default_factory=utc_now)
