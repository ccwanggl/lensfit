"""Adapter: SceneGraph v1 -> ray-optics geometric-optics scene.

The adapter is deliberately isolated from the SceneGraph model. It is the
only place where third-party ray-optics type names such as ``PointSource``,
``Blocker`` and ``Detector`` appear.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from lensfit.lab.workbench import SceneGraph
from lensfit.lab.workbench.ray_optics_sidecar import (
    RayOpticsOutputError,
    RayOpticsRuntimeError,
    RayOpticsSidecar,
)

# The ray-optics engine emits a fixed number of angular rays per unit ray
# density. Micro-scale slits (tens of microns) would be missed at moderate
# densities, producing empty detectors. Scaling only the transverse (y)
# dimension makes the slits large enough to sample while preserving the
# angular distribution: the on-screen pattern is simply scaled by the same
# factor and is divided back out when the result is normalized.
_Y_SCALE = 1000.0

# Fixed optical layout. The source is placed at x=0, the aperture at x=100 mm,
# and the screen one screen-distance beyond the aperture. These match the
# locked breadboard presets and keep the angular magnification predictable.
_APERTURE_X_MM = 100.0

# Detector covers +/- this many millimeters on the screen. This is large
# enough to capture the typical Fraunhofer pattern around the central maximum.
_DETECTOR_HALF_HEIGHT_MM = 100.0
_BIN_SIZE_MM = 0.05

# Scene-level ray density. Higher values sample tiny apertures better but
# increase runtime roughly linearly. The chosen value is a compromise that
# still produces a usable curve for 1 μm slits after the y-scale trick.
_RAY_MODE_DENSITY = 5


def _um_to_mm(value_um: float) -> float:
    return float(value_um) / 1000.0


def _runner_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "third_party" / "ray-optics"


def _has_node_canvas() -> bool:
    """Return True if the runner directory has node-canvas installed."""
    return (_runner_dir() / "node_modules" / "canvas" / "package.json").exists()


def _blocker(x: float, y1: float, y2: float) -> dict[str, Any]:
    return {"type": "Blocker", "p1": {"x": x, "y": y1}, "p2": {"x": x, "y": y2}}


def to_ray_optics_scene(
    scene: SceneGraph, *, include_image: bool = False
) -> dict[str, Any]:
    """Convert a SceneGraph v1 into a ray-optics JSON scene.

    The returned dict is safe to pass to :class:`RayOpticsSidecar` (it contains
    no file paths or URLs).

    Args:
        scene: The SceneGraph v1 to convert.
        include_image: If True (and node-canvas is installed), append a
            ``CropBox`` object so the runner also emits a rendered PNG.
    """
    source = scene._component_by_category("source")
    aperture = scene._component_by_category("aperture")
    screen = scene._component_by_category("screen")

    wavelength_nm = float(source.params.get("wavelength_nm", 550.0))
    screen_distance_m = scene.screen_distance_m()

    # Shift the whole layout so the source sits at x=0. This makes the
    # angular magnification (screen_x / aperture_x) independent of absolute
    # breadboard offsets.
    aperture_x_mm = aperture.transform.x_mm - source.transform.x_mm
    screen_x_mm = aperture_x_mm + screen_distance_m * 1000.0

    source_y_scaled = source.transform.y_mm * _Y_SCALE
    aperture_y_scaled = aperture.transform.y_mm * _Y_SCALE
    screen_y_scaled = screen.transform.y_mm * _Y_SCALE

    objs: list[dict[str, Any]] = [
        {
            "type": "PointSource",
            "x": 0.0,
            "y": source_y_scaled,
            "wavelength": wavelength_nm,
            "brightness": 0.5,
        }
    ]

    params = scene.params_for(aperture.id)

    if aperture.spec_id == "single-slit":
        half_width_mm = _um_to_mm(float(params.get("slit_width_um", 50.0)))
        half_scaled = half_width_mm * _Y_SCALE
        aperture_extent_y = half_scaled
        objs.append(
            _blocker(
                aperture_x_mm,
                aperture_y_scaled - 1e6,
                aperture_y_scaled - half_scaled,
            )
        )
        objs.append(
            _blocker(
                aperture_x_mm,
                aperture_y_scaled + half_scaled,
                aperture_y_scaled + 1e6,
            )
        )
    elif aperture.spec_id == "double-slit":
        half_width_mm = _um_to_mm(float(params.get("slit_width_um", 20.0)))
        half_sep_mm = _um_to_mm(float(params.get("slit_separation_um", 100.0))) / 2.0
        half_width_scaled = half_width_mm * _Y_SCALE
        half_sep_scaled = half_sep_mm * _Y_SCALE
        aperture_extent_y = half_sep_scaled + half_width_scaled

        lower_center = aperture_y_scaled - half_sep_scaled
        upper_center = aperture_y_scaled + half_sep_scaled

        objs.append(
            _blocker(
                aperture_x_mm,
                aperture_y_scaled - 1e6,
                lower_center - half_width_scaled,
            )
        )
        objs.append(
            _blocker(
                aperture_x_mm,
                lower_center + half_width_scaled,
                upper_center - half_width_scaled,
            )
        )
        objs.append(
            _blocker(
                aperture_x_mm,
                upper_center + half_width_scaled,
                aperture_y_scaled + 1e6,
            )
        )
    else:
        raise ValueError(
            f"ray-optics adapter does not support aperture type: {aperture.spec_id}"
        )

    half_height_scaled = _DETECTOR_HALF_HEIGHT_MM * _Y_SCALE
    bin_size_scaled = _BIN_SIZE_MM * _Y_SCALE
    objs.append(
        {
            "type": "Detector",
            "p1": {
                "x": screen_x_mm,
                "y": screen_y_scaled - half_height_scaled,
            },
            "p2": {
                "x": screen_x_mm,
                "y": screen_y_scaled + half_height_scaled,
            },
            "irradMap": True,
            "binSize": bin_size_scaled,
        }
    )

    # If explicitly requested and node-canvas is available, ask the runner to
    # render a 2D ray diagram. The crop region covers the source-to-screen
    # optical axis with enough vertical margin to show the geometric light cone.
    if include_image and _has_node_canvas():
        crop_half_y_scaled = max(500.0, aperture_extent_y + 200.0)
        objs.append(
            {
                "type": "CropBox",
                "p1": {"x": -50.0, "y": -crop_half_y_scaled},
                "p4": {"x": screen_x_mm + 50.0, "y": crop_half_y_scaled},
                "width": 640,
            }
        )

    return {
        "version": 5,
        "rayModeDensity": _RAY_MODE_DENSITY,
        "objs": objs,
    }


def _normalize_detector(
    detector: dict[str, Any], screen_y_mm: float, half_height_mm: float
) -> dict[str, Any]:
    """Turn a raw ray-optics detector reading into a stable overlay dataset."""
    irradiance_map = list(detector.get("irradianceMap", []))
    bin_positions = list(detector.get("binPositions", []))

    if len(irradiance_map) != len(bin_positions):
        raise RayOpticsOutputError(
            "ray-optics detector irradianceMap/binPositions length mismatch"
        )

    max_value = max(irradiance_map) if irradiance_map else 0.0

    samples: list[dict[str, float]] = []
    for pos, value in zip(bin_positions, irradiance_map):
        # binPosition is measured from the detector's p1 along its length.
        y_actual = screen_y_mm - half_height_mm + pos / _Y_SCALE
        intensity = value / max_value if max_value > 0 else 0.0
        samples.append({"y_mm": y_actual, "intensity": float(intensity)})

    return {
        "power": detector.get("power"),
        "normal": detector.get("normal"),
        "samples": samples,
    }


def run_ray_optics(
    scene: SceneGraph,
    sidecar: RayOpticsSidecar | None = None,
    *,
    include_image: bool = False,
) -> dict[str, Any]:
    """Run a SceneGraph through the ray-optics sidecar and normalize the result.

    Returns a dict with keys:

    - ``available``: True
    - ``samples``: list of ``{y_mm, intensity}`` normalized to [0, 1]
    - ``power``, ``normal``: raw detector integrals
    - ``image``: base64 PNG data URL of the 2D ray diagram (only when
      ``include_image`` is True and node-canvas is installed), otherwise ``None``
    - ``warning``: runner-level warning, if any

    Raises the same exceptions as :class:`RayOpticsSidecar` when the sidecar
    cannot produce a usable result.
    """
    sidecar = sidecar or RayOpticsSidecar()
    ray_scene = to_ray_optics_scene(scene, include_image=include_image)
    result = sidecar.run(ray_scene)

    if not result.detectors:
        raise RayOpticsRuntimeError("ray-optics scene produced no detector output")

    screen = scene._component_by_category("screen")
    data = _normalize_detector(
        result.detectors[0], screen.transform.y_mm, _DETECTOR_HALF_HEIGHT_MM
    )
    data["available"] = True
    data["warning"] = result.warning
    data["image"] = result.images[0]["dataUrl"] if result.images else None
    return data
