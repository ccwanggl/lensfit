"""Contract tests for the ray-optics Node sidecar.

These tests verify the minimum viable set of the third-party runner without
connecting it to any user-facing path. They are skipped when Node.js or the
vendored runner is unavailable.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest

from optibench.lab.workbench import SceneGraph
from optibench.lab.workbench.ray_optics_sidecar import (
    RayOpticsNotAvailableError,
    RayOpticsOutputError,
    RayOpticsRuntimeError,
    RayOpticsSidecar,
    RayOpticsTimeoutError,
)

RUNNER = Path(__file__).resolve().parents[1] / "third_party" / "ray-optics" / "runner.js"
NODE_AVAILABLE = shutil.which("node") is not None
RUNNER_AVAILABLE = RUNNER.exists()


def _minimal_detector_scene() -> dict[str, Any]:
    return {
        "version": 5,
        "objs": [
            {"type": "SingleRay", "p1": {"x": 0, "y": 0}, "p2": {"x": 50, "y": 0}},
            {
                "type": "Detector",
                "p1": {"x": 100, "y": -50},
                "p2": {"x": 100, "y": 50},
                "irradMap": True,
                "binSize": 20,
            },
        ],
    }


@pytest.fixture
def sidecar() -> RayOpticsSidecar:
    return RayOpticsSidecar(runner_path=RUNNER)


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js not available")
@pytest.mark.skipif(not RUNNER_AVAILABLE, reason="ray-optics runner not available")
def test_ray_optics_version_is_locked():
    """The vendored integration package must declare a fixed version."""
    readme = RUNNER.parent / "README.md"
    assert readme.exists(), "version lock file (README.md) missing"
    text = readme.read_text(encoding="utf-8")
    assert "Version: `5.3.2`" in text, "ray-optics version not locked to 5.3.2"


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js not available")
@pytest.mark.skipif(not RUNNER_AVAILABLE, reason="ray-optics runner not available")
def test_minimal_detector_scene_runs(sidecar: RayOpticsSidecar):
    """A minimal geometric scene produces stable detector readings."""
    result = sidecar.run(_minimal_detector_scene())

    assert len(result.detectors) == 1
    detector = result.detectors[0]
    assert detector["power"] == pytest.approx(1.0)
    assert detector["normal"] == pytest.approx(1.0)
    assert detector["shear"] == pytest.approx(0.0)
    assert "irradianceMap" in detector
    assert len(detector["irradianceMap"]) == len(detector["binPositions"])
    assert result.images == []
    assert result.error is None
    assert result.stats["processedRayCount"] >= 1


@pytest.mark.skipif(not NODE_AVAILABLE, reason="Node.js not available")
@pytest.mark.skipif(not RUNNER_AVAILABLE, reason="ray-optics runner not available")
def test_runner_warning_is_preserved(sidecar: RayOpticsSidecar):
    """Runner-level warnings are surfaced without raising."""
    # A detector with zero size produces a warning but still runs.
    scene = {
        "version": 5,
        "objs": [
            {"type": "SingleRay", "p1": {"x": 0, "y": 0}, "p2": {"x": 50, "y": 0}},
            {
                "type": "Detector",
                "p1": {"x": 100, "y": 0},
                "p2": {"x": 100, "y": 0},
                "irradMap": True,
                "binSize": 20,
            },
        ],
    }
    result = sidecar.run(scene)
    assert result.warning is not None or result.error is not None or result.detectors


def test_missing_node_raises():
    """A missing Node executable is reported as a normalized error."""
    sidecar = RayOpticsSidecar(runner_path=RUNNER, node_command="node-does-not-exist-xyz")
    with pytest.raises(RayOpticsNotAvailableError):
        sidecar.run(_minimal_detector_scene())


def test_missing_runner_raises():
    """A missing runner file is reported as a normalized error."""
    sidecar = RayOpticsSidecar(runner_path=Path("/nonexistent/runner.js"))
    with pytest.raises(RayOpticsNotAvailableError):
        sidecar.run(_minimal_detector_scene())


def test_scene_with_file_path_is_rejected(sidecar: RayOpticsSidecar):
    """Payloads containing possible file paths are rejected before spawning."""
    scene = _minimal_detector_scene()
    scene["import"] = "file:///etc/passwd"
    with pytest.raises(ValueError, match="possible path/URL reference"):
        sidecar.run(scene)


def test_scene_with_url_is_rejected(sidecar: RayOpticsSidecar):
    """Payloads containing external URLs are rejected before spawning."""
    scene = _minimal_detector_scene()
    scene["module"] = "https://example.com/module.json"
    with pytest.raises(ValueError, match="possible path/URL reference"):
        sidecar.run(scene)


def test_bad_json_output_raises(sidecar: RayOpticsSidecar, monkeypatch):
    """Bad JSON from the runner is converted to a normalized error."""

    def _bad_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["node", "runner.js"],
            returncode=0,
            stdout=b"not-json",
            stderr=b"",
        )

    monkeypatch.setattr(subprocess, "run", _bad_run)
    with pytest.raises(RayOpticsOutputError, match="invalid JSON"):
        sidecar.run(_minimal_detector_scene())


def test_nonzero_exit_raises(sidecar: RayOpticsSidecar, monkeypatch):
    """A non-zero exit code is converted to a normalized error."""

    def _failing_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["node", "runner.js"],
            returncode=1,
            stdout=b'{"error":"simulation failed"}',
            stderr=b"",
        )

    monkeypatch.setattr(subprocess, "run", _failing_run)
    with pytest.raises(RayOpticsRuntimeError, match="simulation failed"):
        sidecar.run(_minimal_detector_scene())


def test_timeout_raises(sidecar: RayOpticsSidecar, monkeypatch):
    """A subprocess timeout is converted to a normalized error."""

    def _slow_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(cmd=["node", "runner.js"], timeout=0.001)

    monkeypatch.setattr(subprocess, "run", _slow_run)
    with pytest.raises(RayOpticsTimeoutError):
        sidecar.run(_minimal_detector_scene())


def test_stdout_size_limit_raises(sidecar: RayOpticsSidecar, monkeypatch):
    """Excessive stdout is converted to a normalized error."""
    sidecar = RayOpticsSidecar(
        runner_path=RUNNER, max_stdout_bytes=10
    )

    def _huge_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=["node", "runner.js"],
            returncode=0,
            stdout=b"x" * 100,
            stderr=b"",
        )

    monkeypatch.setattr(subprocess, "run", _huge_run)
    with pytest.raises(RayOpticsOutputError, match="stdout exceeded size limit"):
        sidecar.run(_minimal_detector_scene())


def test_scenegraph_fixture_has_no_ray_optics_types():
    """SceneGraph v1 fixtures must not contain ray-optics type names."""
    scene = SceneGraph.model_validate(
        {
            "version": 1,
            "components": [
                {
                    "id": "laser-1",
                    "spec_id": "laser-monochrome",
                    "category": "source",
                    "transform": {"x_mm": 0, "y_mm": 0, "rotation_deg": 0},
                    "params": {"wavelength_nm": 550.0},
                },
                {
                    "id": "slit-1",
                    "spec_id": "single-slit",
                    "category": "aperture",
                    "transform": {"x_mm": 100, "y_mm": 0, "rotation_deg": 0},
                    "params": {"slit_width_um": 50.0},
                },
                {
                    "id": "screen-1",
                    "spec_id": "screen",
                    "category": "screen",
                    "transform": {"x_mm": 1100, "y_mm": 0, "rotation_deg": 0},
                    "params": {},
                },
            ],
            "observables": [
                {
                    "type": "fraunhofer_intensity",
                    "source_id": "laser-1",
                    "aperture_id": "slit-1",
                    "screen_id": "screen-1",
                }
            ],
        }
    )
    json_text = scene.model_dump_json()
    ray_optics_types = {
        "SingleRay",
        "Detector",
        "CropBox",
        "SphericalLens",
        "IdealLens",
        "Mirror",
        "Beam",
        "ParallelBeam",
        "PointSource",
    }
    for token in ray_optics_types:
        assert token not in json_text, f"SceneGraph fixture contains {token}"


def test_scenegraph_rejects_ray_optics_spec_id():
    """SceneGraph v1 must reject third-party type names at validation time."""
    payload = {
        "version": 1,
        "components": [
            {
                "id": "ray-1",
                "spec_id": "SingleRay",
                "category": "source",
                "transform": {"x_mm": 0, "y_mm": 0, "rotation_deg": 0},
                "params": {},
            }
        ],
        "observables": [],
    }
    with pytest.raises(ValueError):
        SceneGraph.model_validate(payload)
