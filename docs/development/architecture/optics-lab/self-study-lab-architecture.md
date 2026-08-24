# Architecture: OptiBench Self-Study Optics Laboratory

> **状态注记（2026-08 更新）**：本文多次引用的 `OpticKnowledgeSpace/` Obsidian vault（含 `10-concepts/`、`90-maps/` 等路径）已在 v4.0 知识库重构中删除，由仓库顶层的 `modules/`（10-foundations ~ 50-optical-design）取代。下文中 vault 相关路径描述的是重构前的设计，概念链接机制待重新映射到 `modules/` 结构；配套的 `scripts/sync_experiment_links.py` 等 vault 维护脚本已随重构删除，下文第 3、6.1、6.2 节中的同步流程描述同样失效；`engine/optibench/lab/` 与 `apps/desktop/src/lab/` 的架构描述仍然有效。

## 1. Vision

OptiBench evolves from a **lens/detector matching assistant** into a **self-study optics laboratory**:

> Every physical concept in the `OpticKnowledgeSpace` vault has a runnable, visual experiment. The learner reads the concept note, opens the linked experiment, changes parameters, and immediately sees the physical consequence.

The existing matching engine, catalog, and project features remain, but they become **application domains** inside a larger learning environment.

## 2. Design Principles

| Principle | Meaning |
|---|---|
| **Vault-driven** | The Markdown vault is the source of truth for *what* concepts exist. Code provides experiments *for* those concepts. |
| **Progressive disclosure** | An experiment starts as sliders + live SVG. Advanced learners can expand formulas, raw data, and warnings. |
| **Reusable physics core** | Experiments build on `optibench.core.*` and `optibench.visualization.*`, not one-off math. |
| **Stateless runtime** | An experiment run is a pure function `params → (data, svg, warnings)`. No DB required for the MVP. |
| **Extensible registry** | Adding a new experiment means adding one Python module and one front-end card; no router or store changes. |
| **Git-clean** | Generated plugin data, workspace state, and experiment run history stay out of version control. |

## 3. Concept-to-Experiment Mapping

```text
OpticKnowledgeSpace/                engine/optibench/lab/                apps/desktop/src/lab/
  10-concepts/focal-length.md  <--  experiments/thin_lens.py  <---->  ExperimentCard / Runner
    ## 关联实验
    - [[90-maps/Optics Lab#thin-lens|薄透镜成像实验]]
```

Each experiment declares:

- `experiment_id` — stable machine identifier (`thin-lens`).
- `title` / `description` — human copy.
- `difficulty` — `foundation`, `intermediate`, `advanced`.
- `linked_concepts` — vault note paths (without `.md`) that the experiment illustrates.
- `prerequisites` — experiment IDs that should be run first (for guided paths).
- `parameters` — typed, validated sliders/inputs.
- `learning_objectives` — what the learner should notice.

A sync script (`scripts/sync_experiment_links.py`) reads the registry and injects a `## 关联实验` section into the matching vault notes, keeping links bidirectional.

## 4. Backend Architecture

### 4.1 Package Layout

```text
engine/optibench/lab/
  __init__.py           # public exports
  base.py               # OpticsExperiment, Parameter, ExperimentResult
  registry.py           # ExperimentRegistry with dynamic discovery
  renderer.py           # reusable SVG primitives (axes, arrows, gradients)
  schemas.py            # Pydantic request/response models for API
  experiments/
    __init__.py
    thin_lens.py        # geometric optics / magnification
    diffraction.py      # Airy disk / Rayleigh criterion
    color_mixing.py     # spectral mixing / RGB preview
    sensor_coverage.py  # image circle vs sensor rectangle
    snell_refraction.py # optional next experiment
    nyquist_sampling.py # optional next experiment
```

### 4.2 Base Class Contract

```python
class OpticsExperiment(ABC):
    experiment_id: str
    title: str
    description: str
    difficulty: str = "foundation"
    linked_concepts: list[str] = []
    prerequisites: list[str] = []
    learning_objectives: list[str] = []
    parameters: list[Parameter] = []

    def info(self) -> ExperimentInfo: ...

    @abstractmethod
    def run(self, params: dict[str, Any]) -> ExperimentResult: ...
```

`Parameter` supports `float`, `int`, `bool`, `choice`. Validation happens in `schemas.py` using the declared bounds.

`ExperimentResult` contains:

- `data`: serializable computed values.
- `svg`: a self-contained SVG string.
- `warnings`: list of caveats (e.g., virtual image, aliasing).
- `learning_hints`: optional callouts tied to `learning_objectives`.

### 4.3 Registry

`ExperimentRegistry` discovers experiments by scanning `optibench/lab/experiments/` for concrete subclasses of `OpticsExperiment`. This avoids the brittle hardcoded import list and broken imports.

```python
registry = ExperimentRegistry()
registry.discover(package=experiments)
```

The registry is a singleton exposed via `get_registry()`.

### 4.4 Reuse of Existing Code

Experiments are thin orchestration layers:

- Geometry → `optibench.core.thin_lens.ThinLensCalculator`
- Coverage → `optibench.visualization.coverage.CoveragePlotData`
- MTF / Nyquist → `optibench.visualization.mtf.MtfPlotData`
- DoF → `optibench.visualization.coc.CocPlotData`
- SVG rendering → new `optibench.lab.renderer` helpers (to avoid matplotlib in the engine sidecar)

