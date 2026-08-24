#!/usr/bin/env python3
"""Sync version from root VERSION file to all project manifests."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def read_version() -> str:
    version_file = ROOT / "VERSION"
    if not version_file.exists():
        print(f"ERROR: {version_file} not found", file=sys.stderr)
        sys.exit(1)
    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        print("ERROR: VERSION file is empty", file=sys.stderr)
        sys.exit(1)
    return version


def update_pyproject(version: str) -> None:
    path = ROOT / "engine" / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(r'^(version\s*=\s*").*?(")', rf"\g<1>{version}\g<2>", text, flags=re.M)
    if new_text == text:
        print(f"engine/pyproject.toml: no change needed ({version})")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"engine/pyproject.toml -> {version}")


def update_package_json(version: str) -> None:
    path = ROOT / "apps" / "desktop" / "package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version")
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"apps/desktop/package.json -> {version} (was {old})")


def update_tauri_conf(version: str) -> None:
    path = ROOT / "apps" / "desktop" / "src-tauri" / "tauri.conf.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    old = data.get("version")
    data["version"] = version
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"apps/desktop/src-tauri/tauri.conf.json -> {version} (was {old})")


def update_cargo_toml(version: str) -> None:
    path = ROOT / "apps" / "desktop" / "src-tauri" / "Cargo.toml"
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(
        r'^(version\s*=\s*").*?(")',
        rf"\g<1>{version}\g<2>",
        text,
        flags=re.M,
        count=1,
    )
    if new_text == text:
        print("apps/desktop/src-tauri/Cargo.toml: no change needed")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"apps/desktop/src-tauri/Cargo.toml -> {version}")


def update_server_py(version: str) -> None:
    path = ROOT / "engine" / "optibench" / "api" / "server.py"
    text = path.read_text(encoding="utf-8")
    new_text = re.sub(
        r'("version"\s*:\s*").*?("\s*\})',
        rf"\g<1>{version}\g<2>",
        text,
        count=1,
    )
    if new_text == text:
        print("engine/optibench/api/server.py: no change needed")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"engine/optibench/api/server.py health check -> {version}")


def main() -> int:
    version = read_version()
    print(f"Syncing version {version}...")
    update_pyproject(version)
    update_package_json(version)
    update_tauri_conf(version)
    update_cargo_toml(version)
    update_server_py(version)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
