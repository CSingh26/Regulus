from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session

from regulus_api.db.models import Repo
from regulus_api.db.session import get_session
from regulus_api.diff.summarizer import fetch_github_pr_diff, get_local_diff, summarize_diff

router = APIRouter()


class DiffSummaryRequest(BaseModel):
    repo_id: int
    base_ref: str | None = None
    head_ref: str | None = None
    raw_diff: str | None = None
    github_repo: str | None = None
    pr_number: int | None = None


class DiffFileResponse(BaseModel):
    path: str
    additions: int
    deletions: int


class DiffSummaryResponse(BaseModel):
    summary: str
    files: list[DiffFileResponse]
    risk_bullets: list[str]


@router.post("/diff/summary", response_model=DiffSummaryResponse)
def diff_summary(
    payload: DiffSummaryRequest, session: Session = Depends(get_session)
) -> DiffSummaryResponse:
    repo = session.get(Repo, payload.repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")

    diff_text = payload.raw_diff
    if diff_text is None:
        if payload.github_repo and payload.pr_number is not None:
            diff_text = fetch_github_pr_diff(payload.github_repo, payload.pr_number)
        elif payload.base_ref and payload.head_ref:
            diff_text = get_local_diff(Path(repo.path), payload.base_ref, payload.head_ref)
        else:
            raise HTTPException(status_code=400, detail="missing diff parameters")

    summary = summarize_diff(diff_text)
    return DiffSummaryResponse(
        summary=summary.summary,
        files=[
            DiffFileResponse(path=file.path, additions=file.additions, deletions=file.deletions)
            for file in summary.files
        ],
        risk_bullets=summary.risk_bullets,
    )
