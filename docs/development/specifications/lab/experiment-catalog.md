# Optics Lab Experiment Catalog

This document maps every planned experiment to the corresponding vault notes and learning chapters. The ordering is **dependency-driven**, not value-driven: each experiment only assumes concepts and experiments that appear before it. Every entry includes the exact physical model and accuracy notes so that implementations can be verified against first principles.

> Last synced with `engine/lensfit/lab/`.
>
> 注：本文档中的 `10-concepts/`、`20-formulas/`、`50-learning/` 等链接路径是原 `OpticKnowledgeSpace/` vault 的相对路径。该 vault 已在 v4.0 知识库重构中删除，由仓库顶层的 `modules/`（10-foundations ~ 50-optical-design）取代；这些路径目前仍作为 lab registry 中 `linked_concepts` 的标识符使用，待后续重新映射到 `modules/` 结构。

---

## Legend

- **ID**: stable experiment identifier used in the registry and URLs.
- **Difficulty**: `foundation` / `intermediate` / `advanced`.
- **Prerequisites**: experiment IDs that should be run first.
- **Linked concepts / formulas**: vault note paths (without `.md`) that the experiment illustrates.
- **Linked learning chapters**: `50-learning/` chapters where the concept is introduced or used heavily.
- **Physical model**: the equations / approximations used. All experiments must include these in code comments.
- **Accuracy notes**: known limitations, idealizations, and caveats.

---

## Phase 1 — Foundations (already implemented)

### 1. `thin-lens` — 薄透镜成像实验
- **Difficulty**: foundation
- **Prerequisites**: none
- **Linked concepts**: `10-concepts/focal-length`, `10-concepts/焦距`
- **Linked formulas**: `20-formulas/thin-lens-gauss`
- **Linked chapters**: `50-learning/02-geometric-optics`
- **Physical model**:
  - Gaussian thin-lens equation: `1/f = 1/u + 1/v`
  - Lateral magnification: `M = -v/u`
- **Accuracy notes**:
  - Thin-lens approximation: ignores lens thickness and principal-plane separation.
  - Paraxial rays only; real lenses have aberrations outside the paraxial region.
  - Object is treated as a vertical arrow on the optical axis.

### 2. `sensor-coverage` — 像圈与传感器覆盖实验
- **Difficulty**: foundation
- **Prerequisites**: none
- **Linked concepts**: `10-concepts/image-circle`, `10-concepts/vignetting`, `10-concepts/渐晕`
- **Linked formulas**: `20-formulas/coverage-ratio`
- **Linked chapters**: `50-learning/05-matching-basics`
- **Physical model**:
  - Image circle is modeled as a circle of diameter `D_ic` centered on the sensor.
  - Coverage ratio is `(D_ic / D_sensor_diag)^2` clamped to 1.0.
  - Vignetting regions are approximated as triangles at the four corners when the corner distance exceeds the circle radius.
- **Accuracy notes**:
  - Real vignetting is gradual (cos⁴, mechanical shading, chief-ray angle effects), not a hard cutoff.
  - The safe-zone rectangle is a simplified rule-of-thumb, not a ray-traced result.

### 3. `color-mixing` — 光谱混色实验
- **Difficulty**: foundation
- **Prerequisites**: none
- **Linked concepts**: `10-concepts/spectral-power-distribution`, `10-concepts/color-temperature`, `10-concepts/chromaticity-diagram`, `10-concepts/色温`
- **Linked formulas**: `20-formulas/planck-blackbody`
- **Linked chapters**: `50-learning/01-light-and-waves`, `50-learning/16-spectroscopy`
- **Physical model**:
  - Two Gaussian spectra centered at `λ_A`, `λ_B` with amplitudes `I_A`, `I_B`.
  - Mixed RGB is a weighted sum of approximate per-wavelength RGB values.
- **Accuracy notes**:
  - The wavelength→RGB mapping is a coarse heuristic, not a CIE color-matching function.
  - Metamerism is mentioned but not computed; the experiment is for intuition only.

### 4. `diffraction` — 圆孔衍射与艾里斑
- **Difficulty**: intermediate
- **Prerequisites**: `thin-lens` (helps understand focal plane)
- **Linked concepts**: `10-concepts/airy-disk`, `10-concepts/艾里斑`, `10-concepts/衍射极限`
- **Linked formulas**: `20-formulas/rayleigh-criterion`, `20-formulas/airy-disk-diameter`
- **Linked chapters**: `50-learning/01-light-and-waves`, `50-learning/10-physical-optics-advanced`
- **Physical model**:
  - Airy disk first dark ring radius: `r = 1.22 λ F#` in the image plane.
  - `F# = f / D`.
