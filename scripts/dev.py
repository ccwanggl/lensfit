#!/usr/bin/env python3
"""Cross-platform development launcher for OptiBench.

Creates the Python virtual environment, installs dependencies, initializes the
SQLite database, starts the FastAPI backend, and then starts the Vite frontend
dev server.  Works on Windows, macOS, and Linux.

Usage (identical on every platform):
    uv run scripts/dev.py
or, with any Python 3.12+ already on PATH:
    python3 scripts/dev.py
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import NoReturn


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
BACKEND_PORT = 8765
FRONTEND_PORT = 5173
BACKEND_HOST = "127.0.0.1"
FRONTEND_URL = f"http://{BACKEND_HOST}:{FRONTEND_PORT}"
BACKEND_HEALTH_URL = f"http://{BACKEND_HOST}:{BACKEND_PORT}/health"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def project_root() -> Path:
    """Return repository root directory."""
    return Path(__file__).parent.parent.resolve()


def color_supported() -> bool:
    """Check if terminal supports ANSI colors."""
    if os.name == "nt" and not os.environ.get("ANSICON"):
        return False
    return sys.stdout.isatty()


def color(code: str, text: str) -> str:
    """Wrap text in ANSI color if supported."""
    if not color_supported():
        return text
    return f"\033[{code}m{text}\033[0m"


def info(text: str) -> None:
    print(color("0;32", f"[INFO] {text}"))


def warn(text: str) -> None:
    print(color("1;33", f"[WARN] {text}"))


def error(text: str) -> None:
    print(color("0;31", f"[ERROR] {text}"), file=sys.stderr)


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


def run(
    cmd: list[str],
    cwd: Path | None = None,
    check: bool = True,
    capture: bool = False,
) -> subprocess.CompletedProcess[str]:
    """Run a command and return CompletedProcess."""
    printable = " ".join(str(c) for c in cmd)
    info(f"Running: {printable}")
    kwargs: dict[str, object] = {"cwd": cwd, "text": True}
    if capture:
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.PIPE
    return subprocess.run(cmd, check=check, **kwargs)  # type: ignore[arg-type]


def wait_for_backend(url: str, timeout: float = 30.0, interval: float = 0.5) -> bool:
    """Poll backend health endpoint until ready or timeout."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except urllib.error.URLError:
            pass
        time.sleep(interval)
    return False


def create_venv(venv_dir: Path) -> None:
    """Create a Python virtual environment, preferring uv when available."""
    if use_uv():
        info("Creating Python virtual environment with uv...")
        run([uv_executable(), "venv", str(venv_dir)], cwd=project_root())
    else:
        info("Creating Python virtual environment with venv module...")
        run([sys.executable, "-m", "venv", str(venv_dir)], cwd=project_root())


def install_engine_deps(py: Path, engine_dir: Path) -> None:
    """Install engine dependencies in editable mode."""
    if use_uv():
        info("Installing engine dependencies with uv (editable mode)...")
        run([uv_executable(), "pip", "install", "-e", ".[dev]"], cwd=engine_dir)
    else:
        info("Installing engine dependencies with pip (editable mode)...")
        run([str(py), "-m", "pip", "install", "--upgrade", "pip"], cwd=engine_dir)
        run([str(py), "-m", "pip", "install", "-e", ".[dev]"], cwd=engine_dir)


def ensure_venv(venv_dir: Path) -> Path:
    """Create virtual environment and install engine dependencies if needed."""
    py = python_executable(venv_dir)

    if venv_dir.exists() and not py.exists():
        # The venv was created on another platform (its interpreter layout
        # differs), so it cannot run here. Recreate it from scratch.
        warn("Existing virtual environment belongs to another platform; recreating...")
        shutil.rmtree(venv_dir)

    if not venv_dir.exists():
        create_venv(venv_dir)

    if not py.exists():
        error(f"Virtual environment created but Python not found at {py}")
        sys.exit(1)

    # Check whether optibench-engine is installed in editable mode
    try:
        run([str(py), "-c", "import optibench"], capture=True, check=True)
    except subprocess.CalledProcessError:
        install_engine_deps(py, project_root() / "engine")

    return py


