#!/bin/bash
# Start LensFit in development mode: backend + frontend
#
# This is a thin Unix wrapper around scripts/dev.py, which is the canonical
# cross-platform launcher.  On Windows use scripts/dev.bat or run
# `python scripts/dev.py` directly.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec python3 "${SCRIPT_DIR}/dev.py" "$@"
