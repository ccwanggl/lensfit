"""LensFit optics lab: interactive experiments for self-study."""

from __future__ import annotations

from lensfit.lab.base import (
    Difficulty,
    ExperimentInfo,
    ExperimentResult,
    OpticsExperiment,
    Parameter,
    ParameterType,
)
from lensfit.lab.registry import ExperimentRegistry, get_registry

__all__ = [
    "Difficulty",
    "ExperimentInfo",
    "ExperimentRegistry",
    "ExperimentResult",
    "OpticsExperiment",
    "Parameter",
    "ParameterType",
    "get_registry",
]
