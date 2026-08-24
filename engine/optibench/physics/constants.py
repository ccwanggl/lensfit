"""Physics constants for OptiBench optical calculations.

All constants are versioned to ensure reproducibility and auditability.
When updating a constant value, bump the VERSION and document the change.
"""


class PhysicsConstants:
    """Central registry of optical physics constants."""

    VERSION = "2024.1"

    # ── Diffraction & Resolution ──
    # Rayleigh criterion coefficient for a circular aperture.
    # 0.61 is the standard value for an unobstructed circular aperture.
    # 1.22 is sometimes used for the Airy disk diameter (radius → diameter).
    RAYLEIGH_COEFFICIENT = 0.61

    # ── Electromagnetic ──
    # Visible light center wavelength (μm)
    VISIBLE_WAVELENGTH_UM = 0.55

    # ── Human Vision Reference ──
    # Standard viewing distance for photographic CoC calculations (mm)
    STANDARD_VIEWING_DISTANCE_MM = 250.0

    # Human eye angular resolution (arcminutes)
    HUMAN_EYE_RESOLUTION_ARCMIN = 1.0

    # ── Photography: Circle of Confusion (μm) ──
    # Based on standard viewing distance and human eye resolution.
    COC_FULL_FRAME_UM = 30.0
    COC_APSC_UM = 19.0
    COC_M43_UM = 15.0

    # ── Photography: Format circle diameters (mm) ──
    # Image circle required to fully cover each sensor format without vignetting.
    FORMAT_CIRCLE_FF_MM = 43.3
    FORMAT_CIRCLE_APSC_MM = 28.3
    FORMAT_CIRCLE_M43_MM = 21.6

    # ── Microscopy ──
    # Standard 10× eyepiece magnification for stereo microscopes
    STEREO_EYEPIECE_MAG = 10.0

    # ── Infrared ──
    # NETD baseline for scoring (mK). Higher NETD = worse performance.
    NETD_BASELINE_MK = 200.0
