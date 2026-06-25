"""Workbench solver — dispatch a SceneGraph to the appropriate native experiment."""

from __future__ import annotations

from lensfit.lab import get_registry
from lensfit.lab.base import ExperimentResult
from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.native_interpreter import (
    fraunhofer_double_slit_params,
    fraunhofer_single_slit_params,
)
from lensfit.lab.workbench.ray_optics_adapter import run_ray_optics
from lensfit.lab.workbench.ray_optics_sidecar import RayOpticsError


class WorkbenchSolver:
    """Solver for SceneGraph v1.

    Dispatches ``fraunhofer_intensity`` to the appropriate native experiment
    based on the aperture component. Later phases can add ray-optics adapter
    dispatch here without changing the SceneGraph model.
    """

    def solve(
        self, scene: SceneGraph, *, include_ray_image: bool = False
    ) -> ExperimentResult:
        if not scene.observables:
            raise ValueError("SceneGraph must contain at least one observable")

        observable = scene.observables[0]

        if observable.type != "fraunhofer_intensity":
            raise ValueError(
                f"SceneGraph v1 does not support observable type: {observable.type}"
            )

        aperture = scene._component_by_category("aperture")
        registry = get_registry()

        if aperture.spec_id == "single-slit":
            params, warnings = fraunhofer_single_slit_params(scene)
            result = registry.run("single-slit-diffraction", params)
        elif aperture.spec_id == "double-slit":
            params, warnings = fraunhofer_double_slit_params(scene)
            result = registry.run("double-slit", params)
        else:
            raise ValueError(
                f"SceneGraph v1 does not support aperture type: {aperture.spec_id}"
            )

        result.warnings = warnings + result.warnings

        if observable.type == "fraunhofer_intensity":
            try:
                ray_data = run_ray_optics(
                    scene, include_image=include_ray_image
                )
                result.data["ray_optics"] = ray_data
            except RayOpticsError as exc:
                result.warnings.append(
                    f"几何光学叠加层（ray-optics）不可用：{exc}"
                )
                result.data["ray_optics"] = {
                    "available": False,
                    "error": str(exc),
                }

        return result
