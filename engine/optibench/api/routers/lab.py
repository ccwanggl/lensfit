"""Optics lab API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from optibench.lab import get_registry
from optibench.lab.schemas import (
    ExperimentListResponse,
    ExperimentRunRequest,
    ExperimentRunResponse,
    WorkbenchRunRequest,
)
from optibench.lab.workbench.solver import WorkbenchSolver

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


