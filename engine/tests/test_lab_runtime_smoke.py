"""Runtime smoke tests: every experiment must run, serialize and render.

Guards against the class of failures that unit tests per-experiment miss:
- numpy/None leaking into ``data`` breaks response serialization;
- malformed SVG breaks the frontend viewer;
- choice-typed parameters are exercised with their real option values.

Cases: each experiment runs with defaults, then with min-clamped and
max-clamped numeric parameters (choice/enum keep their default).
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET

import pytest

from optibench.lab.schemas import ExperimentRunResponse
from optibench.lab import get_registry


def _all_cases():
    registry = get_registry()
    cases = []
    for info in registry.list_experiments():
        cases.append((info.id, "defaults", {}))
        mins: dict = {}
        maxs: dict = {}
        for p in info.parameters:
            if p["type"] in ("choice", "enum"):
                mins[p["name"]] = p["default"]
                maxs[p["name"]] = p["default"]
                continue
            mins[p["name"]] = p["min"] if p["min"] is not None else 0
            maxs[p["name"]] = p["max"] if p["max"] is not None else 1
        cases.append((info.id, "mins", mins))
        cases.append((info.id, "maxs", maxs))
    return cases


_CASE_LIST = _all_cases()
_PARAMS_BY_KEY = {(exp_id, label): params for exp_id, label, params in _CASE_LIST}
_IDS_LABELS = [(exp_id, label) for exp_id, label, _ in _CASE_LIST]


@pytest.mark.parametrize(("experiment_id", "label"), _IDS_LABELS)
def test_experiment_runs_and_serializes(experiment_id: str, label: str):
    registry = get_registry()
    result = registry.run(experiment_id, dict(_PARAMS_BY_KEY[(experiment_id, label)]))

    payload = {
        "data": result.data,
        "svg": result.svg,
        "warnings": result.warnings,
        "learning_hints": result.learning_hints,
    }
    model = ExperimentRunResponse.model_validate(payload)
    dumped = json.dumps(model.model_dump(), allow_nan=False)
    assert "NaN" not in dumped

    root = ET.fromstring(result.svg)
    assert root.tag == "{http://www.w3.org/2000/svg}svg"
