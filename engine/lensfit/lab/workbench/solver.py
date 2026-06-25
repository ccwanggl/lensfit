"""Workbench solver — dispatch a SceneGraph to the appropriate native experiment."""

from __future__ import annotations

from lensfit.lab import get_registry
from lensfit.lab.base import ExperimentResult
from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.native_interpreter import fraunhofer_single_slit_params


class WorkbenchSolver:
    """Solver for SceneGraph v1.

    This first version only supports the ``fraunhofer_intensity`` observable
    mapped to the existing ``single-slit-diffraction`` experiment. Later
    phases can add ray-optics adapter dispatch here without changing the
    SceneGraph model.
    """

    def solve(self, scene: SceneGraph) -> ExperimentResult:
        if not scene.observables:
            raise ValueError("SceneGraph must contain at least one observable")

        observable = scene.observables[0]

        if observable.type != "fraunhofer_intensity":
            raise ValueError(
                f"SceneGraph v1 does not support observable type: {observable.type}"
            )

        params, warnings = fraunhofer_single_slit_params(scene)
        registry = get_registry()
        result = registry.run("single-slit-diffraction", params)
        result.warnings = warnings + result.warnings
        return result
