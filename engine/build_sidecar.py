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
        "--hidden-import",
        "lensfit.api.server",
        "--hidden-import",
        "lensfit.core.thin_lens",
        "--hidden-import",
        "lensfit.core.sensor",
        "--hidden-import",
        "lensfit.core.utils",
        "--hidden-import",
        "lensfit.db.models",
        "--hidden-import",
        "lensfit.db.catalog",
        "--hidden-import",
        "lensfit.domains.base",
        "--hidden-import",
        "lensfit.domains.industrial",
        "--hidden-import",
        "lensfit.matching.engine",
        "--hidden-import",
        "lensfit.matching.scoring",
        "--hidden-import",
        "lensfit.visualization.coverage",
        "--hidden-import",
        "uvicorn",
        "--hidden-import",
        "fastapi",
        "--hidden-import",
        "sqlalchemy.ext.baked",
        str(engine_dir / "lensfit" / "__main__.py"),
    ]

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