- **Accuracy notes**:
  - Assumes a circular unobstructed aperture and monochromatic light.
  - The SVG intensity pattern is a cosine-squared approximation of `(2 J₁(x)/x)²`, accurate enough for visual intuition but not for scientific PSF analysis.

---

## Phase 2 — Geometric Optics & Matching

### 5. `angle-of-view` — 视角与传感器尺寸实验
- **Difficulty**: foundation
- **Prerequisites**: `thin-lens`
- **Linked concepts**: `10-concepts/focal-length`, `10-concepts/焦距`
- **Linked formulas**: `20-formulas/angle-of-view`
- **Linked chapters**: `50-learning/02-geometric-optics`, `50-learning/03-lens-parameters`
- **Physical model**:
  - `AFOV = 2 arctan(sensor_size / (2 f))`.
  - Sensor formats selectable from `lensfit.core.sensor` table.
- **Accuracy notes**:
  - Diagonal, horizontal, and vertical FOV computed separately.
  - Assumes a pinhole/thin-lens model; real lens distortion changes edges.

### 6. `magnification-scale` — 放大倍率与像素精度实验
- **Difficulty**: foundation
- **Prerequisites**: `thin-lens`, `angle-of-view`
- **Linked concepts**: `10-concepts/像素精度`, `10-concepts/工作距离`
- **Linked formulas**: `20-formulas/lateral-magnification`, `20-formulas/pixel-precision`, `20-formulas/focal-length-from-wd`
- **Linked chapters**: `50-learning/02-geometric-optics`, `50-learning/05-matching-basics`
- **Physical model**:
  - `β = f / (WD - f)` (lateral magnification).
  - Pixel precision = pixel_size_um / |β|.
  - Object feature size projected onto sensor = feature_size × |β|.
- **Accuracy notes**:
  - Assumes a simple thin lens at finite conjugates.
  - Does not account for distortion or sensor fill factor.

### 7. `depth-of-field` — 景深实验
- **Difficulty**: foundation
- **Prerequisites**: `thin-lens`, `magnification-scale`
- **Linked concepts**: `10-concepts/depth-of-field`, `10-concepts/f-number`
- **Linked formulas**: `20-formulas/depth-of-field`, `20-formulas/hyperfocal-distance`
- **Linked chapters**: `50-learning/03-lens-parameters`
- **Physical model**:
  - Circle of confusion: `c = max(sensor_diag / 1730, 2 * pixel_size_um / 1000)`.
  - Hyperfocal: `H = f² / (N c) + f`.
  - Near/far limits: `near = H s / (H + s)`, `far = H s / (H - s)` for `s < H`.
- **Accuracy notes**:
  - Uses a standard full-frame CoC divisor; real acceptable blur depends on display size/viewing distance.
  - Pixel-limited CoC is a conservative digital criterion.
  - SVG draws DOF as a band around the focus plane; blur circle size is not rendered to scale.

---

## Phase 3 — Sensors & Sampling

### 8. `nyquist-sampling` — 奈奎斯特采样与混叠实验
- **Difficulty**: intermediate
- **Prerequisites**: `diffraction`, `magnification-scale`
- **Linked concepts**: `10-concepts/nyquist-frequency`, `10-concepts/奈奎斯特频率`, `10-concepts/混叠`
- **Linked formulas**: `20-formulas/nyquist-frequency`, `20-formulas/oversampling-ratio`
- **Linked chapters**: `50-learning/04-sensors`, `50-learning/12-otf-and-image-quality`
- **Physical model**:
  - Sensor Nyquist frequency: `f_N = 1 / (2 * pixel_size_um / 1000)` in lp/mm.
  - Lens MTF approximated as Gaussian with given MTF50.
  - Oversampling ratio = lens MTF50 / sensor Nyquist.
- **Accuracy notes**:
  - MTF model is synthetic; real lenses have complex MTF depending on field and color.
  - Aliasing only occurs when sampling a band-limited signal above Nyquist; the experiment signals "aliasing risk" when lens resolution exceeds sensor Nyquist.

---

## Phase 4 — Physical Optics

### 9. `snell-refraction` — 斯涅尔定律与全反射实验
- **Difficulty**: foundation
- **Prerequisites**: `thin-lens`
- **Linked concepts**: `10-concepts/refractive-index`, `10-concepts/dispersion`, `10-concepts/色散`
- **Linked formulas**: Snell's law `n₁ sin θ₁ = n₂ sin θ₂`
- **Linked chapters**: `50-learning/01-light-and-waves`
- **Physical model**:
  - Incident ray from medium 1 to medium 2.
  - Refraction angle from Snell's law; critical angle `θ_c = arcsin(n₂/n₁)` for `n₁ > n₂`.
  - Fresnel reflection amplitude (optional): `R_s` and `R_p` simplified.
