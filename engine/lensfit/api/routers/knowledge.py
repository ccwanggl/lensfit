"""Knowledge base endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from lensfit.knowledge.constraints import ALL_CONSTRAINTS
from lensfit.knowledge.engine import KnowledgeInferenceEngine, OpticalKnowledgeBase
from lensfit.knowledge.formulas import list_formulas as kb_list_formulas
from lensfit.knowledge.presets import get_preset_by_id, list_presets

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge"])

_knowledge_engine = KnowledgeInferenceEngine(OpticalKnowledgeBase())


@router.get("/formulas")
def list_knowledge_formulas(domain: str | None = None):
    """列出光学公式库."""
    formulas = kb_list_formulas(domain)
    return {"items": [f.to_dict() for f in formulas]}


@router.get("/constraints")
def list_knowledge_constraints():
    """列出物理约束库."""
    return {"items": [c.to_dict() for c in ALL_CONSTRAINTS]}


class InferReq(BaseModel):
    params: dict
    domain: str = Field(default="all", max_length=32)


@router.post("/infer")
def knowledge_infer(req: InferReq):
    """基于已知参数，使用知识库推理未知参数."""
    try:
        result = _knowledge_engine.infer(req.params, req.domain)
        return {
            "derived_params": result.derived_params,
            "trace_chain": result.trace_chain,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")


@router.get("/presets")
def list_knowledge_presets(domain: str | None = None):
    """列出专业预设配置方案."""
    presets = list_presets(domain)
    return {"items": [p.to_dict() for p in presets]}


@router.get("/presets/{preset_id}")
def get_knowledge_preset(preset_id: str):
    """获取单个预设配置详情."""
    preset = get_preset_by_id(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset not found: {preset_id}")
    return preset.to_dict()
