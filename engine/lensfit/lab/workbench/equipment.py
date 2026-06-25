"""Minimal in-memory equipment catalog for the optics workbench.

This catalog is intentionally small for SceneGraph v1. It only describes the
semantic `spec_id`s that the workbench understands. Solver-specific mappings
must live in adapter modules, not here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EquipmentSpec:
    spec_id: str
    category: str
    name: str
    default_params: dict[str, Any]


CATALOG: dict[str, EquipmentSpec] = {
    "laser-monochrome": EquipmentSpec(
        spec_id="laser-monochrome",
        category="source",
        name="单色激光器",
        default_params={"wavelength_nm": 550.0},
    ),
    "single-slit": EquipmentSpec(
        spec_id="single-slit",
        category="aperture",
        name="单缝光阑",
        default_params={"slit_width_um": 50.0},
    ),
    "screen": EquipmentSpec(
        spec_id="screen",
        category="screen",
        name="接收屏",
        default_params={},
    ),
}