- **Accuracy notes**:
  - Planar interface.
  - Dispersion not modeled by default; optional wavelength slider uses Cauchy/Sellmeier approximation.

### 10. `chromatic-aberration` — 色差实验
- **Difficulty**: intermediate
- **Prerequisites**: `thin-lens`, `snell-refraction`
- **Linked concepts**: `10-concepts/chromatic-aberration`, `10-concepts/abbe-number`, `10-concepts/色散`
- **Linked formulas**: Longitudinal chromatic aberration proportional to `f / V` (Abbe number).
- **Linked chapters**: `50-learning/06-aberrations`
- **Physical model**:
  - Focal length shift for wavelength λ approximated from Abbe number `V_d`.
  - Three chief rays (R/G/B) traced to show focal-plane separation.
- **Accuracy notes**:
  - Simplified linear model; real glass partial dispersions are nonlinear.
  - Does not model transverse chromatic aberration.

---

## Phase 5 — Wave & Interference

### 11. `polarization-malus` — 偏振与马吕斯定律实验
- **Difficulty**: foundation
- **Prerequisites**: `thin-lens`
- **Linked concepts**: polarization (introduced in Ch. 10)
- **Linked formulas**: Malus's law `I = I₀ cos² θ`
- **Linked chapters**: `50-learning/10-physical-optics-advanced`
- **Physical model**:
  - Unpolarized light passes polarizer 1 (intensity halved), then polarizer 2 at angle θ.
  - Output intensity follows Malus's law.
- **Accuracy notes**:
  - Ideal polarizers; no absorption/dichroic losses.
  - Only linear polarization.

### 12. `single-slit-diffraction` — 单缝衍射实验
- **Difficulty**: intermediate
- **Prerequisites**: `diffraction`
- **Linked concepts**: `10-concepts/衍射极限`
- **Linked formulas**: Fraunhofer single-slit intensity `I(θ) ∝ sinc²(π a sin θ / λ)`
- **Linked chapters**: `50-learning/10-physical-optics-advanced`
- **Physical model**:
  - Far-field (Fraunhofer) single-slit pattern.
  - First minima at `sin θ = λ / a`.
- **Accuracy notes**:
  - Assumes infinite slit length and uniform plane-wave illumination.
  - Near-field (Fresnel) effects not included.

### 13. `double-slit` — 双缝干涉实验
- **Difficulty**: intermediate
- **Prerequisites**: `single-slit-diffraction`, `polarization-malus`
- **Linked concepts**: interference (Ch. 10)
- **Linked formulas**: Fringe spacing `Δy = λ L / d`
- **Linked chapters**: `50-learning/10-physical-optics-advanced`
- **Physical model**:
  - Two coherent point sources / infinitely narrow slits.
  - Intensity `I(θ) ∝ cos²(π d sin θ / λ)`.
  - Optional envelope from finite slit width (`single-slit-diffraction` result).
- **Accuracy notes**:
  - Requires mutual coherence; partial coherence broadens fringes.
  - Slit width envelope optional but recommended.

### 14. `grating` — 光栅方程与光谱级次实验
- **Difficulty**: intermediate
- **Prerequisites**: `double-slit`, `color-mixing`
- **Linked concepts**: `10-concepts/diffraction-grating`
- **Linked formulas**: `20-formulas/grating-equation`, `20-formulas/grating-resolving-power`
- **Linked chapters**: `50-learning/10-physical-optics-advanced`, `50-learning/16-spectroscopy`
- **Physical model**:
  - Transmission grating: `d (sin θ_i + sin θ_m) = m λ`.
  - Show allowed diffraction orders for a given λ and angle of incidence.
- **Accuracy notes**:
  - Assumes monochromatic plane wave and neglects blaze angle efficiency.
  - Blaze efficiency strongly affects real spectrometer throughput.

---

## Phase 6 — Image Quality & Advanced Imaging

### 15. `mtf-explorer` — MTF/OTF 探索实验
- **Difficulty**: intermediate
- **Prerequisites**: `nyquist-sampling`, `diffraction`
- **Linked concepts**: MTF/OTF/PSF (Ch. 12)
- **Linked formulas**: `20-formulas/airy-disk-diameter`
- **Linked chapters**: `50-learning/12-otf-and-image-quality`
- **Physical model**:
  - Synthesize MTF from MTF50 Gaussian.
  - Add defocus blur and diffraction limit.
  - Compute PSF via inverse cosine transform (or analytical Gaussian).
