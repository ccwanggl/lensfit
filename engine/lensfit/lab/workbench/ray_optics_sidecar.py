"""ray-optics Node sidecar wrapper.

This module invokes the third-party `ray-optics` integration runner as a
stateless subprocess. It is intentionally isolated from the rest of the
workbench so that failures in the Node environment cannot break the native
Python experiments.

The contract is:

- Input: a ray-optics scene JSON (`dict`) written to the runner's stdin.
- Output: a normalized result object parsed from the runner's stdout.
- Errors: normalized to a small family of exceptions; no stack trace from the
  runner is leaked to callers unless explicitly requested.

The wrapper enforces resource limits and rejects payloads that may reference
arbitrary files or external resources.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class RayOpticsError(Exception):
    """Base class for ray-optics sidecar errors."""


class RayOpticsNotAvailableError(RayOpticsError):
    """Raised when Node.js or the runner is missing."""


class RayOpticsTimeoutError(RayOpticsError):
    """Raised when the runner does not finish within the configured timeout."""


class RayOpticsOutputError(RayOpticsError):
    """Raised when the runner output cannot be parsed or exceeds size limits."""


class RayOpticsRuntimeError(RayOpticsError):
    """Raised when the runner exits with non-zero status or reports an error."""


@dataclass(frozen=True)
class RayOpticsResult:
    """Normalized result from the ray-optics runner."""

    detectors: list[dict[str, Any]]
    images: list[dict[str, Any]]
    error: str | None
    warning: str | None
    stats: dict[str, Any]


class RayOpticsSidecar:
    """Stateless wrapper around the ray-optics Node runner.

    Parameters
    ----------
    runner_path:
        Path to ``runner.js``. Defaults to the vendored copy under
        ``engine/third_party/ray-optics/runner.js``.
    node_command:
        Node.js executable. Defaults to ``node`` resolved from ``PATH``.
    timeout_seconds:
        Maximum wall-clock time for one simulation request.
    max_stdout_bytes:
        Maximum stdout size before the run is aborted with
        :class:`RayOpticsOutputError`.
    max_stderr_bytes:
        Maximum stderr size before the run is aborted with
        :class:`RayOpticsOutputError`.
    """

    _PATH_RE = re.compile(r"[\\/]|://")

    def __init__(
        self,
        *,
        runner_path: str | os.PathLike[str] | None = None,
        node_command: str | None = None,
        timeout_seconds: float = 30.0,
        max_stdout_bytes: int = 8 * 1024 * 1024,
        max_stderr_bytes: int = 1 * 1024 * 1024,
    ) -> None:
        self.runner_path = Path(
            runner_path
            if runner_path is not None
            else Path(__file__).resolve().parents[3] / "third_party" / "ray-optics" / "runner.js"
        )
        self.node_command = node_command or "node"
        self.timeout_seconds = timeout_seconds
        self.max_stdout_bytes = max_stdout_bytes
        self.max_stderr_bytes = max_stderr_bytes

    def _validate_payload(self, scene: dict[str, Any]) -> None:
        """Ensure the scene payload cannot reference external resources."""
        if not isinstance(scene, dict):
            raise ValueError("ray-optics scene must be a JSON object")

        stack: list[Any] = [scene]
        while stack:
            item = stack.pop()
            if isinstance(item, dict):
                stack.extend(item.values())
            elif isinstance(item, list):
                stack.extend(item)
            elif isinstance(item, str):
                if self._PATH_RE.search(item):
                    raise ValueError(
                        "ray-optics scene contains a possible path/URL reference"
                    )

    def _require_runner(self) -> tuple[str, str]:
        """Return resolved node executable and runner path, or raise."""
        node = shutil.which(self.node_command)
        if node is None:
            raise RayOpticsNotAvailableError(
                f"Node.js executable not found: {self.node_command}"
            )
        if not self.runner_path.exists():
            raise RayOpticsNotAvailableError(
                f"ray-optics runner not found: {self.runner_path}"
            )
        return node, str(self.runner_path)

    def run(self, scene: dict[str, Any]) -> RayOpticsResult:
        """Run a ray-optics scene and return a normalized result.

        Parameters
        ----------
        scene:
            A ray-optics scene JSON object. Must not contain file paths or
            external URLs.

        Raises
        ------
        RayOpticsNotAvailableError
            If Node.js or the runner is missing.
        RayOpticsTimeoutError
            If the runner does not finish in time.
        RayOpticsOutputError
            If the output is empty, too large, or not valid JSON.
        RayOpticsRuntimeError
            If the runner exits non-zero or sets an ``error`` field.
        ValueError
            If the input scene contains suspicious path/URL strings.
        """
        self._validate_payload(scene)
        node, runner = self._require_runner()
        input_bytes = json.dumps(scene, separators=(",", ":")).encode("utf-8")

        try:
            proc = subprocess.run(
                [node, runner],
                input=input_bytes,
                capture_output=True,
                timeout=self.timeout_seconds,
            )
        except subprocess.TimeoutExpired as exc:
            raise RayOpticsTimeoutError(
                f"ray-optics runner timed out after {self.timeout_seconds}s"
            ) from exc
        except FileNotFoundError as exc:
            # This can happen if shutil.which returned a path that was removed
            # between the check and the call.
            raise RayOpticsNotAvailableError(
                f"Node.js executable disappeared: {self.node_command}"
            ) from exc

        if len(proc.stdout) > self.max_stdout_bytes:
            raise RayOpticsOutputError("ray-optics runner stdout exceeded size limit")
        if len(proc.stderr) > self.max_stderr_bytes:
            raise RayOpticsOutputError("ray-optics runner stderr exceeded size limit")

        if not proc.stdout.strip():
            stderr_text = proc.stderr.decode("utf-8", errors="replace").strip()
            raise RayOpticsOutputError(
                "ray-optics runner produced no output"
                + (f"; stderr: {stderr_text[:500]}" if stderr_text else "")
            )

        try:
            data = json.loads(proc.stdout.decode("utf-8"))
        except json.JSONDecodeError as exc:
            snippet = proc.stdout.decode("utf-8", errors="replace")[:500]
            raise RayOpticsOutputError(
                f"ray-optics runner returned invalid JSON: {snippet}"
            ) from exc

        if not isinstance(data, dict):
            raise RayOpticsOutputError("ray-optics runner returned a non-object JSON")

        if proc.returncode != 0 or data.get("error"):
            message = data.get("error") or f"runner exited with code {proc.returncode}"
            raise RayOpticsRuntimeError(message)

        return RayOpticsResult(
            detectors=list(data.get("detectors", [])),
            images=list(data.get("images", [])),
            error=data.get("error"),
            warning=data.get("warning"),
            stats={
                key: data[key]
                for key in (
                    "totalTruncation",
                    "processedRayCount",
                    "brightnessScale",
                )
                if key in data
            },
        )
