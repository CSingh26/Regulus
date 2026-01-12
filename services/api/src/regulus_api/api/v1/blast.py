from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from regulus_api.blast.engine import predict_blast_radius

router = APIRouter()


class BlastRequest(BaseModel):
    repo_id: int
    changed_files: list[str]


class BlastImpact(BaseModel):
    path: str
    confidence: float
    reasons: list[str]
    signals: dict[str, object]


class BlastResponse(BaseModel):
    impacts: list[BlastImpact]
    tests: list[str]


@router.post("/blast", response_model=BlastResponse)
def blast(payload: BlastRequest) -> BlastResponse:
    result = predict_blast_radius(payload.repo_id, payload.changed_files)
    return BlastResponse(
        impacts=[BlastImpact(**impact) for impact in result["impacts"]],
        tests=result["tests"],
    )
