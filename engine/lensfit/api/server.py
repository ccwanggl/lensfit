"""FastAPI server for LensFit engine."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Generator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response as FastAPIResponse
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from lensfit.api import catalog_router
from lensfit.db.catalog import CatalogQuery
from lensfit.db.models import (
    DetectorCatalog,
    LensCatalog,
    Project,
    ProjectSetup,
    init_db,
)
from lensfit.domains.base import Requirements
from lensfit.domains.industrial import IndustrialVisionModule
from lensfit.domains.infrared import InfraredModule
from lensfit.domains.microscope import MicroscopyModule
from lensfit.domains.photography import PhotographyModule
from lensfit.knowledge.constraints import ALL_CONSTRAINTS
from lensfit.knowledge.engine import KnowledgeInferenceEngine, OpticalKnowledgeBase
from lensfit.knowledge.formulas import list_formulas as kb_list_formulas
from lensfit.knowledge.presets import get_preset_by_id, list_presets
from lensfit.matching.engine import MatchingEngine

# Global instances
_engine: MatchingEngine | None = None
_session_maker = None


def get_db_session() -> Generator[Any, None, None]:
    """Yield a database session for FastAPI dependency injection."""
    if _session_maker is None:
        raise RuntimeError("Database session maker not initialized")
    session = _session_maker()
    try:
        yield session
    finally:
        session.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    global _engine, _session_maker
    # Skip initialization if globals are already set (e.g., in tests)
    if _engine is not None and _session_maker is not None:
        yield
        return

    db_url = getattr(app.state, "db_url", None) or "sqlite:///lensfit.db"

    init_db(db_url)

    # SQLite requires check_same_thread=False for use in FastAPI thread pool
    connect_args = {"check_same_thread": False}
    db_engine = create_engine(
        db_url,
        echo=False,
        connect_args=connect_args,
        poolclass=StaticPool,
    )
    _session_maker = sessionmaker(bind=db_engine)

    _engine = MatchingEngine(_session_maker)
    _engine.register_domain(IndustrialVisionModule())
    _engine.register_domain(MicroscopyModule())
    _engine.register_domain(InfraredModule())
    _engine.register_domain(PhotographyModule())

    # In desktop mode, expose the API key to the local sidecar supervisor via stdout
    # so the Tauri host can forward it to the frontend without leaking it over HTTP.
    if getattr(app.state, "mode", None) == "desktop":
        print(f"LENSFIT_API_KEY {_API_KEY}", flush=True)

    yield
    _engine = None


# API Key — generated at startup if not provided via env
_API_KEY = os.environ.get("LENSFIT_API_KEY") or os.urandom(32).hex()


def verify_api_key(request: Request) -> None:
    """Verify X-API-Key header for non-health endpoints in desktop mode."""
    if request.url.path == "/health":
        return
    # In dev/web mode we rely on local network/CORS instead of the API key.
    if getattr(request.app.state, "mode", "desktop") != "desktop":
        return
    key = request.headers.get("X-API-Key")
    if key != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app = FastAPI(
    title="LensFit Engine API",
    version="1.0.0",
    lifespan=lifespan,
    dependencies=[Depends(verify_api_key)],
)

# CORS: only allow known local origins for desktop/web dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5173",   # Vite dev
        "http://localhost:5173",   # Vite dev fallback
        "http://localhost:1420",   # Tauri dev
        "http://localhost:3000",   # Alternative dev
        "tauri://localhost",       # Tauri production
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key"],
)

app.include_router(catalog_router.router)


# =====================================================================
# Health
# =====================================================================
@app.get("/health")
def health_check():
    """Health check endpoint — Sidecar Supervisor polls this."""
    return {"status": "ok", "version": "1.0.0"}


# =====================================================================
# Domains
# =====================================================================
@app.get("/api/v1/domains")
def list_domains():
    """列出所有已注册领域."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    return {
        "items": [
            {"id": d.domain_id, "name": d.domain_name}
            for d in _engine.domains.values()
        ]
    }


@app.get("/api/v1/domains/{domain}/parameters")
def get_domain_parameters(domain: str):
    """获取指定领域的参数定义 — 用于前端动态渲染表单."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    try:
        module = _engine.get_domain(domain)
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


# =====================================================================
# Calculate
# =====================================================================
class CalculateReq(BaseModel):
    working_distance: float | None = None
    sensor_w: float | None = None
    fov_w: float | None = None
    focal_length: float | None = None
    sensor_h: float | None = None
    fov_h: float | None = None


@app.post("/api/v1/calculate")
def calculate(params: CalculateReq):
    """基础光学计算（薄透镜公式）."""
    from lensfit.core.thin_lens import ThinLensCalculator
    from lensfit.core.types import OpticalParams

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


# =====================================================================
# Matching
# =====================================================================
class MatchReq(BaseModel):
    domain: str = Field(default="industrial", max_length=32)
    requirements: dict


@app.post("/api/v1/match/async")
def start_matching(req: MatchReq):
    """启动异步匹配任务."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    requirements = Requirements(
        domain=req.domain,
        params=req.requirements,
    )
    task = _engine.match_async(requirements)
    return {
        "task_id": task.task_id,
        "status": task.status,
        "created_at": task.created_at.isoformat(),
    }