### 4.5 API Router

New router: `engine/optibench/api/routers/lab.py`

```text
GET  /api/v1/lab/experiments              -> list experiment metadata
GET  /api/v1/lab/experiments/{id}         -> single experiment metadata
POST /api/v1/lab/experiments/{id}/run     -> {data, svg, warnings, hints}
POST /api/v1/lab/experiments/{id}/sweep   -> param sweep (future)
```

Registered in `optibench/api/server.py` with `app.include_router(lab.router)`.

### 4.6 Testing

- `engine/tests/test_lab.py`: registry discovery, each experiment returns valid result, parameter bounds enforced, SVG is well-formed XML.
- `engine/tests/test_api_lab.py`: router endpoints using the standard `TestClient` fixture pattern.

## 5. Frontend Architecture

### 5.1 New Tab

Add `"lab"` to `TabId` and the `tabs` array in `apps/desktop/src/App.tsx`. Icon: `FlaskConical` from `lucide-react`.

### 5.2 Page Layout

```text
LabPage (two-column)
  ├─ Left: ExperimentCatalog
  │    ├─ Search/filter by concept/difficulty
  │    └─ ExperimentCard list
  └─ Right: ExperimentRunner
       ├─ Header (title, concept links, difficulty badge)
       ├─ ParameterPanel
       │    └─ ParameterControl per parameter
       ├─ VisualizationPanel
       │    └─ inline SVG or Canvas
       └─ DataPanel (collapsible)
            ├─ computed values
            ├─ warnings
            └─ learning hints
```

### 5.3 State

- **Server state**: React Query for experiment catalog and runs.
- **Client state**: Zustand store `labStore` for:
  - `activeExperimentId`
  - `paramDrafts: Record<experimentId, Record<paramName, value>>`
  - `showDataPanel`, `recentExperiments`
- **Persistence**: `paramDrafts` and `recentExperiments` saved to `localStorage`.

### 5.4 API Client

Add to `apps/desktop/src/utils/api.ts`:

```ts
export interface LabExperiment { id; title; description; difficulty; linked_concepts; parameters; }
export interface LabRunResult { data; svg; warnings; learning_hints; }
export async function listLabExperiments(): Promise<{ items: LabExperiment[] }>;
export async function runLabExperiment(id: string, params: Record<string, unknown>): Promise<LabRunResult>;
```

### 5.5 Visualization

Experiments return SVG strings, so the front end renders them with:

```tsx
<div dangerouslySetInnerHTML={{ __html: result.svg }} />
```

For performance, the runner debounces parameter changes (e.g., 150 ms) before calling `/run`.

## 6. Knowledge Base Integration

### 6.1 Sync Script

`scripts/sync_experiment_links.py`:

1. Imports the engine registry.
2. For each experiment, finds the vault notes in `linked_concepts`.
3. Injects or updates a `## 关联实验` section:

```markdown
## 关联实验

- [[90-maps/Optics Lab#thin-lens|薄透镜成像实验]] — 拖动焦距/物距，观察像距与放大率变化。
```

4. Creates/updates `90-maps/Optics Lab.md`, a master catalog of all experiments.

### 6.2 Lab Map Note

`90-maps/Optics Lab.md`:

- Explains how to use the lab.
- Lists experiments grouped by difficulty and concept domain.
- Links to the desktop app tab (narrative only; no direct deep-link until a custom URI scheme is added).

## 7. Extensibility: Adding a New Experiment

1. **Backend**: create `engine/optibench/lab/experiments/<my_experiment>.py` subclassing `OpticsExperiment`.
2. **Test**: add a test in `engine/tests/test_lab.py`.
3. **Frontend**: no code change required if it uses standard parameter types.
4. **Vault links**: run `python scripts/sync_experiment_links.py`.
5. **Visual Index**: if the experiment produces a notable SVG, mention it in `90-maps/Visual Index.md`.

## 8. Roadmap

### Phase 1 — Lab foundation (this task)
- [ ] Refactor `optibench/lab/` to dynamic registry and reusable renderer.
- [ ] Fix broken `sensor_coverage` import.
- [ ] Implement four MVP experiments: thin lens, diffraction, color mixing, sensor coverage.
- [ ] Add `lab.py` API router and register it in `server.py`.
- [ ] Add `LabPage` in desktop app with catalog + runner.
- [ ] Sync vault links and create `90-maps/Optics Lab.md`.
- [ ] Tests green, commit.

### Phase 2 — Core optics experiments
- Snell’s law / total internal reflection
- Nyquist sampling & aliasing
- Depth of field / hyperfocal distance
- Angle of view vs sensor format
- Polarization / Malus law

### Phase 3 — Advanced labs
- Double-slit / single-slit interference
- Grating equation & spectral orders
- Blackbody / Planck curve
- MTF/OTF explorer
- Lens aberration spot diagrams

### Phase 4 — Learning analytics
- Track which experiments a learner has run.
- Recommend next experiments based on prerequisites.
- Export a "lab report" PDF.

## 9. Non-Goals (MVP)

- Real-time ray-tracing through complex lens systems.
- GPU compute or WebGL simulations.
- Persisting experiment runs in the database.
- Multi-user lab state.
- Direct Obsidian → running app deep links (URI scheme).

These are valuable but out of scope for the first architecture slice.
