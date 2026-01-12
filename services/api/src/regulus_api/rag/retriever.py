from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from sqlmodel import Session, select

from regulus_api.db.models import Chunk, Embedding, File
from regulus_api.rag.provider import get_embedding_provider


@dataclass
class SearchHit:
    chunk_id: int
    file_id: int
    file_path: str
    content: str
    start_line: int
    end_line: int
    score: float


def semantic_search(
    session: Session,
    repo_id: int,
    query: str,
    limit: int = 6,
    file_path: str | None = None,
) -> list[SearchHit]:
    provider = get_embedding_provider()
    query_vector = provider.embed([query])[0]

    distance = cast(Any, Embedding.embedding).cosine_distance(query_vector)
    statement = (
        select(Chunk, File, distance.label("distance"))
        .join(File, File.id == Chunk.file_id)  # type: ignore[arg-type]
        .join(Embedding, Embedding.chunk_id == Chunk.id)  # type: ignore[arg-type]
        .where(Embedding.repo_id == repo_id)
    )
    if file_path:
        statement = statement.where(File.path == file_path)
    statement = statement.order_by(distance).limit(limit)

    results = session.exec(statement).all()
    hits: list[SearchHit] = []
    for chunk, file, dist in results:
        if chunk.id is None or file.id is None:
            continue
        score = max(0.0, 1.0 - float(dist))
        hits.append(
            SearchHit(
                chunk_id=chunk.id,
                file_id=file.id,
                file_path=file.path,
                content=chunk.content,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                score=score,
            )
        )
    return hits
