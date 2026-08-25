"""Content loader — resolves the modules root and serves the shared index.

Resolution order for the modules root:

1. ``OPTIBENCH_MODULES_DIR`` environment variable (explicit override).
2. PyInstaller sidecar bundle: ``<sys._MEIPASS>/modules`` (packed by
   ``build_sidecar.py`` via ``--add-data``).
3. Source checkout: ``<repo root>/modules`` derived from this file's path.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from optibench.content.index import ContentIndex

_ENV_VAR = "OPTIBENCH_MODULES_DIR"


def resolve_modules_root() -> Path:
    """Resolve the modules root directory for the current runtime."""
    env = os.environ.get(_ENV_VAR)
    if env:
        return Path(env)
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "modules"
    # engine/optibench/content/loader.py -> repo root is parents[3].
    return Path(__file__).resolve().parents[3] / "modules"


_INDEX: ContentIndex | None = None


def get_content_index() -> ContentIndex:
    """Return the shared content index, building it on first access."""
    global _INDEX
    if _INDEX is None:
        _INDEX = ContentIndex.build(resolve_modules_root())
    return _INDEX


def reset_content_index() -> None:
    """Drop the cached index (used by tests)."""
    global _INDEX
    _INDEX = None
