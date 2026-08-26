"""Matching and calculation endpoints."""

from __future__ import annotations

import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from optibench.api.deps import get_engine
from optibench.domains.base import Requirements
from optibench.matching.engine import MatchingEngine

router = APIRouter(prefix="/api/v1", tags=["matching"])

logger = logging.getLogger(__name__)


class CalculateReq(BaseModel):
    working_distance: float | None = None
    sensor_w: float | None = None
    fov_w: float | None = None
    focal_length: float | None = None
    sensor_h: float | None = None
    fov_h: float | None = None


@router.post("/calculate")
def calculate(params: CalculateReq):
    """基础光学计算（薄透镜公式）."""
    from optibench.core.thin_lens import ThinLensCalculator
    from optibench.core.types import OpticalParams

    try:
        calc = ThinLensCalculator()
        op = OpticalParams(**params.model_dump(exclude_none=True))
        result = calc.solve(op)
        return {
            k: v
            for k, v in result.__dict__.items()
            if v is not None
        }
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Calculation error: {str(e)}")


class MatchReq(BaseModel):
    domain: str = Field(default="industrial", max_length=32)
    requirements: dict


@router.post("/match/async")
def start_matching(req: MatchReq, engine: MatchingEngine = Depends(get_engine)):
    """启动异步匹配任务."""
    requirements = Requirements(
        domain=req.domain,
        params=req.requirements,
    )
    task = engine.match_async(requirements)
    return {
        "task_id": task.task_id,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
    }


@router.post("/match/stream")
def start_matching_stream(req: MatchReq, engine: MatchingEngine = Depends(get_engine)):
    """启动渐进式 SSE 流式匹配 — 实时推送各阶段结果."""
    requirements = Requirements(
        domain=req.domain,
        params=req.requirements,
    )

    def event_generator():
        try:
            for chunk in engine.match_progressive(requirements):
                data = json.dumps(chunk, default=str)
                yield f"data: {data}\n\n"
        except Exception as e:
            error_data = json.dumps({"stage": "error", "error": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/match/async/{task_id}")
def get_matching_status(task_id: str, engine: MatchingEngine = Depends(get_engine)):
    """查询匹配任务状态."""
    task = engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "stage": task.stage,
        "total_candidates": task.total_candidates,
        "filtered_candidates": task.filtered_candidates,
        "error": task.error,
    }


@router.get("/match/async/{task_id}/result")
def get_matching_result(task_id: str, engine: MatchingEngine = Depends(get_engine)):
    """获取已完成任务的匹配结果."""
    task = engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"Task status: {task.status}")

    top_matches = (task.result or [])[:20]
    explanations = {}
    for r in top_matches:
        try:
            explanations[f"{r.lens_id}-{r.detector_id}"] = engine.explain_result(r)
        except Exception:
            logger.warning(
                "explain_result failed for %s-%s",
                r.lens_id,
                r.detector_id,
                exc_info=True,
            )

    return {
        "top_matches": [r.to_dict() for r in top_matches],
        "diagnostics": [d.to_dict() for d in (task.diagnostics or [])],
        "explanations": explanations,
    }


@router.delete("/match/async/{task_id}")
def cancel_matching(task_id: str, engine: MatchingEngine = Depends(get_engine)):
    """取消正在执行的任务."""
    cancelled = engine.cancel_task(task_id)
    return {"cancelled": cancelled}
