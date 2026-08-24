"""Domain discovery endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from optibench.api.deps import get_engine
from optibench.matching.engine import MatchingEngine

router = APIRouter(prefix="/api/v1", tags=["domains"])


@router.get("/domains")
def list_domains(engine: MatchingEngine = Depends(get_engine)):
    """列出所有已注册领域."""
    return {
        "items": [
            {"id": d.domain_id, "name": d.domain_name}
            for d in engine.domains.values()
        ]
    }


@router.get("/domains/{domain}/parameters")
def get_domain_parameters(domain: str, engine: MatchingEngine = Depends(get_engine)):
    """获取指定领域的参数定义 — 用于前端动态渲染表单."""
    try:
        module = engine.get_domain(domain)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Unknown domain: {domain}")

    params = module.get_parameters()
    return {
        "domain_id": module.domain_id,
        "domain_name": module.domain_name,
        "parameters": [
            {
                "name": p.name,
                "label": p.label,
                "type": p.type,
                "unit": p.unit,
                "default": p.default,
                "required": p.required,
                "options": [{"value": v, "label": label} for v, label in (p.options or [])],
                "min_value": p.min_value,
                "max_value": p.max_value,
                "description": p.description,
            }
            for p in params
        ],
    }
