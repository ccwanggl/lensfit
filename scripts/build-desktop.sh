#!/bin/bash
# Build LensFit desktop application (sidecar + Tauri bundle)
#
# This is a thin Unix wrapper around scripts/build-desktop.py, which is the
# canonical cross-platform build script.  On Windows use scripts/build-desktop.bat
# or run `python scripts/build-desktop.py` directly.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/build-desktop.py" "$@"
