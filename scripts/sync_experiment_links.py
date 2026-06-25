#!/usr/bin/env python3
"""Sync experiment links between the optics lab registry and the knowledge vault.

This script reads the backend experiment registry and:
1. Creates/updates ``OpticKnowledgeSpace/90-maps/Optics Lab.md`` with a catalog.
2. Injects a ``## 关联实验`` section into each linked vault note.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make engine package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from lensfit.lab import get_registry  # noqa: E402

VAULT = Path("OpticKnowledgeSpace")
LAB_MAP = VAULT / "90-maps" / "Optics Lab.md"

SECTION_MARKER = "## 关联实验"


def find_note(concept_path: str) -> Path | None:
    """Find a vault note by its path without .md extension.

    Tries the exact path plus common language variants.
    """
    candidates = [
        VAULT / f"{concept_path}.md",
    ]
    # If the note has an English kebab-case name, also try a Chinese translation
    # by looking for any .md file in the same directory whose stem maps... this is
    # heuristic; we simply check the exact candidate first.
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def ensure_section(text: str, section: str) -> str:
    """Insert or replace a `## 关联实验` section near the end of the note."""
    if SECTION_MARKER in text:
        # Replace existing section until next ## or end of file
        before, _, after = text.partition(SECTION_MARKER)
        # Find the start of the next top-level section after the marker
        next_section_idx = after.find("\n## ")
        rest = after[next_section_idx:] if next_section_idx != -1 else ""
        return before.rstrip() + "\n\n" + section + "\n" + rest.lstrip()
    return text.rstrip() + "\n\n" + section + "\n"


def build_experiment_link(experiment) -> str:
    return (
        f"- [[90-maps/Optics Lab#{experiment.id}|{experiment.title}]] — "
        f"{experiment.description}"
    )


def sync_note_links() -> int:
    registry = get_registry()
    updated = 0
    for exp in registry.list_experiments():
        link_line = build_experiment_link(exp)
        for concept in exp.linked_concepts:
            note = find_note(concept)
            if note is None:
                print(f"  未找到笔记: {concept}")
                continue
            text = note.read_text(encoding="utf-8")
            section = f"{SECTION_MARKER}\n\n{link_line}"
            new_text = ensure_section(text, section)
            if new_text != text:
                note.write_text(new_text, encoding="utf-8")
                updated += 1
                print(f"  已更新: {note.relative_to(VAULT)}")
    return updated


def sync_lab_map() -> None:
    registry = get_registry()
    experiments = registry.list_experiments()

    lines = [
        "---",
        "id: map.optics-lab",
        "title: 光学实验室",
        "type: map",
        "status: reviewed",
        "aliases:",
        "  - Optics Lab",
        "  - 实验室",
        "---",
        "",
        "# 光学实验室",
        "",
        "本页汇总 LensFit 中所有可交互的光学实验。每个实验都与知识库中的概念/公式笔记双向链接，"
        "你可以在阅读笔记后打开实验，通过调整参数来建立直觉。",
        "",
        "> 在 LensFit 桌面应用中，点击顶部导航栏的「光学实验室」即可运行这些实验。",
        "",
        "---",
        "",
        "## 实验目录",
        "",
    ]

    difficulty_label = {
        "foundation": "基础",
        "intermediate": "进阶",
        "advanced": "高级",
    }

    for exp in sorted(experiments, key=lambda e: (e.difficulty, e.title)):
        diff = difficulty_label.get(exp.difficulty, exp.difficulty)
        lines.append(f"### {exp.title}")
        lines.append(f"")
        lines.append(f"- **难度**: {diff}")
        lines.append(f"- **说明**: {exp.description}")
        lines.append(f"- **学习目标**: {', '.join(exp.learning_objectives) or '—'}")
        if exp.linked_concepts:
            concept_links = ", ".join(
                f"[[{c}|{c.split('/')[-1]}]]" for c in exp.linked_concepts
            )
            lines.append(f"- **关联笔记**: {concept_links}")
        lines.append(f"")

    lines.extend([
        "---",
        "",
        "## 如何新增实验",
        "",
        "1. 在后端创建 `engine/lensfit/lab/experiments/<your-experiment>.py` 并继承 `OpticsExperiment`。",
        "2. 声明 `linked_concepts` 指向本知识库的笔记路径。",
        "3. 运行 `python scripts/sync_experiment_links.py` 更新本页和关联笔记。",
        "",
        "详见架构文档：`docs/development/plans/optics-lab-architecture.md`。",
        "",
    ])

    LAB_MAP.write_text("\n".join(lines), encoding="utf-8")
    print(f"  已更新: {LAB_MAP.relative_to(VAULT)}")


def main():
    print("同步光学实验室链接...")
    sync_lab_map()
    count = sync_note_links()
    print(f"\n完成，更新了 {count} 个笔记。")


if __name__ == "__main__":
    main()
