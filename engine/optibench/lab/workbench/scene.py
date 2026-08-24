"""SceneGraph v1 — solver-neutral breadboard scene model.

All coordinates use breadboard units (millimeters), angles are in degrees, and
wavelengths are in nanometers. The model is intentionally free of any
third-party engine identifiers such as ``SingleRay`` or ``SphericalLens``.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Units(BaseModel):
    length: Literal["mm"] = "mm"
    angle: Literal["deg"] = "deg"
    wavelength: Literal["nm"] = "nm"


class Transform(BaseModel):
    x_mm: float = 0.0
    y_mm: float = 0.0
    rotation_deg: float = 0.0


class Component(BaseModel):
    id: str = Field(..., min_length=1)
    spec_id: Literal["laser-monochrome", "single-slit", "double-slit", "screen"]
    category: Literal["source", "aperture", "screen"]
    transform: Transform = Field(default_factory=Transform)
    params: dict[str, Any] = Field(default_factory=dict)


class Observable(BaseModel):
    type: Literal["fraunhofer_intensity"]
    source_id: str
    aperture_id: str
    screen_id: str


class SceneGraph(BaseModel):
    version: Literal[1]
    units: Units = Field(default_factory=Units)
    components: list[Component]
    observables: list[Observable]

    @field_validator("components")
    @classmethod
    def _unique_component_ids(cls, components: list[Component]) -> list[Component]:
        ids = [c.id for c in components]
        if len(ids) != len(set(ids)):
            raise ValueError("component ids must be unique within a scene")
        return components

    @model_validator(mode="after")
    def _validate_scene(self) -> SceneGraph:
        by_category: dict[str, list[str]] = {
            "source": [],
            "aperture": [],
            "screen": [],
        }
        for comp in self.components:
            by_category.setdefault(comp.category, []).append(comp.id)

        for category in ("source", "aperture", "screen"):
            count = len(by_category[category])
            if count != 1:
                raise ValueError(
                    f"SceneGraph v1 requires exactly one {category} component, found {count}"
                )

        for comp in self.components:
            if comp.transform.rotation_deg != 0:
                raise ValueError(
                    f"component {comp.id}: rotation_deg must be 0 in SceneGraph v1"
                )

        ids = {c.id for c in self.components}
        for obs in self.observables:
            for ref in (obs.source_id, obs.aperture_id, obs.screen_id):
                if ref not in ids:
                    raise ValueError(
                        f"observable references unknown component id: {ref}"
                    )

        return self

    def _component_by_category(self, category: str) -> Component:
        for comp in self.components:
            if comp.category == category:
                return comp
        raise KeyError(f"no component with category {category}")

    def screen_distance_m(self) -> float:
        """Derive the distance between aperture and screen in meters."""
        aperture = self._component_by_category("aperture")
        screen = self._component_by_category("screen")
        distance_mm = screen.transform.x_mm - aperture.transform.x_mm
        if distance_mm <= 0:
            raise ValueError(
                "screen must be placed after aperture (x_screen > x_aperture)"
            )
        return distance_mm / 1000.0

    def params_for(self, component_id: str) -> dict[str, Any]:
        """Return merged default + override parameters for a component.

        Defaults come from the in-memory equipment catalog. Unknown spec_ids
        cannot occur because pydantic has already validated the scene.
        """
        from optibench.lab.workbench.equipment import CATALOG

        comp = next(c for c in self.components if c.id == component_id)
        defaults = CATALOG[comp.spec_id].default_params.copy()
        defaults.update(comp.params)
        return defaults
