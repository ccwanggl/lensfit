"""Build OptiBench engine as a standalone binary for Tauri sidecar."""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


def build() -> None:
    """Run PyInstaller to create the sidecar binary."""
    engine_dir = Path(__file__).parent.resolve()
    root_dir = engine_dir.parent
    tauri_bin_dir = root_dir / "apps" / "desktop" / "src-tauri" / "binaries"

    # Detect Rust target triple from Python platform info.
    system = platform.system()
    machine = platform.machine().lower()

    # Normalize Python machine names to Rust LLVM target architectures.
    arch_map = {
        "amd64": "x86_64",
        "x86": "i686",
        "win32": "i686",
        "arm64": "aarch64",
        "aarch64": "aarch64",
    }
    arch = arch_map.get(machine, machine)

    if system == "Darwin":
        target = f"{arch}-apple-darwin"
    elif system == "Linux":
        target = f"{arch}-unknown-linux-gnu"
    elif system == "Windows":
        target = f"{arch}-pc-windows-msvc"
    else:
        target = f"{arch}-{system.lower()}"

    binary_name = f"optibench-engine-{target}"
    if system == "Windows":
        binary_name += ".exe"

    print(f"Building sidecar for {target} ...")

    hidden_imports = [
        "optibench.api.server",
        "optibench.core.thin_lens",
        "optibench.core.sensor",
        "optibench.core.utils",
        "optibench.core.types",
        "optibench.db.models",
        "optibench.db.catalog",
        "optibench.domains.base",
        "optibench.domains.industrial",
        "optibench.domains.photography",
        "optibench.domains.microscope",
        "optibench.domains.infrared",
        "optibench.matching.engine",
        "optibench.matching.scoring",
        "optibench.visualization.coverage",
        "optibench.lab",
        "optibench.lab.base",
        "optibench.lab.registry",
        "optibench.lab.schemas",
        "optibench.lab.renderer",
        "optibench.api.routers.lab",
        "optibench.knowledge.formulas",
        "optibench.knowledge.constraints",
        "optibench.knowledge.presets",
        "optibench.knowledge.engine",
        "optibench.export.pdf_exporter",
        "optibench.export.excel_exporter",
        "uvicorn",
        "fastapi",
        "sqlalchemy.ext.baked",
    ]

    # Auto-discover all lab experiments so the binary registry matches the source tree.
    experiments_dir = engine_dir / "optibench" / "lab" / "experiments"
    for exp_file in sorted(experiments_dir.glob("*.py")):
        if exp_file.name == "__init__.py":
            continue
        module_name = f"optibench.lab.experiments.{exp_file.stem}"
        hidden_imports.append(module_name)

    # PyInstaller data separator is ``;`` on Windows and ``:`` elsewhere.
    data_sep = ";" if system == "Windows" else ":"
    migrations_dir = engine_dir / "optibench" / "db" / "migrations"
    alembic_ini = engine_dir / "alembic.ini"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        binary_name,
        "--distpath",
        str(tauri_bin_dir),
        "--workpath",
        str(engine_dir / "build"),
        "--specpath",
        str(engine_dir),
        "--collect-data",
        "alembic",
        "--collect-data",
        "sqlalchemy",
        "--collect-submodules",
        "optibench.db.migrations",
        "--collect-data",
        "optibench.db.migrations",
        "--add-data",
        f"{migrations_dir}{data_sep}optibench/db/migrations",
        "--add-data",
        f"{alembic_ini}{data_sep}.",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    cmd.append(str(engine_dir / "optibench" / "__main__.py"))

    subprocess.run(cmd, check=True)

    # Rename to plain "optibench-engine" for local dev if target matches host
    plain_name = "optibench-engine"
    if system == "Windows":
        plain_name += ".exe"

    src = tauri_bin_dir / binary_name
    dst = tauri_bin_dir / plain_name
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)
        print(f"Also copied to {dst.name}")

    print(f"Sidecar built: {src}")


if __name__ == "__main__":
    build()
