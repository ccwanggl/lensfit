"""Curriculum — declarative learning-path graph (loader + DAG builder)."""

from optibench.curriculum.graph import CurriculumEdge, CurriculumGraph, RefResolver
from optibench.curriculum.loader import (
    CurriculumError,
    CurriculumNode,
    load_curriculum,
    resolve_curriculum_path,
)

__all__ = [
    "CurriculumEdge",
    "CurriculumError",
    "CurriculumGraph",
    "CurriculumNode",
    "RefResolver",
    "get_curriculum_graph",
    "load_curriculum",
    "reset_curriculum_graph",
    "resolve_curriculum_path",
]

_GRAPH: CurriculumGraph | None = None


def get_curriculum_graph() -> CurriculumGraph:
    """Return the shared curriculum graph, built on first access."""
    global _GRAPH
    if _GRAPH is None:
        _GRAPH = CurriculumGraph.build(load_curriculum(resolve_curriculum_path()))
    return _GRAPH


def reset_curriculum_graph() -> None:
    """Drop the cached graph (used by tests)."""
    global _GRAPH
    _GRAPH = None
