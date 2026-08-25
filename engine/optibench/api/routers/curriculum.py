"""Curriculum API endpoints — serves the learning-path graph."""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from optibench.api.deps import get_db_session
from optibench.curriculum import get_curriculum_graph
from optibench.db.models import LearningRecord

router = APIRouter(prefix="/api/v1/curriculum", tags=["curriculum"])

DEFAULT_LEARNER = "default"
DEFAULT_STATUS = "not_started"
# completed/scored 都视为已完成（scored 是测验类完成的形态）。
_COMPLETED_STATUSES = ("completed", "scored")


class CurriculumNodeItem(BaseModel):
    id: str
    kind: Literal["concept", "experiment", "preset", "practice", "assessment"]
    ref: str
    title: str
    module: str
    prerequisites: list[str]
    status: str


class CurriculumEdgeItem(BaseModel):
    from_id: str
    to_id: str


class CurriculumGraphResponse(BaseModel):
    nodes: list[CurriculumNodeItem]
    edges: list[CurriculumEdgeItem]


@router.get("/graph", response_model=CurriculumGraphResponse)
def get_graph(session: Session = Depends(get_db_session)):
    """Return the curriculum graph (nodes + edges) with learner status merged.

    Node ``status`` merges ``learning_records`` for the default learner:
    ``completed`` when a completed/scored record exists for the node id,
    ``viewed`` when only a viewed record exists, otherwise ``not_started``.
    """
    graph = get_curriculum_graph()
    records = session.execute(
        select(LearningRecord).where(LearningRecord.learner_id == DEFAULT_LEARNER)
    ).scalars().all()
    status_by_item: dict[str, str] = {}
    for record in records:
        # completed/scored 优先于 viewed（同一 item 多条 kind 记录合并时取高态）。
        if record.status in _COMPLETED_STATUSES or status_by_item.get(record.item_id) is None:
            status_by_item[record.item_id] = (
                "completed" if record.status in _COMPLETED_STATUSES else "viewed"
            )
    return {
        "nodes": [
            {
                "id": node.id,
                "kind": node.kind,
                "ref": node.ref,
                "title": node.title,
                "module": node.module,
                "prerequisites": node.prerequisites,
                "status": status_by_item.get(node.id, DEFAULT_STATUS),
            }
            for node in graph.nodes.values()
        ],
        "edges": [{"from_id": e.from_id, "to_id": e.to_id} for e in graph.edges],
    }