- **Accuracy notes**:
  - Synthetic MTF is a teaching approximation; real MTF is measured.
  - Defocus model uses geometrical optics CoC, not wave-optical defocus OTF.

### 16. `blackbody` — 黑体辐射与色温实验
- **Difficulty**: intermediate
- **Prerequisites**: `color-mixing`
- **Linked concepts**: `10-concepts/color-temperature`, `10-concepts/色温`
- **Linked formulas**: `20-formulas/planck-blackbody`
- **Linked chapters**: `50-learning/13-illumination-design`, `50-learning/16-spectroscopy`
- **Physical model**:
  - Planck spectral radiance `B_λ(T)`.
  - Wien's displacement law `λ_peak = b / T` with `b ≈ 2.898 × 10⁻³ m·K`.
- **Accuracy notes**:
  - Ideal blackbody; real sources (LED, tungsten, sun) deviate.
  - CIE color temperature requires chromaticity comparison, not just peak.

---

## Phase 7 — Domain-Specific Labs

### 17. `illumination-geometry` — 照明方式几何实验
- **Difficulty**: intermediate
- **Prerequisites**: `snell-refraction`
- **Linked concepts**: illumination types (Ch. 13)
- **Linked formulas**: Snell's law, Fresnel reflectance
- **Linked chapters**: `50-learning/13-illumination-design`
- **Physical model**:
  - Switch between bright-field, dark-field, coaxial, diffuse-back, low-angle.
  - For each mode, draw incident rays and highlight which surface features (specular, diffuse, scratches) become visible.
- **Accuracy notes**:
  - 2-D ray cartoon; real illumination has 3-D light cones and scattering lobes.
  - Surface BRDF not modeled quantitatively.

### 18. `thermal-ifov-netd` — 热成像 IFOV 与 NETD 实验
- **Difficulty**: advanced
- **Prerequisites**: `magnification-scale`, `angle-of-view`
- **Linked concepts**: `10-concepts/NETD`, `10-concepts/微测辐射热计`
- **Linked formulas**: `IFOV = pixel_size_um / f`, projected spot size, NETD scaling
- **Linked chapters**: `50-learning/08-domain-applications` (infrared)
- **Physical model**:
  - `IFOV_rad = pixel_pitch / f`.
  - Projected spot size at distance `D`: `spot = IFOV × D`.
  - NETD shown as system sensitivity (input parameter), with note that measured NETD depends on F# and integration time.
- **Accuracy notes**:
  - Pixel pitch is the active photosite pitch; real fill factor affects signal.
  - NETD is a system-level figure, not solely determined by pixel pitch.

### 19. `aberration-spot` — 透镜像差点列图实验
- **Difficulty**: advanced
- **Prerequisites**: `thin-lens`, `chromatic-aberration`, `mtf-explorer`
- **Linked concepts**: `50-learning/06-aberrations`, `50-learning/11-optical-design-basics`
- **Linked formulas**: Seidel aberration wavefront polynomials (simplified)
- **Linked chapters**: `50-learning/06-aberrations`, `50-learning/11-optical-design-basics`
- **Physical model**:
  - Generate a pupil grid and compute transverse ray aberrations from low-order Seidel terms (spherical, coma, astigmatism, field curvature, distortion).
  - Draw spot diagram and approximate PSF.
- **Accuracy notes**:
  - Simplified Seidel model; real lens design uses ray tracing with exact surfaces.
  - Interaction between aberration orders and color not modeled.

---

## Implementation Order Summary

```text
Phase 1 (done)
  1. thin-lens
  2. sensor-coverage
  3. color-mixing
  4. diffraction

Phase 2
  5. angle-of-view
  6. magnification-scale
  7. depth-of-field

Phase 3
  8. nyquist-sampling

Phase 4
  9. snell-refraction
  10. chromatic-aberration

Phase 5
  11. polarization-malus
  12. single-slit-diffraction
  13. double-slit
  14. grating

Phase 6 (done)
  15. mtf-explorer
  16. blackbody

Phase 7 (done)
  17. illumination-geometry
  18. thermal-ifov-netd
  19. aberration-spot
```

---

## How to Add a New Entry

1. Pick the smallest dependency group it belongs to.
2. Write the physical model and accuracy notes before writing code.
3. Add the experiment module under `engine/lensfit/lab/experiments/`.
4. Run `python scripts/sync_experiment_links.py` to update this catalog and vault notes.
5. Add a focused test in `engine/tests/test_lab.py` verifying both the numeric result and SVG output.
