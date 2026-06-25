#!/usr/bin/env python3
"""Sync experiment links between the optics lab registry and the knowledge vault.

This script reads the backend experiment registry and:
1. Creates/updates ``OpticKnowledgeSpace/90-maps/Optics Lab.md`` with a catalog.
2. Injects a ``## 关联实验`` section into each linked vault note.
"""

from __future__ import annotations

import sys
import re
from collections import defaultdict
from pathlib import Path

# Make engine package importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "engine"))

from lensfit.lab import get_registry  # noqa: E402

VAULT = Path("OpticKnowledgeSpace")
LAB_MAP = VAULT / "90-maps" / "Optics Lab.md"

SECTION_MARKER = "## 关联实验"
EXPERIMENT_SECTION_RE = re.compile(
    r"(?:\n|^)## (?:关联实验|相关实验|Related experiments?|Related experiment)\n.*?(?=\n## |\Z)",
    re.DOTALL,
)


DIFFICULTY_LABEL = {
    "foundation": "基础",
    "intermediate": "进阶",
    "advanced": "高级",
}


DIFFICULTY_GROUPS = [
    ("foundation", "基础实验"),
    ("intermediate", "进阶实验"),
    ("advanced", "高级实验"),
]


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
    """Replace legacy experiment sections with one canonical section."""
    cleaned = EXPERIMENT_SECTION_RE.sub("", text).rstrip()
    return cleaned + "\n\n" + section + "\n"


def build_experiment_link(experiment) -> str:
    return (
        f"- [[90-maps/Optics Lab#{experiment.title}|{experiment.title}]] — "
        f"{experiment.description}"
    )


def format_concept_links(concept_paths: list[str]) -> str:
    links: list[str] = []
    seen: set[tuple[str, str]] = set()
    for concept_path in concept_paths:
        note = find_note(concept_path)
        label = note_title(note) if note is not None else concept_path.split("/")[-1]
        folder = concept_path.split("/", 1)[0]
        key = (folder, label)
        if key in seen:
            continue
        seen.add(key)
        links.append(f"[[{concept_path}|{label}]]")
    return "、".join(links)


def note_title(note: Path) -> str:
    in_frontmatter = False
    in_aliases = False
    title = note.stem
    first_chinese_alias = ""
    for line in note.read_text(encoding="utf-8").splitlines():
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            break
        if not in_frontmatter:
            continue
        if line.startswith("title:"):
            title = clean_frontmatter_value(line.split(":", 1)[1])
            in_aliases = False
            continue
        if line.startswith("aliases:"):
            in_aliases = True
            continue
        if in_aliases and line.startswith("  - "):
            alias = clean_frontmatter_value(line.split("-", 1)[1])
            if not first_chinese_alias and re.search(r"[\u4e00-\u9fff]", alias):
                first_chinese_alias = alias
        if in_aliases and line and not line.startswith("  - "):
            in_aliases = False
    if re.search(r"[\u4e00-\u9fff]", title):
        return title
    return first_chinese_alias or title


def clean_frontmatter_value(value: str) -> str:
    return value.strip().strip("\"'").removesuffix("---").strip()


def sync_note_links() -> int:
    registry = get_registry()
    links_by_note: dict[Path, list[str]] = defaultdict(list)

    for exp in registry.list_experiments():
        link_line = build_experiment_link(exp)
        for concept in exp.linked_concepts:
            note = find_note(concept)
            if note is None:
                print(f"  未找到笔记: {concept}")
                continue
            if link_line not in links_by_note[note]:
                links_by_note[note].append(link_line)

    updated = 0
    for note, link_lines in links_by_note.items():
        text = note.read_text(encoding="utf-8")
        section = SECTION_MARKER + "\n\n" + "\n".join(link_lines)
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

    for difficulty, heading in DIFFICULTY_GROUPS:
        group = [exp for exp in experiments if exp.difficulty == difficulty]
        if not group:
            continue

        lines.append(f"### {heading}")
        lines.append("")
        for exp in sorted(group, key=lambda e: e.title):
            diff = DIFFICULTY_LABEL.get(exp.difficulty, exp.difficulty)
            lines.append(f"#### {exp.title}")
            lines.append("")
            lines.append(f"- **难度**：{diff}")
            lines.append(f"- **说明**：{exp.description}")
            if exp.learning_objectives:
                lines.append("- **学习目标**：")
                for objective in exp.learning_objectives:
                    lines.append(f"  - {objective}")
            else:
                lines.append("- **学习目标**：—")
            if exp.linked_concepts:
                lines.append(f"- **关联笔记**：{format_concept_links(exp.linked_concepts)}")
            lines.append("")

    remaining = [
        exp for exp in experiments
        if exp.difficulty not in {difficulty for difficulty, _ in DIFFICULTY_GROUPS}
    ]
    if remaining:
        lines.append("### 其他实验")
        lines.append("")
    for exp in sorted(remaining, key=lambda e: (e.difficulty, e.title)):
        diff = DIFFICULTY_LABEL.get(exp.difficulty, exp.difficulty)
        lines.append(f"### {exp.title}")
        lines.append("")
        lines.append(f"- **难度**：{diff}")
        lines.append(f"- **说明**：{exp.description}")
        lines.append("- **学习目标**：")
        for objective in exp.learning_objectives:
            lines.append(f"  - {objective}")
        if exp.linked_concepts:
            lines.append(f"- **关联笔记**：{format_concept_links(exp.linked_concepts)}")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## 如何新增实验",
        "",
        "1. 在后端创建 `engine/lensfit/lab/experiments/<your-experiment>.py` 并继承 `OpticsExperiment`。",
        "2. 声明 `linked_concepts` 指向本知识库的笔记路径。",
        "3. 运行 `python scripts/sync_experiment_links.py` 更新本页和关联笔记。",
        "",
        "详见当前执行计划：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`。",
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
