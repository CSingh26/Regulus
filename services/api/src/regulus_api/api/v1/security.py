from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlmodel import Session, select

from regulus_api.db.models import Finding, Repo
from regulus_api.db.session import get_session
from regulus_api.jobs.queue import get_queue
from regulus_api.jobs.tasks import run_security_scans

router = APIRouter()


class JobEnqueueResponse(BaseModel):
    job_id: str
    status: str


class ScanRequest(BaseModel):
    repo_id: int


class FindingResponse(BaseModel):
    id: int
    tool: str
    severity: str
    file_path: str | None
    line: int | None
    message: str
    rule_id: str | None


class FindingsResponse(BaseModel):
    items: list[FindingResponse]


@router.post(
    "/security/scan", response_model=JobEnqueueResponse, status_code=status.HTTP_202_ACCEPTED
)
def enqueue_security_scan(
    payload: ScanRequest, session: Session = Depends(get_session)
) -> JobEnqueueResponse:
    repo = session.get(Repo, payload.repo_id)
    if not repo:
        raise HTTPException(status_code=404, detail="repo not found")
    queue = get_queue()
    job = queue.enqueue(run_security_scans, payload.repo_id)
    return JobEnqueueResponse(job_id=job.id, status="queued")


@router.get("/security/findings", response_model=FindingsResponse)
def list_findings(
    repo_id: int = Query(...),
    severity: str | None = Query(default=None),
    session: Session = Depends(get_session),
) -> FindingsResponse:
    statement = select(Finding).where(Finding.repo_id == repo_id)
    if severity:
        statement = statement.where(Finding.severity == severity)
    findings = session.exec(statement).all()
    items = [
        FindingResponse(
            id=finding.id,
            tool=finding.tool,
            severity=finding.severity,
            file_path=finding.file_path,
            line=finding.line,
            message=finding.message,
            rule_id=finding.rule_id,
        )
        for finding in findings
        if finding.id is not None
    ]
    return FindingsResponse(items=items)