@app.post("/api/v1/match/stream")
def start_matching_stream(req: MatchReq):
    """启动渐进式 SSE 流式匹配 — 实时推送各阶段结果."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    requirements = Requirements(
        domain=req.domain,
        params=req.requirements,
    )

    def event_generator():
        try:
            for chunk in _engine.match_progressive(requirements):
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


@app.get("/api/v1/match/async/{task_id}")
def get_matching_status(task_id: str):
    """查询匹配任务状态."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    task = _engine.get_task(task_id)
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


@app.get("/api/v1/match/async/{task_id}/result")
def get_matching_result(task_id: str):
    """获取已完成任务的匹配结果."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    task = _engine.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"Task status: {task.status}")

    top_matches = (task.result or [])[:20]
    explanations = {}
    for r in top_matches:
        try:
            explanations[f"{r.lens_id}-{r.detector_id}"] = _engine.explain_result(r)
        except Exception:
            pass

    return {
        "top_matches": [r.to_dict() for r in top_matches],
        "diagnostics": [d.to_dict() for d in (task.diagnostics or [])],
        "explanations": explanations,
    }


@app.delete("/api/v1/match/async/{task_id}")
def cancel_matching(task_id: str):
    """取消正在执行的任务."""
    if _engine is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    cancelled = _engine.cancel_task(task_id)
    return {"cancelled": cancelled}


# =====================================================================
# Knowledge Base
# =====================================================================
_knowledge_engine = KnowledgeInferenceEngine(OpticalKnowledgeBase())


@app.get("/api/v1/knowledge/formulas")
def list_knowledge_formulas(domain: str | None = None):
    """列出光学公式库."""
    formulas = kb_list_formulas(domain)
    return {"items": [f.to_dict() for f in formulas]}


@app.get("/api/v1/knowledge/constraints")
def list_knowledge_constraints():
    """列出物理约束库."""
    return {"items": [c.to_dict() for c in ALL_CONSTRAINTS]}


class InferReq(BaseModel):
    params: dict
    domain: str = Field(default="all", max_length=32)


@app.post("/api/v1/knowledge/infer")
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


@app.get("/api/v1/knowledge/presets")
def list_knowledge_presets(domain: str | None = None):
    """列出专业预设配置方案."""
    presets = list_presets(domain)
    return {"items": [p.to_dict() for p in presets]}


@app.get("/api/v1/knowledge/presets/{preset_id}")
def get_knowledge_preset(preset_id: str):
    """获取单个预设配置详情."""
    preset = get_preset_by_id(preset_id)
    if not preset:
        raise HTTPException(status_code=404, detail=f"Preset not found: {preset_id}")
    return preset.to_dict()


# =====================================================================
# Visualization
# =====================================================================
class CoverageReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)


@app.post("/api/v1/visualize/coverage")
def generate_coverage_data(req: CoverageReq):
    """生成传感器覆盖图几何数据."""
    from lensfit.visualization.coverage import CoveragePlotData

    if _engine is None or _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    with _session_maker() as session:
        catalog = CatalogQuery(session)
        lens = catalog.get_lens_by_id(req.lens_id)
        det = catalog.get_detector_by_id(req.detector_id)

        if not lens or not det:
            raise HTTPException(status_code=404, detail="Lens or detector not found")

        plot = CoveragePlotData(
            sensor_w=det.sensor_w_mm or 0,
            sensor_h=det.sensor_h_mm or 0,
            image_circle=lens.image_circle_mm or 0,
        )
        return plot.generate()


class MtfReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)


@app.post("/api/v1/visualize/mtf")
def generate_mtf_data(req: MtfReq):
    """生成镜头 MTF 曲线数据（基于 mtf50_lpmm 估算）."""
    from lensfit.visualization.mtf import MtfPlotData

    if _engine is None or _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    with _session_maker() as session:
        catalog = CatalogQuery(session)
        lens = catalog.get_lens_by_id(req.lens_id)
        det = catalog.get_detector_by_id(req.detector_id)

        if not lens or not det:
            raise HTTPException(status_code=404, detail="Lens or detector not found")

        mtf50 = lens.mtf50_lpmm
        if mtf50 is None or mtf50 <= 0:
            raise HTTPException(
                status_code=422, detail="Lens has no valid MTF50 data for plotting"
            )

        plot = MtfPlotData(
            mtf50_lpmm=mtf50,
            pixel_size_um=det.pixel_size_um,
        )
        return plot.generate()


class CocReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)
    focus_distance_m: float = Field(default=2.0, gt=0)


@app.post("/api/v1/visualize/coc")
def generate_coc_data(req: CocReq):
    """生成摄影景深/弥散圆数据（基于镜头与传感器参数估算）."""
    from lensfit.visualization.coc import CocPlotData

    if _engine is None or _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    with _session_maker() as session:
        catalog = CatalogQuery(session)
        lens = catalog.get_lens_by_id(req.lens_id)
        det = catalog.get_detector_by_id(req.detector_id)

        if not lens or not det:
            raise HTTPException(status_code=404, detail="Lens or detector not found")

        focal_length = lens.focal_length_mm
        max_aperture = lens.max_aperture
        if not focal_length or focal_length <= 0:
            raise HTTPException(
                status_code=422, detail="Lens has no valid focal length for CoC plot"
            )
        if not max_aperture or max_aperture <= 0:
            raise HTTPException(
                status_code=422, detail="Lens has no valid aperture for CoC plot"
            )
        if (
            not det.sensor_w_mm
            or det.sensor_w_mm <= 0
            or not det.sensor_h_mm
            or det.sensor_h_mm <= 0
        ):
            raise HTTPException(
                status_code=422, detail="Detector has no valid sensor dimensions for CoC plot"
            )
        if not det.pixel_size_um or det.pixel_size_um <= 0:
            raise HTTPException(
                status_code=422, detail="Detector has no valid pixel size for CoC plot"
            )

        plot = CocPlotData(
            focal_length_mm=focal_length,
            max_aperture=max_aperture,
            sensor_w_mm=det.sensor_w_mm,
            sensor_h_mm=det.sensor_h_mm,
            pixel_size_um=det.pixel_size_um,
            focus_distance_m=req.focus_distance_m,
        )
        return plot.generate()


# =====================================================================
# Project & Setup Management
# =====================================================================
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


@app.get("/api/v1/projects")
def list_projects():
    """列出项目."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
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


