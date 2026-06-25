"""Workbench solver — dispatch a SceneGraph to the appropriate native experiment."""

from __future__ import annotations

from lensfit.lab import get_registry
from lensfit.lab.base import ExperimentResult
from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.native_interpreter import (
    fraunhofer_double_slit_params,
    fraunhofer_single_slit_params,
)


class WorkbenchSolver:
    """Solver for SceneGraph v1.

    Dispatches ``fraunhofer_intensity`` to the appropriate native experiment
    based on the aperture component. Later phases can add ray-optics adapter
    dispatch here without changing the SceneGraph model.
    """

    def solve(self, scene: SceneGraph) -> ExperimentResult:
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
        return result