def ensure_npm_deps(frontend_dir: Path) -> None:
    """Install Node.js dependencies if missing or built for another platform."""
    node_modules = frontend_dir / "node_modules"
    marker = node_modules / ".optibench-platform"

    if node_modules.exists():
        current = marker.read_text(encoding="utf-8").strip() if marker.exists() else None
        if current == sys.platform:
            return
        # node_modules contains platform-specific binaries (esbuild, rollup...);
        # a tree copied from another OS will not run here. Reinstall in place.
        warn("node_modules was installed on another platform; reinstalling...")
        run([npm_executable(), "install"], cwd=frontend_dir)
    else:
        info("Installing Node.js dependencies...")
        run([npm_executable(), "install"], cwd=frontend_dir)

    marker.write_text(sys.platform + "\n", encoding="utf-8")


def ensure_database(py: Path, db_path: Path) -> None:
    """Run Alembic migrations and seed data if database is missing."""
    engine_dir = project_root() / "engine"

    info("Applying database migrations...")
    run([str(py), "-m", "alembic", "upgrade", "head"], cwd=engine_dir)

    if not db_path.exists():
        info("Initializing database with seed data...")
        import_script = project_root() / "database" / "import_scripts" / "import_seed.py"
        run([str(py), str(import_script)], cwd=project_root())
    else:
        # Even if DB exists, re-import seed to keep catalog data fresh
        warn("Database exists; skipping seed import. Use --reseed to force re-import.")


def reseed_database(py: Path) -> None:
    """Force re-import seed data."""
    import_script = project_root() / "database" / "import_scripts" / "import_seed.py"
    run([str(py), str(import_script)], cwd=project_root())


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> NoReturn:
    parser = argparse.ArgumentParser(description="Start OptiBench development servers.")
    parser.add_argument(
        "--reseed",
        action="store_true",
        help="Force re-import seed data even if database already exists.",
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Start only the backend server.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=BACKEND_PORT,
        help=f"Backend port (default: {BACKEND_PORT}).",
    )
    args = parser.parse_args()

    root = project_root()
    engine_dir = root / "engine"
    frontend_dir = root / "apps" / "desktop"
    venv_dir = engine_dir / ".venv"
    db_path = root / "optibench.db"

    py = ensure_venv(venv_dir)

    if args.reseed:
        reseed_database(py)
    else:
        ensure_database(py, db_path)

    if not args.backend_only:
        ensure_npm_deps(frontend_dir)

    # Start backend
    info(f"Starting backend on port {args.port}...")
    backend_cmd = [
        str(py),
        "-m",
        "optibench.api.server",
        "--port",
        str(args.port),
        "--host",
        BACKEND_HOST,
        "--mode",
        "dev",
        "--db",
        "sqlite:///optibench.db",
    ]
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    # Wait for backend health
    health_url = f"http://{BACKEND_HOST}:{args.port}/health"
    if wait_for_backend(health_url):
        info("Backend is ready.")
    else:
        error("Backend failed to start within timeout.")
        backend_proc.terminate()
        sys.exit(1)

    if args.backend_only:
        info(f"Backend running at http://{BACKEND_HOST}:{args.port}")
        info("Press Ctrl+C to stop.")
        try:
            backend_proc.wait()
        except KeyboardInterrupt:
            backend_proc.terminate()
        sys.exit(0)

    # Start frontend
    info("Starting frontend dev server...")
    frontend_proc = subprocess.Popen(
        [npm_executable(), "run", "dev"],
        cwd=str(frontend_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    info("OptiBench is running!")
    info(f"  Frontend: {FRONTEND_URL}")
    info(f"  Backend:  http://{BACKEND_HOST}:{args.port}")
    info("Press Ctrl+C to stop both servers.")

    # Stream output from both processes
    processes = [backend_proc, frontend_proc]
    try:
        while all(p.poll() is None for p in processes):
            for p in processes:
                if p.stdout is None:
                    continue
                line = p.stdout.readline()
                if line:
                    prefix = "[BACKEND]" if p is backend_proc else "[FRONTEND]"
                    print(f"{prefix} {line}", end="")
            time.sleep(0.05)
    except KeyboardInterrupt:
        pass
    finally:
        warn("Shutting down servers...")
        for p in processes:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
        info("Done.")
        sys.exit(0)


if __name__ == "__main__":
    main()
