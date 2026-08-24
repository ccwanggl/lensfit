#!/usr/bin/env python3
"""Cross-platform desktop build script for OptiBench.

Builds the Python engine sidecar with PyInstaller and then packages the Tauri
desktop application.  Works on Windows, macOS, and Linux.

Usage:
    python scripts/build-desktop.py
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NoReturn


def project_root() -> Path:
    """Return repository root directory."""
    return Path(__file__).parent.parent.resolve()


def python_executable(venv_dir: Path) -> Path:
    """Return path to Python interpreter inside the virtual environment."""
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def npm_executable() -> str:
    """Return npm command name."""
    return shutil.which("npm") or "npm"


def uv_executable() -> str | None:
    """Return uv command path if available."""
    return shutil.which("uv")


def use_uv() -> bool:
    """Check whether to use uv for venv/pip operations."""
    return uv_executable() is not None


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> None:
    """Run a command, printing it first."""
    printable = " ".join(str(c) for c in cmd)
    print(f"[BUILD] {printable}")
    subprocess.run(cmd, cwd=cwd, check=check)


def create_venv(venv_dir: Path) -> None:
    """Create a Python virtual environment, preferring uv when available."""
    if use_uv():
        print("[BUILD] Creating Python virtual environment with uv...")
        run([uv_executable(), "venv", str(venv_dir)], cwd=project_root())
    else:
        print("[BUILD] Creating Python virtual environment with venv module...")
        run([sys.executable, "-m", "venv", str(venv_dir)], cwd=project_root())


def install_engine_deps(py: Path, engine_dir: Path) -> None:
    """Install engine dependencies in editable mode."""
    if use_uv():
        print("[BUILD] Installing engine dependencies with uv (editable mode)...")
        run([uv_executable(), "pip", "install", "-e", ".[dev]"], cwd=engine_dir)
    else:
        print("[BUILD] Installing engine dependencies with pip (editable mode)...")
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"], cwd=engine_dir)
        run([str(py), "-m", "pip", "install", "-e", ".[dev]"], cwd=engine_dir)


def ensure_venv(venv_dir: Path) -> Path:
    """Create virtual environment and install engine dependencies if needed."""
    py = python_executable(venv_dir)

    if not venv_dir.exists():
        create_venv(venv_dir)

    if not py.exists():
        print(f"[ERROR] Python not found at {py}", file=sys.stderr)
        sys.exit(1)

    try:
        subprocess.run(
            [str(py), "-c", "import optibench"],
            cwd=project_root(),
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError:
        install_engine_deps(py, project_root() / "engine")

    return py


def main() -> NoReturn:
    root = project_root()
    engine_dir = root / "engine"
    frontend_dir = root / "apps" / "desktop"
    venv_dir = root / ".venv"

    py = ensure_venv(venv_dir)

    print("[BUILD] Building Python engine sidecar...")
    run([str(py), "build_sidecar.py"], cwd=engine_dir)

    print("[BUILD] Installing Node.js dependencies...")
    run([npm_executable(), "install"], cwd=frontend_dir)

    print("[BUILD] Building Tauri desktop app...")
    run([npm_executable(), "run", "tauri", "build"], cwd=frontend_dir)

    print("[BUILD] Build complete.")
    print("[BUILD] Artifacts should be in:")
    print(f"        {frontend_dir / 'src-tauri' / 'target' / 'release' / 'bundle'}")

    sys.exit(0)


if __name__ == "__main__":
    main()
