"""PracticeActivity — the only interface the learning layer uses to reference
practice capabilities (matching domains, breadboard presets).

Per ADR-003 the learning layer must not import matching-pipeline internals;
it depends solely on this interface. Implementations register themselves in
:mod:`optibench.practice.matching` and :mod:`optibench.practice.breadboard`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

PracticeKind = Literal["domain", "preset"]


@dataclass
class PracticeActivity:
    """A practice activity that curriculum nodes can reference.

    ``entry`` carries frontend positioning info (e.g. which app tab or lab
    experiment to open); the engine treats it as opaque data.
    """

    id: str
    title: str
    kind: PracticeKind
    entry: dict[str, Any] = field(default_factory=dict)

    def available(self) -> bool:
        """Whether the activity can be launched in the current build."""
        return True


class PracticeRegistry:
    """Registry of all practice activities."""

    def __init__(self):
        self._activities: dict[str, PracticeActivity] = {}

    def register(self, activity: PracticeActivity) -> None:
        if not activity.id:
            raise ValueError("PracticeActivity must have an id")
        self._activities[activity.id] = activity

    def get(self, activity_id: str) -> PracticeActivity | None:
        return self._activities.get(activity_id)

    def list(self, kind: PracticeKind | None = None) -> list[PracticeActivity]:
        activities = self._activities.values()
        if kind is None:
            return list(activities)
        return [a for a in activities if a.kind == kind]


_REGISTRY: PracticeRegistry | None = None


def get_practice_registry() -> PracticeRegistry:
    """Return the shared practice registry, built on first access."""
    global _REGISTRY
    if _REGISTRY is None:
        registry = PracticeRegistry()
        # Imports register their activities into the registry.
        from optibench.practice import breadboard, matching

        for activity in matching.activities() + breadboard.activities():
            registry.register(activity)
        _REGISTRY = registry
    return _REGISTRY
