"""Experiment registry for LensFit optics lab."""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from typing import Any

from lensfit.lab import experiments
from lensfit.lab.base import ExperimentInfo, ExperimentResult, OpticsExperiment


class ExperimentRegistry:
    """Registry of all available optics experiments.

    Experiments are discovered dynamically by scanning ``lensfit.lab.experiments``
    for concrete subclasses of :class:`OpticsExperiment`. This avoids brittle
    hardcoded imports and broken references.
    """

    def __init__(self):
        self._experiments: dict[str, OpticsExperiment] = {}
        self.discover()

    def discover(self) -> None:
        """Discover and register all experiment modules."""
        for importer, modname, ispkg in pkgutil.iter_modules(
            experiments.__path__, experiments.__name__ + "."
        ):
            if ispkg:
                continue
            try:
                module = importlib.import_module(modname)
            except Exception:
                # Skip broken experiment modules so the rest of the lab keeps working.
                continue
            for _name, obj in inspect.getmembers(module):
                if (
                    inspect.isclass(obj)
                    and issubclass(obj, OpticsExperiment)
                    and obj is not OpticsExperiment
                    and not inspect.isabstract(obj)
                    and obj.experiment_id
                ):
                    self.register(obj())

    def register(self, experiment: OpticsExperiment) -> None:
        if not experiment.experiment_id:
            raise ValueError("Experiment must have an experiment_id")
        self._experiments[experiment.experiment_id] = experiment

    def list_experiments(self) -> list[ExperimentInfo]:
        return [exp.info() for exp in self._experiments.values()]

    def get(self, experiment_id: str) -> OpticsExperiment | None:
        return self._experiments.get(experiment_id)

    def run(self, experiment_id: str, params: dict[str, Any]) -> ExperimentResult:
        exp = self.get(experiment_id)
        if exp is None:
            raise KeyError(f"Unknown experiment: {experiment_id}")
        validated = exp.validate_params(params)
        return exp.run(validated)


# Global singleton
_REGISTRY = ExperimentRegistry()


def get_registry() -> ExperimentRegistry:
    return _REGISTRY
