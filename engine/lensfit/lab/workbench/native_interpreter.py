"""Native interpreter: translate a SceneGraph into experiment parameters.

This module maps LensFit's own SceneGraph to the existing parameterized
experiments. It does not invoke any third-party engine.
"""

from __future__ import annotations

from typing import Any

from lensfit.lab.workbench import SceneGraph


def fraunhofer_single_slit_params(
    scene: SceneGraph,
) -> tuple[dict[str, Any], list[str]]:
    """Map a SceneGraph v1 single-slit scene to SingleSlitDiffractionExperiment params.

    The far-field Fraunhofer criterion is ``L >> a^2 / λ``. If the configured
    screen distance is too small, a warning is returned so the UI can tell the
    learner the result is no longer in the Fraunhofer regime.
    """
    source = scene._component_by_category("source")
    aperture = scene._component_by_category("aperture")

    wavelength_nm = float(source.params.get("wavelength_nm", 550.0))
    slit_width_um = float(aperture.params.get("slit_width_um", 50.0))
    screen_distance_m = scene.screen_distance_m()

    a_m = slit_width_um * 1e-6
    lambda_m = wavelength_nm * 1e-9
    far_field_m = a_m**2 / lambda_m if lambda_m > 0 else 0.0

    warnings: list[str] = []
    if far_field_m > 0 and screen_distance_m < 10 * far_field_m:
        warnings.append(
            f"当前屏距 {screen_distance_m:.3f} m 可能不满足夫琅禾费远场条件 "
            f"（建议远大于 {10 * far_field_m:.3f} m）。"
        )

    params = {
        "wavelength_nm": wavelength_nm,
        "slit_width_um": slit_width_um,
        "screen_distance_m": screen_distance_m,
    }
    return params, warnings


def fraunhofer_double_slit_params(
    scene: SceneGraph,
) -> tuple[dict[str, Any], list[str]]:
    """Map a SceneGraph v1 double-slit scene to DoubleSlitExperiment params.

    The same Fraunhofer far-field criterion applies: ``L >> a^2 / λ``.
    """
    source = scene._component_by_category("source")
    aperture = scene._component_by_category("aperture")

    wavelength_nm = float(source.params.get("wavelength_nm", 550.0))
    slit_width_um = float(aperture.params.get("slit_width_um", 20.0))
    slit_separation_um = float(aperture.params.get("slit_separation_um", 100.0))
    screen_distance_m = scene.screen_distance_m()

    a_m = slit_width_um * 1e-6
    lambda_m = wavelength_nm * 1e-9
    far_field_m = a_m**2 / lambda_m if lambda_m > 0 else 0.0

    warnings: list[str] = []
    if far_field_m > 0 and screen_distance_m < 10 * far_field_m:
        warnings.append(
            f"当前屏距 {screen_distance_m:.3f} m 可能不满足夫琅禾费远场条件 "
            f"（建议远大于 {10 * far_field_m:.3f} m）。"
        )

    params = {
        "wavelength_nm": wavelength_nm,
        "slit_width_um": slit_width_um,
        "slit_separation_um": slit_separation_um,
        "screen_distance_m": screen_distance_m,
    }
    return params, warnings
