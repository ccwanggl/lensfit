#!/bin/bash
set -e

echo "=== Building LensFit Desktop ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

# Build Python engine sidecar
echo "Building Python engine sidecar..."
cd engine
source .venv/bin/activate
python build_sidecar.py

# Build Tauri desktop app
echo "Building Tauri desktop app..."
cd ../apps/desktop
npm install
npm run tauri build

echo "=== Build Complete ==="
echo "Artifacts in: apps/desktop/src-tauri/target/release/bundle/"
