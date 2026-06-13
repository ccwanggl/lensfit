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

    # Detect target triple
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        target = f"{machine}-apple-darwin"
    elif system == "Linux":
        target = f"{machine}-unknown-linux-gnu"
    elif system == "Windows":
        target = f"{machine}-pc-windows-msvc"
    else:
        target = f"{machine}-{system.lower()}"

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
        "lensfit.knowledge.formulas",
        "lensfit.knowledge.constraints",
        "lensfit.knowledge.presets",
        "lensfit.knowledge.engine",
        "lensfit.export.pdf_exporter",
        "lensfit.export.excel_exporter",
        "lensfit.db.migrations.versions.001_init",
        "lensfit.db.migrations.versions.002_add_match_snapshot",
        "lensfit.db.migrations.versions.c53e30ed595b_add_catalog_indexes",
        "lensfit.db.migrations.versions.003_merge_heads",
        "uvicorn",
        "fastapi",
        "sqlalchemy.ext.baked",
    ]

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
