# Plan: OptiBench as a Self-Study Optics Laboratory

## Goal

Transform OptiBench from a "selection helper" into a **self-study optics laboratory**: every physical concept in the knowledge vault should have a runnable, visual experiment that learners can manipulate to build intuition.

## Philosophy

- **Concept → Experiment → Intuition**: a learner reads an atomic note, runs the linked experiment, changes parameters, and sees the result.
- **Progressive disclosure**: experiments start with sliders and 2-D plots; advanced learners can inspect raw data and formulas.
- **Vault-driven**: the `OpticKnowledgeSpace/` vault remains the source of truth for what concepts exist; the code exposes experiments for those concepts.

## Architecture

```text
OpticKnowledgeSpace/          # human-readable concepts + experiment links
  10-concepts/focal-length.md
    ## 关联实验
    - [[lab/thin-lens|薄透镜成像实验]]

engine/optibench/lab/           # backend experiment framework
  base.py                     # OpticsExperiment base class
  registry.py                 # ExperimentRegistry
  experiments/
    thin_lens.py              # Gaussian lens equation + ray diagram
    diffraction.py            # Airy disk vs aperture/wavelength
    color_mixing.py           # RGB/SPD mixing and CIE chromaticity
    sensor_coverage.py        # image circle vs sensor rectangle
    interference.py           # double-slit (future)
    polarization.py           # Malus law (future)

engine/optibench/api/routers/lab.py
  GET  /api/v1/lab/experiments
  POST /api/v1/lab/experiments/{id}/run  -> {data, svg, notes}

apps/desktop/src/lab/         # frontend lab UI (React)
  LabPage.tsx
  ExperimentCard.tsx
  ExperimentRunner.tsx
```

## Backend Experiment Contract

Each experiment is a class:

```python
class ThinLensExperiment(OpticsExperiment):
    experiment_id = "thin-lens"
    title = "薄透镜成像实验"
    linked_concepts = ["10-concepts/focal-length", "20-formulas/thin-lens-gauss"]
    parameters = [
        Parameter(name="focal_length", label="焦距", type="float", default=50, min=10, max=200, unit="mm"),
        Parameter(name="object_distance", label="物距", type="float", default=100, min=20, max=500, unit="mm"),
    ]

    def run(self, params: dict) -> ExperimentResult:
        # compute image_distance, magnification, chief rays
        # return data + SVG string
```

`ExperimentResult` contains:

- `data`: serializable dict of computed values.
- `svg`: an SVG string rendered by matplotlib or hand-written geometry.
- `warnings`: list of human-readable caveats (e.g., "虚像，屏幕无法承接").

## Frontend Lab Page

- Grid of experiment cards with title, concept tags, and thumbnail.
- Click opens runner: parameter sliders on the left, SVG visualization on the right.
- "Open in Vault" button jumps to the linked concept note.

## Knowledge Base Integration

- Add a `## 关联实验` section to concept/formula notes.
- Use a script `scripts/sync_experiment_links.py` to auto-generate/update these sections from `registry.py`.
- This keeps the vault and code in sync as new experiments are added.

## MVP Experiments (first slice)

1. **thin-lens** — object/image distance, magnification, ray diagram.
2. **diffraction** — Airy disk diameter vs wavelength and aperture.
3. **color-mixing** — mix two monochromatic spectra and see resulting chromaticity.
4. **sensor-coverage** — image circle vs sensor size, visualize vignetting boundary.

## Success Criteria

- [ ] Backend experiment framework compiles and tests pass.
- [ ] Four MVP experiments return valid SVG + JSON via API.
- [ ] Vault notes for linked concepts include `## 关联实验` sections.
- [ ] Desktop app has a reachable `/lab` page that can run at least one experiment.
- [ ] All existing tests/lint/build gates remain green.
