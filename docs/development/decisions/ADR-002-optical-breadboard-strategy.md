# ADR-002: Optical Breadboard / Digital-Twin Strategy

**Status:** Proposed
**Date:** 2026-06-12
**Author:** LensFit architecture team
**Scope:** Decide the architectural direction for evolving the "Self-Study Optics Lab" into an equipment-based optical breadboard (digital twin), while keeping implementation details in follow-up plans.

## 1. Context

The user envisions LensFit as a **digital twin of a physical optics laboratory**:

1. An equipment library (lasers, lenses, apertures, gratings, mounts, detectors, etc.).
2. A 2D optical breadboard/table where users drag real-looking components and connect them into light paths.
3. Basic experiments such as the **single-slit diffraction intensity distribution** should be runnable on that breadboard.

This is a large, multi-phase effort. Before building, we need to decide whether to:

- **Integrate** an existing open-source geometric-optics engine (most mature candidate: `ricktu288/ray-optics`).
- **Self-build** a ray-tracing / wave-optics solver in Python.
- Use a **hybrid** approach: reuse `ray-optics` for the geometric breadboard, and keep LensFit's native Python experiments for wave/diffraction physics.

This document compares candidate engine strategies and defines the system boundaries that future implementation plans must respect.

## 1.1 Positioning

This ADR is an **architecture decision record**, not a full implementation plan.

It decides:

- LensFit should use a hybrid simulation architecture.
- A third-party geometric optics engine may be used behind an adapter boundary.
- Wave/interference/diffraction observables remain LensFit-native unless a dedicated wave-optics engine is adopted later through another ADR.
- The LensFit `SceneGraph` is the stable domain model. Third-party scene formats are adapter details.

It does not decide:

- The final breadboard UI framework.
- The long-term persistence schema for saved scenes.
- Whether third-party engine artifacts are vendored into git or downloaded during builds.
- The full catalog of physical equipment.
- Any future 3D/VR implementation.

## 2. Landscape Scan

### 2.1 Mature open-source candidate: Ray Optics Simulation

