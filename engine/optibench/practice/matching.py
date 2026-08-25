"""Practice activities for the four matching domains.

Deliberately does NOT import ``optibench.matching`` or ``optibench.domains``
internals (ADR-003 boundary): the domain ids and titles are stable public
identifiers, and the matching pipeline stays untouched behind this interface.
"""

from __future__ import annotations

from optibench.practice.base import PracticeActivity

# (id, title, frontend tab) — ids match the ``domain`` field used by
# ``optibench.knowledge.presets`` and the desktop app tabs.
_DOMAINS: list[tuple[str, str, str]] = [
    ("industrial", "工业视觉选型实践", "industrial"),
    ("photography", "摄影镜头选型实践", "photography"),
    ("microscope", "显微镜选型实践", "microscope"),
    ("infrared", "红外成像选型实践", "infrared"),
]


def activities() -> list[PracticeActivity]:
    return [
        PracticeActivity(
            id=domain_id,
            title=title,
            kind="domain",
            entry={"type": "domain-tab", "tab": tab},
        )
        for domain_id, title, tab in _DOMAINS
    ]
