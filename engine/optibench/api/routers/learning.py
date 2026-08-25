"""Learning progress endpoints — local single-user learner state (phase 2).

Spec: ``docs/development/specifications/lab/learning-records.md``.
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from optibench.api.deps import get_db_session
from optibench.db.models import LearningRecord

router = APIRouter(prefix="/api/v1/learning", tags=["learning"])

DEFAULT_LEARNER = "default"

ProgressStatus = Literal["viewed", "completed", "scored"]


class ProgressItem(BaseModel):
    learner_id: str
    item_kind: str
    item_id: str
    status: str
    score: float | None
    updated_at: datetime | None


class ProgressListResponse(BaseModel):
    items: list[ProgressItem]


class ProgressReportRequest(BaseModel):
    item_kind: str = Field(..., min_length=1, max_length=32)
    item_id: str = Field(..., min_length=1, max_length=255)
    status: ProgressStatus
    score: float | None = None
    learner_id: str = Field(default=DEFAULT_LEARNER, min_length=1, max_length=64)


def _to_item(record: LearningRecord) -> ProgressItem:
    return ProgressItem(
        learner_id=record.learner_id,
        item_kind=record.item_kind,
        item_id=record.item_id,
        status=record.status,
        score=record.score,
        updated_at=record.updated_at,
    )


@router.get("/progress", response_model=ProgressListResponse)
def get_progress(
    learner_id: str = DEFAULT_LEARNER,
    item_kind: str | None = None,
    session: Session = Depends(get_db_session),
):
    """Query learning progress for a learner, optionally filtered by item kind."""
    stmt = select(LearningRecord).where(LearningRecord.learner_id == learner_id)
    if item_kind is not None:
        stmt = stmt.where(LearningRecord.item_kind == item_kind)
    records = session.execute(stmt).scalars().all()
    return {"items": [_to_item(r) for r in records]}


@router.put("/progress", response_model=ProgressItem)
def put_progress(req: ProgressReportRequest, session: Session = Depends(get_db_session)):
    """Report a single progress record (upsert by learner + kind + item)."""
    if req.status != "scored" and req.score is not None:
        raise HTTPException(status_code=422, detail="score 仅当 status=scored 时有意义")
    record = session.execute(
        select(LearningRecord).where(
            LearningRecord.learner_id == req.learner_id,
            LearningRecord.item_kind == req.item_kind,
            LearningRecord.item_id == req.item_id,
        )
    ).scalar_one_or_none()
    if record is None:
        record = LearningRecord(
            learner_id=req.learner_id,
            item_kind=req.item_kind,
            item_id=req.item_id,
            status=req.status,
            score=req.score,
        )
        session.add(record)
    else:
        record.status = req.status
        record.score = req.score
        record.updated_at = datetime.now()
    session.commit()
    session.refresh(record)
    return _to_item(record)
