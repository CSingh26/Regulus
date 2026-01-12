from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from regulus_api.db.models import Repo
from regulus_api.db.session import get_session
from regulus_api.jobs.queue import get_queue
from regulus_api.jobs.tasks import build_embeddings
from regulus_api.rag.explain import Citation, explain_with_citations
from regulus_api.rag.retriever import SearchHit, semantic_search

router = APIRouter()


class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str


class SearchRequest(BaseModel):
    repo_id: int
    query: str
    limit: int = 6
    file_path: str | None = None


class SearchHitResponse(BaseModel):
    chunk_id: int
    file_id: int
    file_path: str
    start_line: int
    end_line: int
    score: float


class SearchResponse(BaseModel):
    hits: list[SearchHitResponse]


class ExplainRequest(BaseModel):
    repo_id: int
    question: str
    file_path: str | None = None


class CitationResponse(BaseModel):
    chunk_id: int
    file_id: int
    file_path: str
    start_line: int
    end_line: int
    score: float


class ExplainResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]
    referenced_files: list[int]


@router.post(
    "/repos/{repo_id}/embeddings",
    response_model=JobEnqueueResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def enqueue_embeddings(repo_id: int, session: Session = Depends(get_session)) -> JobEnqueueResponse:
    repo = session.get(Repo, repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    queue = get_queue()
    job = queue.enqueue(build_embeddings, repo_id)
    return JobEnqueueResponse(job_id=job.id, status="queued")


@router.post("/search", response_model=SearchResponse)
def search(payload: SearchRequest, session: Session = Depends(get_session)) -> SearchResponse:
    hits = semantic_search(
        session=session,
        repo_id=payload.repo_id,
        query=payload.query,
        limit=payload.limit,
        file_path=payload.file_path,
    )
    return SearchResponse(hits=[map_search_hit(hit) for hit in hits])


@router.post("/explain", response_model=ExplainResponse)
def explain(payload: ExplainRequest, session: Session = Depends(get_session)) -> ExplainResponse:
    answer, citations = explain_with_citations(
        session=session,
        repo_id=payload.repo_id,
        question=payload.question,
        file_path=payload.file_path,
    )
    referenced_files = sorted({citation.file_id for citation in citations})
    return ExplainResponse(
        answer=answer,
        citations=[map_citation(citation) for citation in citations],
        referenced_files=referenced_files,
    )


def map_search_hit(hit: SearchHit) -> SearchHitResponse:
    return SearchHitResponse(
        chunk_id=hit.chunk_id,
        file_id=hit.file_id,
        file_path=hit.file_path,
        start_line=hit.start_line,
        end_line=hit.end_line,
        score=hit.score,
    )


def map_citation(citation: Citation) -> CitationResponse:
    return CitationResponse(
        chunk_id=citation.chunk_id,
        file_id=citation.file_id,
        file_path=citation.file_path,
        start_line=citation.start_line,
        end_line=citation.end_line,
        score=citation.score,
    )
