"""Project and setup management endpoints."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from lensfit.api.deps import get_db_session
from lensfit.db.models import DetectorCatalog, LensCatalog, Project, ProjectSetup

router = APIRouter(prefix="/api/v1", tags=["projects"])


class CreateProjectReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1000)
    domain: str = Field(default="industrial", max_length=32)


class CreateSetupReq(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    lens_id: int | None = None
    detector_id: int | None = None
    notes: str | None = Field(default=None, max_length=2000)
    match_result_snapshot: dict | None = None


class ProjectReportReq(BaseModel):
    format: str = Field(default="pdf", pattern=r"^(pdf|excel)$")


def _safe_json_loads(raw: str | None) -> Any | None:
    """Safely load a JSON string, returning None on failure."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _model_to_dict(obj: Any) -> dict:
    """Convert SQLAlchemy model to plain dict (excluding relationships)."""
    result: dict = {}
    for c in obj.__table__.columns:
        val = getattr(obj, c.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[c.name] = val
    return result


@router.get("/projects")
def list_projects(session: Session = Depends(get_db_session)):
    """列出项目."""
    projects = session.query(Project).order_by(Project.created_at.desc()).all()
    return {
        "items": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "domain": p.domain,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in projects
        ],
    }


@router.post("/projects")
def create_project(req: CreateProjectReq, session: Session = Depends(get_db_session)):
    """创建项目."""
    project = Project(
        name=req.name,
        description=req.description,
        domain=req.domain,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "domain": project.domain,
        "created_at": project.created_at.isoformat() if project.created_at else None,
    }


@router.get("/projects/{project_id}/setups")
def list_setups(project_id: int, session: Session = Depends(get_db_session)):
    """列出方案."""
    setups = (
        session.query(ProjectSetup)
        .filter(ProjectSetup.project_id == project_id)
        .order_by(ProjectSetup.created_at.desc())
        .all()
    )
    return {
        "items": [
            {
                "id": s.id,
                "project_id": s.project_id,
                "name": s.name,
                "lens_id": s.lens_id,
                "detector_id": s.detector_id,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "lens_snapshot": _safe_json_loads(s.lens_snapshot),
                "detector_snapshot": _safe_json_loads(s.detector_snapshot),
                "match_result_snapshot": _safe_json_loads(s.match_result_snapshot),
                "notes": s.notes,
            }
            for s in setups
        ],
    }


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, session: Session = Depends(get_db_session)):
    """删除项目及其下所有方案."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    session.query(ProjectSetup).filter(ProjectSetup.project_id == project_id).delete()
    session.delete(project)
    session.commit()
    return {"deleted": True}


@router.post("/projects/{project_id}/setups")
def save_setup(project_id: int, req: CreateSetupReq, session: Session = Depends(get_db_session)):
    """保存方案."""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    lens = session.get(LensCatalog, req.lens_id) if req.lens_id else None
    detector = session.get(DetectorCatalog, req.detector_id) if req.detector_id else None

    setup = ProjectSetup(
        project_id=project_id,
        name=req.name,
        lens_id=req.lens_id,
        detector_id=req.detector_id,
        lens_snapshot=json.dumps(_model_to_dict(lens)) if lens else None,
        detector_snapshot=json.dumps(_model_to_dict(detector)) if detector else None,
        match_result_snapshot=(
            json.dumps(req.match_result_snapshot, default=str)
            if req.match_result_snapshot else None
        ),
        notes=req.notes,
    )
    session.add(setup)
    session.commit()
    session.refresh(setup)
    return {
        "id": setup.id,
        "project_id": setup.project_id,
        "name": setup.name,
        "lens_id": setup.lens_id,
        "detector_id": setup.detector_id,
        "created_at": setup.created_at.isoformat() if setup.created_at else None,
    }


@router.delete("/projects/{project_id}/setups/{setup_id}")
def delete_setup(project_id: int, setup_id: int, session: Session = Depends(get_db_session)):
    """删除方案."""
    setup = (
        session.query(ProjectSetup)
        .filter(ProjectSetup.id == setup_id, ProjectSetup.project_id == project_id)
        .first()
    )
    if not setup:
        raise HTTPException(status_code=404, detail="Setup not found")
    session.delete(setup)
    session.commit()
    return {"deleted": True}


@router.post("/projects/{project_id}/report")
def generate_project_report(
    project_id: int,
    req: ProjectReportReq,
    session: Session = Depends(get_db_session),
):
    """聚合项目下所有方案的匹配历史，生成综合选型建议书."""
    from fastapi.responses import Response as FastAPIResponse

    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    setups = (
        session.query(ProjectSetup)
        .filter(ProjectSetup.project_id == project_id)
        .order_by(ProjectSetup.created_at.desc())
        .all()
    )

    # Collect match result snapshots
    aggregated_results: list[dict] = []
    for s in setups:
        if s.match_result_snapshot:
            try:
                snap = json.loads(s.match_result_snapshot)
                if isinstance(snap, dict):
                    aggregated_results.append(snap)
                elif isinstance(snap, list) and snap:
                    aggregated_results.extend(snap)
            except json.JSONDecodeError:
                continue

    if not aggregated_results:
        raise HTTPException(status_code=400, detail="项目中没有可聚合的匹配记录")

    # Build synthetic requirements from project info
    synthetic_requirements = {
        "project_name": project.name,
        "domain": project.domain or "-",
        "setup_count": len(setups),
    }

    # Deduplicate by lens+detector combo, keep highest score
    seen: set[str] = set()
    unique_results: list[dict] = []
    for r in sorted(aggregated_results, key=lambda x: x.get("score", 0), reverse=True):
        key = f"{r.get('lens_id')}-{r.get('detector_id')}"
        if key not in seen:
            seen.add(key)
            unique_results.append(r)

    try:
        if req.format == "pdf":
            from lensfit.export.pdf_exporter import generate_pdf_report
            pdf_bytes = generate_pdf_report(synthetic_requirements, unique_results, top_k=50)
            return FastAPIResponse(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={
                    "Content-Disposition": (
                        f"attachment; filename=lensfit-project-{project_id}-report.pdf"
                    ),
                },
            )
        else:
            from lensfit.export.excel_exporter import generate_excel_report
            excel_bytes = generate_excel_report(
                synthetic_requirements, unique_results, top_k=50
            )
            return FastAPIResponse(
                content=excel_bytes,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": (
                        f"attachment; filename=lensfit-project-{project_id}-report.xlsx"
                    ),
                },
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")
