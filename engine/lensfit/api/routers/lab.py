"""Optics lab API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from lensfit.lab import get_registry
from lensfit.lab.schemas import (
    ExperimentListResponse,
    ExperimentRunRequest,
    ExperimentRunResponse,
    WorkbenchRunRequest,
)
from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.ray_optics_adapter import run_ray_optics
from lensfit.lab.workbench.ray_optics_sidecar import RayOpticsError
from lensfit.lab.workbench.solver import WorkbenchSolver

router = APIRouter(prefix="/api/v1/lab", tags=["lab"])


@router.get("/experiments", response_model=ExperimentListResponse)
def list_experiments():
    """List all available optics experiments."""
    registry = get_registry()
    return {"items": registry.list_experiments()}


@router.get("/experiments/{experiment_id}", response_model=ExperimentListResponse)
def get_experiment(experiment_id: str):
    """Get metadata for a single experiment."""
    registry = get_registry()
    exp = registry.get(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    return {"items": [exp.info()]}


@router.post("/experiments/{experiment_id}/run", response_model=ExperimentRunResponse)
def run_experiment(experiment_id: str, req: ExperimentRunRequest):
    """Run an experiment with the supplied parameters."""
    registry = get_registry()
    exp = registry.get(experiment_id)
    if exp is None:
        raise HTTPException(status_code=404, detail=f"Experiment not found: {experiment_id}")
    try:
        result = registry.run(experiment_id, req.params)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Experiment failed: {str(e)}") from e

    return {
        "data": result.data,
        "svg": result.svg,
        "warnings": result.warnings,
        "learning_hints": result.learning_hints,
    }


@router.post("/workbench/run", response_model=ExperimentRunResponse)
def run_workbench(req: WorkbenchRunRequest):
    """Run a stateless SceneGraph v1 workbench scene."""
    solver = WorkbenchSolver()
    try:
        result = solver.solve(req.scene, include_ray_image=req.include_ray_image)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workbench solve failed: {str(e)}") from e

    return {
        "data": result.data,
        "svg": result.svg,
        "warnings": result.warnings,
        "learning_hints": result.learning_hints,
    }


@router.post("/workbench/ray-image")
def render_workbench_ray_image(scene: SceneGraph):
    """Render a 2D geometric ray diagram for a SceneGraph v1 scene.

    This is an on-demand, slower operation that is intentionally separate from
    :func:`run_workbench` so the default solve path stays fast.
    """
    try:
        data = run_ray_optics(scene, include_image=True)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except RayOpticsError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ray diagram render failed: {str(e)}"
        ) from e

    if not data.get("image"):
        raise HTTPException(
            status_code=404, detail="Ray diagram image is not available"
        )

    return {"image": data["image"]}
