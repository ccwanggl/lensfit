"""Base classes for LensFit optics experiments."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

ParameterType = Literal["float", "int", "bool", "choice", "enum"]
Difficulty = Literal["foundation", "intermediate", "advanced"]


@dataclass
class Parameter:
    """A tunable experiment parameter."""

    name: str
    label: str
    type: ParameterType = "float"
    default: Any = None
    min: float | int | None = None
    max: float | int | None = None
    step: float | int | None = None
    unit: str | None = None
    options: list[dict[str, Any]] = field(default_factory=list)
    description: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "label": self.label,
            "type": self.type,
            "default": self.default,
            "min": self.min,
            "max": self.max,
            "step": self.step,
            "unit": self.unit,
            "options": self.options,
            "description": self.description,
        }


@dataclass
class ExperimentResult:
    """Result returned by an experiment run."""

    data: dict[str, Any]
    svg: str
    warnings: list[str] = field(default_factory=list)
    learning_hints: list[str] = field(default_factory=list)


@dataclass
class ExperimentInfo:
    """Static metadata describing an experiment."""

    id: str
    title: str
    description: str
    difficulty: Difficulty
    linked_concepts: list[str]
    linked_formulas: list[str]
    prerequisites: list[str]
    learning_objectives: list[str]
    parameters: list[dict[str, Any]]


class OpticsExperiment(ABC):
    """Abstract base class for a runnable optics experiment."""

    experiment_id: str = ""
    title: str = ""
    description: str = ""
    difficulty: Difficulty = "foundation"
    # Paths relative to OpticKnowledgeSpace, without .md extension
    linked_concepts: list[str] = []
    linked_formulas: list[str] = []
    prerequisites: list[str] = []
    learning_objectives: list[str] = []
    parameters: list[Parameter] = []

    def info(self) -> ExperimentInfo:
        return ExperimentInfo(
            id=self.experiment_id,
            title=self.title,
            description=self.description,
            difficulty=self.difficulty,
            linked_concepts=list(self.linked_concepts),
            linked_formulas=list(self.linked_formulas),
            prerequisites=list(self.prerequisites),
            learning_objectives=list(self.learning_objectives),
            parameters=[p.as_dict() for p in self.parameters],
        )

    @abstractmethod
    def run(self, params: dict[str, Any]) -> ExperimentResult:
        """Run the experiment and return data + SVG visualization."""
        raise NotImplementedError

    def validate_params(self, params: dict[str, Any]) -> dict[str, Any]:
        """Coerce and validate supplied parameters against declared metadata."""
        validated: dict[str, Any] = {}
        for p in self.parameters:
            value = params.get(p.name, p.default)
            if p.type in ("float", "int"):
                try:
                    value = float(value) if p.type == "float" else int(value)
                except (TypeError, ValueError) as exc:
                    raise ValueError(f"Parameter '{p.name}' must be numeric") from exc
                if p.min is not None:
                    value = max(p.min, value)
                if p.max is not None:
                    value = min(p.max, value)
            elif p.type == "bool":
                value = bool(value)
            elif p.type in ("choice", "enum"):
                valid = {opt.get("value") for opt in p.options}
                if value not in valid:
                    raise ValueError(
                        f"Parameter '{p.name}' must be one of {sorted(valid - {None})}"
                    )
            validated[p.name] = value
        return validated