@app.post("/api/v1/projects")
def create_project(req: CreateProjectReq):
    """创建项目."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
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


@app.get("/api/v1/projects/{project_id}/setups")
def list_setups(project_id: int):
    """列出方案."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
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


@app.delete("/api/v1/projects/{project_id}")
def delete_project(project_id: int):
    """删除项目及其下所有方案."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
        project = session.get(Project, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        session.query(ProjectSetup).filter(ProjectSetup.project_id == project_id).delete()
        session.delete(project)
        session.commit()
        return {"deleted": True}


@app.post("/api/v1/projects/{project_id}/setups")
def save_setup(project_id: int, req: CreateSetupReq):
    """保存方案."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
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


@app.delete("/api/v1/projects/{project_id}/setups/{setup_id}")
def delete_setup(project_id: int, setup_id: int):
    """删除方案."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")
    with _session_maker() as session:
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


def _safe_json_loads(raw: str | None) -> Any | None:
    """Safely load a JSON string, returning None on failure."""
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def _model_to_dict(obj):
    """Convert SQLAlchemy model to plain dict (excluding relationships)."""
    from datetime import datetime

    result = {}
    for c in obj.__table__.columns:
        val = getattr(obj, c.name)
        if isinstance(val, datetime):
            val = val.isoformat()
        result[c.name] = val
    return result


# =====================================================================
# Export
# =====================================================================
class ExportReq(BaseModel):
    requirements: dict
    results: list[dict]
    format: str = Field(default="pdf", pattern=r"^(pdf|excel|csv)$")
    top_k: int = Field(default=10, ge=1, le=1000)
    diagnostics: list[dict] | None = None
    what_if_results: list[dict] | None = None


@app.post("/api/v1/export")
def export_results(req: ExportReq):
    """导出匹配结果为 PDF、Excel 或 CSV."""
    try:
        if req.format == "pdf":
            from lensfit.export.pdf_exporter import generate_pdf_report

            pdf_bytes = generate_pdf_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=lensfit-report.pdf"},
            )
        elif req.format == "excel":
            from lensfit.export.excel_exporter import generate_excel_report

            excel_bytes = generate_excel_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=excel_bytes,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=lensfit-report.xlsx"},
            )
        elif req.format == "csv":
            from lensfit.export.csv_exporter import generate_csv_report

            csv_bytes = generate_csv_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=csv_bytes,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=lensfit-report.csv"},
            )
        else:
            raise HTTPException(status_code=400, detail="Unsupported format. Use 'pdf', 'excel' or 'csv'.")  # noqa: E501
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


class ProjectReportReq(BaseModel):
    format: str = Field(default="pdf", pattern=r"^(pdf|excel)$")


@app.post("/api/v1/projects/{project_id}/report")
def generate_project_report(project_id: int, req: ProjectReportReq):
    """聚合项目下所有方案的匹配历史，生成综合选型建议书."""
    if _session_maker is None:
        raise HTTPException(status_code=503, detail="Engine not initialized")

    with _session_maker() as session:
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


# =====================================================================
# CLI Entry
# =====================================================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--host", type=str, default="127.0.0.1")
    parser.add_argument("--mode", type=str, default="desktop")
    parser.add_argument("--db", type=str, default="sqlite:///lensfit.db")
    args = parser.parse_args()

    app.state.db_url = args.db
    app.state.mode = args.mode

    import uvicorn
    # Pass the app object directly so uvicorn does not re-import the module
    # and discard state (e.g. mode/db_url) set above.
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
