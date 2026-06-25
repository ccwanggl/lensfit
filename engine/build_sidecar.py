"""Build LensFit engine as a standalone binary for Tauri sidecar."""

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

    binary_name = f"lensfit-engine-{target}"
    if system == "Windows":
        binary_name += ".exe"

    print(f"Building sidecar for {target} ...")

    hidden_imports = [
        "lensfit.api.server",
        "lensfit.core.thin_lens",
        "lensfit.core.sensor",
        "lensfit.core.utils",
        "lensfit.core.types",
        "lensfit.db.models",
        "lensfit.db.catalog",
        "lensfit.domains.base",
        "lensfit.domains.industrial",
        "lensfit.domains.photography",
        "lensfit.domains.microscope",
        "lensfit.domains.infrared",
        "lensfit.matching.engine",
        "lensfit.matching.scoring",
        "lensfit.visualization.coverage",
        "lensfit.lab",
        "lensfit.lab.base",
        "lensfit.lab.registry",
        "lensfit.lab.schemas",
        "lensfit.lab.renderer",
        "lensfit.api.routers.lab",
        "lensfit.knowledge.formulas",
        "lensfit.knowledge.constraints",
        "lensfit.knowledge.presets",
        "lensfit.knowledge.engine",
        "lensfit.export.pdf_exporter",
        "lensfit.export.excel_exporter",
        "uvicorn",
        "fastapi",
        "sqlalchemy.ext.baked",
    ]

    # Auto-discover all lab experiments so the binary registry matches the source tree.
    experiments_dir = engine_dir / "lensfit" / "lab" / "experiments"
    for exp_file in sorted(experiments_dir.glob("*.py")):
        if exp_file.name == "__init__.py":
            continue
        module_name = f"lensfit.lab.experiments.{exp_file.stem}"
        hidden_imports.append(module_name)

    # PyInstaller data separator is ``;`` on Windows and ``:`` elsewhere.
    data_sep = ";" if system == "Windows" else ":"
    migrations_dir = engine_dir / "lensfit" / "db" / "migrations"
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
        "lensfit.db.migrations",
        "--collect-data",
        "lensfit.db.migrations",
        "--add-data",
        f"{migrations_dir}{data_sep}lensfit/db/migrations",
        "--add-data",
        f"{alembic_ini}{data_sep}.",
    ]
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    cmd.append(str(engine_dir / "lensfit" / "__main__.py"))

    subprocess.run(cmd, check=True)

    # Rename to plain "lensfit-engine" for local dev if target matches host
    plain_name = "lensfit-engine"
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