| Attribute | Detail |
|---|---|
| **Project** | [ricktu288/ray-optics](https://github.com/ricktu288/ray-optics) |
| **License** | Apache-2.0 (permissive, compatible with LensFit's MPL/Apache stack) |
| **What it does** | 2D geometric ray tracing with reflection, refraction, lenses, mirrors, beam splitters, gratings, GRIN media, ideal lens/mirror, detectors, irradiance maps, color/wavelength. |
| **Distribution forms** | Web app (`phydemo.app/ray-optics/simulator/`), gallery, **Node module** (`dist-node/rayOptics.js`), **CLI runner** (`dist-integrations/runner.js`). |
| **Runtime API** | `Scene`, `Simulator`, `sceneObjs`, `geometry`. Scenes are JSON-serializable and versioned. |
| **Headless output** | Detector readings (power, normal/shear momentum flow, 1-D irradiance map) and PNG/SVG images of crop boxes. |
| **Integration tools** | Pre-built `dist-integrations` zip with `runner.js` + examples for Python/Julia. Reads a scene JSON from stdin and writes results JSON to stdout. |
| **Maintenance** | Active (2024–2026), large gallery, Weblate translations, automatic scene-based tests, citeable Zenodo releases. |

**Why it is attractive**

- It already solves 90% of the geometric-breadboard simulation problem.
- It exposes a clean JSON scene format and a Node CLI, so the LensFit Python backend can treat it as a sidecar process.
- Apache-2.0 means we can ship it with the desktop app as long as we preserve attribution and license notices.

**Where it does not fit**

- It is a **geometric ray tracer**, not a wave solver. A single slit in ray-optics will cast a geometric shadow; it will **not** produce the Fraunhofer intensity distribution.
- It has no concept of an "equipment catalog" with manufacturer specs, part numbers, or measurement error.
- Its UI is English-first; although translation files exist, the visual editor is not designed to be embedded wholesale into another application.
- It is 2D only (sufficient for the envisioned breadboard, but not a full 3D lab).

### 2.2 Broader open-source / academic scan

| Project | Type | License / Availability | Verdict |
|---|---|---|---|
| **Ray Optics Simulation** (`ricktu288/ray-optics`) | Browser-first 2D geometric optics simulator with Node integration tools | Apache-2.0 | Best fit for an MVP 2D teaching breadboard because it already has interactive scenes, detector output, SVG export, integration tools, and scene tests. |
| **Open Optics Module** | Open-source 2D geometrical optics teaching software from Lund University | Open source, GitLab linked from project site | Good reference for educational 2D scope and UI concepts; integration surface appears less direct than ray-optics. |
| **OpticsWorkbench** (`chbergmann/OpticsWorkbench`) | FreeCAD workbench for ray tracing through FreeCAD objects | GitHub project | Useful reference for optomechanical/CAD workflows and grating orders; too FreeCAD-centric for LensFit's desktop teaching UI. |
| **RayOptics** (`mjhoptics/ray-optics`) | Python optical system design and image-forming optics library | Open source | Strong candidate for future lens-design analysis; not a drag-and-drop 2D teaching breadboard engine. |
| **pyOpTools** | Python optical system simulation, mainly ray tracing with emerging field propagation tools | Open source docs | Good future reference for Python-native optical systems; heavier and less UI-oriented than the MVP needs. |
| **raytracing** PyPI package | Python ABCD matrix / paraxial optics package | Open source | Valuable for simple analytic validation and teaching examples; insufficient for arbitrary non-sequential breadboard scenes. |
| **Raysect** | Python geometrical optical simulation framework | Open source | Research-grade, physically robust ray tracing; likely too heavy for near-term interactive educational breadboard use. |
| **KrakenOS** | Python exact ray tracing with 2D/3D visualization | Open source GitHub project | Useful comparison point for Python 3D optical systems; higher integration and UX cost for the current app. |
| **TorchOptics** | PyTorch-based differentiable Fourier optics | Open source / academic | Useful future candidate for advanced wave optics, diffraction, holography, and GPU workflows; too much for MVP analytic diffraction. |
| **Poke** | Ray-based physical optics platform connecting ray data to diffraction/polarization models | Open source / academic | Architecturally relevant because it validates separating ray-trace data from physical-optics computation; not a direct teaching breadboard engine. |
| **Optics Bench JS** (Physlet) | Legacy Java-to-JS geometric optics bench | Educational code, older architecture | Reference only; not a modern integration foundation. |
| **RWTH Aachen Virtual Optical Bench** | VR/3D lab prototype | Research project, not obviously open source | Useful inspiration for long-term 3D/VR direction, not current code reuse. |
| **PraxiLabs, 3DOptix, VirtualLab Fusion, 北京欧倍尔** | Commercial virtual labs | Proprietary / paid | Competitor/reference landscape only; out of scope for an open-source-first LensFit core. |

**Conclusion:** `ray-optics` is not the only optics-related open-source project, but it is currently the best-fit candidate for a **2D interactive educational breadboard**. Python libraries are stronger references for optical design, validation, or future physical-optics modules. The architecture should therefore keep the LensFit domain model independent from any one engine.

## 3. Comparison Matrix

| Dimension | A. Embed ray-optics web app (iframe) | B. Use ray-optics Node sidecar | C. Self-build Python ray tracer | D. Hybrid (recommended) |
|---|---|---|---|---|
| **Functional coverage** | Full web-app feature set, but hard to skin/control. | Geometric simulation + detector/PNG output only. | Whatever we implement; high long-term cost. | Geometric via sidecar + wave/diffraction native. |
| **Breadboard UX ownership** | Low — we show someone else's UI. | High — we draw components ourselves. | High. | High. |
| **Wave optics (single-slit, double-slit, Airy)** | Not supported by the engine. | Not supported by the engine. | We implement directly. | Native Python wave solvers, ray-optics draws the geometric layout. |
| **Performance** | Browser runs it; iframe overhead. | Spawning Node per request adds ~50–200 ms; long-lived sidecar fixes this. | Fast once built; huge upfront cost. | Fast geometric batch via sidecar; fast analytic wave in Python. |
| **Integration effort** | Days (iframe), but brittle. | Weeks (sidecar wrapper, JSON mapping, error handling). | Months to years. | Months, but incremental. |
| **License / distribution** | Apache-2.0, attribution required. | Apache-2.0, ship `dist-integrations` files. | Fully ours. | Same as B, plus our own code. |
| **Maintainability** | Tied to upstream UI changes. | Tied to upstream JSON format; bounded surface. | Full burden on LensFit team. | Bounded + domain-specific value. |
| **Equipment catalog integration** | None. | Easy: catalog generates JSON scenes. | We build everything. | Catalog generates scene graph for both solvers. |
| **Chinese localization** | Partial (community translations). | Full — our UI wraps it. | Full. | Full. |

## 4. Decision

**Adopt option D: a hybrid architecture with a `ray-optics` Node sidecar for geometric breadboard simulation and LensFit-native Python solvers for wave/interference/diffraction experiments.**

### 4.1 Rationale

- We should **not** rebuild a geometric ray tracer when a high-quality, Apache-2.0 engine already exists.
- We **must not** force wave-optics experiments into a geometric engine where they are physically incorrect.
- The existing `lensfit.lab` experiment runtime already returns `(data, svg, warnings)`; this maps naturally to a multi-solver dispatcher.
- A sidecar keeps the optics engine out of the critical Python/FastAPI process, reducing coupling and allowing independent updates.

### 4.2 Decision boundary

This decision commits LensFit to a **hybrid solver boundary**, not to embedding the upstream `ray-optics` UI or leaking its JSON schema into the product model.

The dependency direction is:

```text
LensFit SceneGraph -> solver adapters -> third-party/native engines
```

The reverse dependency is forbidden:

```text
ray-optics scene JSON -> LensFit domain model
```

If `ray-optics` is replaced later, saved LensFit scenes and frontend payloads should remain valid after only adapter-level changes.

## 5. Proposed Architecture

### 5.1 High-level flow

```text
┌─────────────────────────────────────────────────────────────┐
│                     apps/desktop (React/Vite)                │
│  BreadboardCanvas ──► ComponentPalette ──► ParameterPanel    │
└───────────────────────┬─────────────────────────────────────┘
                        │ scene graph JSON
┌───────────────────────▼─────────────────────────────────────┐
│              engine/lensfit/lab/workbench.py                 │
│  OpticalWorkbench ──► SolverDispatcher                       │
│     ├─► RayOpticsSidecar  (geometric rays, detectors, PNG)  │
│     └─► WaveSolver        (Fraunhofer, Fresnel, phasors)    │
└───────────────────────┬─────────────────────────────────────┘
                        │ {data, svg, warnings}
┌───────────────────────▼─────────────────────────────────────┐
│              FastAPI /api/v1/lab/workbench/run               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 New backend modules

```text
engine/lensfit/lab/
  base.py                 # existing OpticsExperiment / Parameter / Result
  registry.py             # existing auto-discovery
  renderer.py             # existing SVG primitives
  workbench/              # NEW
    __init__.py
    equipment.py          # EquipmentSpec: laser, lens, slit, grating, screen, detector
    scene.py              # SceneGraph, Component, Port, Transform
    solver.py             # SolverDispatcher
    ray_optics_sidecar.py # Wrapper around runner.js
    wave_solver.py        # Native Fraunhofer/Fresnel diffraction solvers
    composer.py           # Combine ray-optics PNG + Python SVG overlays
```

### 5.3 Domain model rules

`SceneGraph` is the stable LensFit workbench model and must remain solver-neutral.

Required invariants:

- All distances use millimeters unless a field explicitly says otherwise.
- Angles use degrees in UI payloads and radians only inside numerical solvers.
- Coordinates are 2D breadboard coordinates, not screen pixels.
- `SceneGraph.version` is required and migration-tested.
- Components reference LensFit `EquipmentSpec` records by stable `spec_id`.
- Solver-specific object types are kept in adapter mapping tables, not in saved scenes.
- Scene validation runs before any solver adapter is invoked.

### 5.4 Component catalog data model (minimal)

```python
@dataclass
class EquipmentSpec:
    id: str                      # e.g. "hene-laser-632.8"
    category: Literal["source", "lens", "mirror", "aperture", "grating", "screen", "detector", "mount"]
    name: str
    manufacturer: str | None
    parameters: list[Parameter]  # focal length, diameter, wavelength, slit width, etc.
    ports: list[Port]            # input/output beam attachment points
    icon_svg: str | None
```

Solver-specific mappings live outside the equipment record:

```python
@dataclass
class SolverMapping:
    spec_id: str
    solver: Literal["ray_optics", "wave"]
    model: str
    parameter_map: dict[str, str]
```

The catalog may reference the existing `lensfit.db.catalog` data where useful, but optics-lab teaching equipment should remain a separate domain. This avoids expanding the production lens/sensor catalog around breadboard-only concerns.

### 5.5 Scene graph → ray-optics JSON mapping

A `SceneGraph` is a list of placed `Component` instances. Each component carries:

- `spec_id` — reference to `EquipmentSpec`.
- `transform` — 2D position and rotation on the breadboard.
- `param_overrides` — user-tuned values.
- `connections` — which output port feeds which input port.

The `RayOpticsSidecar` translates this into a `ray-optics` scene JSON:

```json
{
  "version": 5,
  "objs": [
    {"type": "SingleRay", "p1": {"x": 0, "y": 0}, "p2": {"x": 50, "y": 0}, "wavelength": 632.8},
    {"type": "SphericalLens", "p1": {"x": 100, "y": -20}, "p2": {"x": 100, "y": 20},
     "params": {"d": 10, "r1": 50, "r2": -50}, "refIndex": 1.5},
    {"type": "Detector", "p1": {"x": 200, "y": -30}, "p2": {"x": 200, "y": 30}, "irradMap": true, "binSize": 2}
  ]
}
```

The sidecar invokes `node runner.js`, captures `detectors[]` / `images[]`, and returns them to the dispatcher.

### 5.6 Wave-optics path

For experiments such as single-slit diffraction:

1. The user places laser → single-slit aperture → screen on the breadboard.
2. The geometric part (layout, ray envelope) is rendered by `ray-optics`.
3. The `WaveSolver` computes the analytic Fraunhofer intensity `I(y) = (sin β / β)²` from the slit width, wavelength, and screen distance.
4. `composer.py` overlays the intensity curve onto the geometric SVG/PNG as a second layer.

This preserves physical correctness while giving the user a coherent breadboard view.

### 5.7 SolverDispatcher behavior

```python
class SolverDispatcher:
    def run(self, scene: SceneGraph, observables: list[Observable]) -> ExperimentResult:
        plan = self.plan(scene, observables)
        if plan.requires("ray_optics") and plan.requires("wave"):
            geo = self.ray_optics.render(scene)
            wave = self.wave_solver.compute(scene, observables)
            return self.composer.compose(geo, wave)
        if plan.requires("wave"):
            return self.wave_solver.compute(scene, observables)
        return self.ray_optics.render(scene)
```

Solver selection is based on requested observables, not only on component types. Example observable families:

- `ray_paths`
- `detector_power`
- `irradiance_map`
- `fraunhofer_intensity`
- `fresnel_field`
- `polarization_state`

This keeps the dispatcher explicit as the physics surface grows.

## 6. Integration Details for `ray-optics`

### 6.1 Sidecar packaging

- Phase 1 should fetch or cache a pinned `ray-optics` release for contract tests. Vendoring `dist-integrations` into git is a separate packaging decision.
- Add `node` to the desktop build prerequisites (Electron already includes Node; for the dev server, developers need Node ≥ 18).
- `rayOptics.js` + `runner.js` are invoked as a subprocess from Python.

### 6.2 Runtime contract

```python
class RayOpticsSidecar:
    async def simulate(self, scene_json: dict) -> dict:
        proc = await asyncio.create_subprocess_exec(
            "node", self.runner_path,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(json.dumps(scene_json).encode())
        return json.loads(stdout)
```

For production, consider keeping a **long-lived sidecar process** with a JSON-RPC loop to avoid per-request Node startup cost.

The production wrapper must add:

- Fixed `ray-optics` version and scene schema checks.
- Request timeout and subprocess cleanup.
- Non-zero exit handling with normalized LensFit error codes.
- JSON schema validation for stdin and stdout.
- Bounded stdout/stderr size.
- A concurrency policy: single-flight queue for MVP, worker pool only after measurement.
- No arbitrary filesystem paths in scene payloads.

### 6.3 What we get from `ray-optics`

- **Sources:** `SingleRay`, `Beam`/`ParallelBeam`, `PointSource`.
- **Optics:** `SphericalLens`, `IdealLens`, `Mirror` (plane/curve/parabolic), `BeamSplitter`, `Blocker`, `DiffractionGrating`, `Glass` shapes.
- **Sensing:** `Detector` with irradiance map, `CropBox` for PNG export.
- **Utilities:** grid, rulers, protractor, text labels.

### 6.4 Limitations we must paper over

| Limitation | Mitigation |
|---|---|
| No true wave diffraction | Use native Python wave solver for intensity plots. |
| No measurement uncertainty | Add post-processing noise/error model in `WaveSolver`/`composer`. |
| No equipment metadata | Keep metadata in LensFit `EquipmentSpec`; ray-optics only sees geometry. |
| 2D only | Document as intentional for the MVP breadboard. |
| Requires `node-canvas` for PNG output | Ship it with the sidecar; fallback to SVG-only mode if native deps fail. |

## 7. Roadmap

### Phase 0 — Architecture probe (3–5 days)

- [ ] Pin a candidate `ray-optics` release and run one minimal scene through its Node integration.
- [ ] Capture detector data and SVG/PNG output in a contract-test fixture.
- [ ] Verify Windows, Linux, and macOS execution assumptions.
- [ ] Record license files and attribution requirements.
- [ ] Decide whether Phase 1 may vendor artifacts or should download/cache them in build scripts.

### Phase 1 — Workbench domain slice (1–2 weeks)

- [ ] Define `SceneGraph v1`, `Component`, `Port`, `Transform`, `Observable`, and validation schemas.
- [ ] Define `EquipmentSpec` for a minimal in-memory teaching catalog. Avoid Alembic until persistence is required.
- [ ] Define solver mapping tables outside `EquipmentSpec`.
- [ ] Add `POST /api/v1/lab/workbench/run` for stateless SceneGraph simulation.
- [ ] Add tests for versioning, validation, and adapter isolation.

### Phase 2 — Sidecar adapter MVP (1–2 weeks)

- [ ] Implement `RayOpticsSidecar` with timeout, error handling, schema validation, and bounded output.
- [ ] Translate a small LensFit scene to `ray-optics` JSON through adapter code.
- [ ] Return detector readings and a render artifact through a LensFit result schema.
- [ ] Keep `/api/v1/lab/experiments/{id}/run` unchanged for existing parameterized experiments.

### Phase 3 — Minimal breadboard UI (2–3 weeks)

- [ ] Add `BreadboardPage` in `apps/desktop`.
- [ ] Implement component palette, 2D placement, property inspector, and stateless run.
- [ ] Serialize canvas state to LensFit `SceneGraph v1` and POST to `/api/v1/lab/workbench/run`.
- [ ] Display returned composite SVG/PNG.

### Phase 4 — Single-slit diffraction on breadboard (1–2 weeks)

- [ ] Implement `Observable.fraunhofer_intensity`.
- [ ] Implement `WaveSolver.single_slit_fraunhofer()`.
- [ ] Add a `single-slit-breadboard` preset that generates a SceneGraph.
- [ ] Overlay analytic intensity on the geometric layout with clear layer labels.
- [ ] Add learning hints linking to `OpticKnowledgeSpace` notes and formulas.

### Phase 5 — Persistence and catalog scale

- [ ] Add save/load only after `SceneGraph v1` stabilizes through MVP usage.
- [ ] Introduce database persistence and Alembic migrations if saved scenes or user catalogs are required.
- [ ] Seed catalog:
  - HeNe laser 632.8 nm
  - Diode laser 532 nm / 650 nm
  - Planoconvex / biconvex lenses (various focal lengths)
  - Single-slit aperture, double-slit aperture, diffraction grating
  - Plane mirror, beam splitter
  - Screen, photodiode / CCD detector
- [ ] Add API `GET /api/v1/lab/catalog` and `GET /api/v1/lab/catalog/{id}`.

### Later — Polish / scale

- [ ] Long-lived sidecar process after measured spawn overhead justifies it.
- [ ] Undo/redo, share via JSON, and guided experiments.
- [ ] Evaluate Python-native engines for advanced optical design workflows.
- [ ] Evaluate Fourier/physical-optics libraries for advanced wave modules.
- [ ] 3D preview or CAD integration only through a separate ADR.

## 8. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| `node-canvas` native dependency fails on some platforms | High for PNG output | Provide SVG-only fallback; pre-build sidecar binaries in CI. |
| `ray-optics` JSON format changes between versions | Medium | Pin to a tested release; add version-gate test. |
| Per-request Node spawn is too slow | Medium | Use long-lived sidecar or batch renders. |
| LensFit domain model becomes coupled to ray-optics JSON | High | Keep ray-optics types in adapter mappings only; add tests that saved scenes do not contain third-party object names. |
| Workbench API conflicts with existing experiment API | Medium | Use `/lab/workbench/run` for SceneGraph simulation and keep `/lab/experiments/{id}/run` for parameterized experiments. |
| Users expect real 3D lab / VR | Low for MVP | Keep scope 2D; document roadmap. |
| License attribution missed | Legal | Ship `NOTICE` file and keep `dist-integrations` LICENSE intact. |
| Wave/geometric solvers produce inconsistent visuals | Medium | Clearly label layers: "geometric rays" vs "wave intensity". |

## 9. Open Questions

1. Do we ship `ray-optics` source/binaries in git, or fetch/cache them in build scripts?
2. Should the breadboard canvas be SVG-based (easier to compose with Python renderer) or Canvas-based (better drag UX)?
3. Which physical parameters (e.g. lens diameter, beam waist, detector pixel pitch) are required for the MVP catalog?
4. How do we represent real manufacturer data (Thorlabs, Edmund Optics) without copyright issues?
5. Should advanced wave optics stay analytic for teaching, or adopt a library such as TorchOptics after MVP?
6. Should Python optical-design libraries such as RayOptics or pyOpTools be integrated later for lens-system workflows?

## 10. References

- [ricktu288/ray-optics](https://github.com/ricktu288/ray-optics) — source, gallery, and `dist-integrations`.
- [Ray Optics Documentation](https://phydemo.app/ray-optics/docs/index.html) — `Scene`, `Simulator`, `sceneObjs` API.
- [Ray Optics Integration Tools README](https://github.com/ricktu288/ray-optics/tree/dist-integrations) — `runner.js` and Python example.
- [Open Optics Module](https://openopticsmodule.com/) — open-source 2D geometrical optics teaching software.
- [chbergmann/OpticsWorkbench](https://github.com/chbergmann/OpticsWorkbench) — FreeCAD optics workbench and CAD-oriented ray tracing reference.
- [mjhoptics/ray-optics](https://github.com/mjhoptics/ray-optics) — Python geometric ray tracing and optical system analysis.
- [pyOpTools documentation](https://pyoptools.readthedocs.io/en/latest/notebooks/basic/00-Intro.html) — Python optical system simulation reference.
- [raytracing PyPI package](https://pypi.org/project/raytracing/) — Python ABCD matrix / paraxial optics package.
- [Raysect](https://www.raysect.org/introduction.html) — Python geometrical optical simulation framework.
- [Kraken Optical Simulator](https://github.com/Garchupiter/Kraken-Optical-Simulator) — Python exact ray tracing and 2D/3D visualization reference.
- [TorchOptics paper](https://arxiv.org/abs/2411.18591) — differentiable Fourier optics reference.
- [Poke paper](https://arxiv.org/abs/2309.04649) — ray-based physical optics architecture reference.
- [Optics Bench JS](https://iwant2study.org/lookangejss/04waves_13light/Java/opticsbench/optics.html) — legacy Physlet reference.
- `docs/development/architecture/optics-lab/self-study-lab-architecture.md` — existing LensFit lab architecture.
