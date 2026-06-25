"""Workbench domain model for the optical breadboard.

This package contains the solver-neutral SceneGraph and a minimal in-memory
equipment catalog. It deliberately avoids any third-party engine specifics.
"""

from __future__ import annotations

from lensfit.lab.workbench.equipment import CATALOG, EquipmentSpec
from lensfit.lab.workbench.scene import (
    Component,
    Observable,
    SceneGraph,
    Transform,
    Units,
)

__all__ = [
    "CATALOG",
    "Component",
    "EquipmentSpec",
    "Observable",
    "SceneGraph",
    "Transform",
    "Units",
]
