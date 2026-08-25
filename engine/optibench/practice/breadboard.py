"""Practice activities for the optical breadboard presets.

The preset scene definitions live in the desktop frontend
(``apps/desktop/src/lab/workbenchTypes.ts``); this module only mirrors their
stable ids so the learning layer can reference them through the
PracticeActivity interface.
"""

from __future__ import annotations

from optibench.practice.base import PracticeActivity

_PRESETS: list[tuple[str, str]] = [
    ("single-slit-breadboard", "单缝衍射面包板"),
    ("double-slit-breadboard", "双缝干涉面包板"),
]


def activities() -> list[PracticeActivity]:
    return [
        PracticeActivity(
            id=preset_id,
            title=title,
            kind="preset",
            entry={"type": "lab-experiment", "experiment_id": preset_id},
        )
        for preset_id, title in _PRESETS
    ]
