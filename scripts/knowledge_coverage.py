"""Report knowledge-link coverage: vault notes vs experiment anchors (ADR-004).

Reads apps/desktop/src/lab/knowledgeLinks.json and the linked_concepts /
linked_formulas declared across lab experiments plus breadboard presets,
then prints a coverage summary and writes
scripts/knowledge_coverage_report.md with the full uncovered inventory.

The uncovered inventory is the experiment-proposal backlog: each entry is a
vault note with no runnable anchor in the software.

Usage:
    python scripts/knowledge_coverage.py [--write-report]
"""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINKS_PATH = REPO_ROOT / "apps" / "desktop" / "src" / "lab" / "knowledgeLinks.json"
REPORT_PATH = REPO_ROOT / "scripts" / "knowledge_coverage_report.md"

SCAN_TARGETS = [
    REPO_ROOT / "engine" / "optibench" / "lab" / "experiments",
    REPO_ROOT / "apps" / "desktop" / "src" / "lab",
]

LEGACY_PREFIXES = ("10-concepts/", "20-formulas/", "50-learning/")


def collect_declared_slugs() -> tuple[set[str], set[str], dict[str, int]]:
    concepts: set[str] = set()
    formulas: set[str] = set()
    legacy: dict[str, int] = {}
    files: list[Path] = []
    for target in SCAN_TARGETS:
        if "desktop" in str(target):
            files.extend(sorted(target.glob("*.ts")))
        else:
            files.extend(sorted(target.glob("*.py")))
    for path in files:
        text = path.read_text(encoding="utf-8")
        for field, bucket in (
            ("linked_concepts", concepts),
            ("linked_formulas", formulas),
        ):
            for m in re.finditer(rf"(?ms){field}\s*[=:]\s*\[(.*?)\]", text):
                for lit in re.findall(r'"([^"]+)"', m.group(1)):
                    if lit.startswith(LEGACY_PREFIXES):
                        legacy[lit] = legacy.get(lit, 0) + 1
                    elif field == "linked_concepts":
                        bucket.add(lit)
                    else:
                        bucket.add(lit)
    return concepts, formulas, legacy


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--write-report", action="store_true", help="同时写出 markdown 报告"
    )
    args = parser.parse_args()

    links = json.loads(LINKS_PATH.read_text(encoding="utf-8"))
    used_c, used_f, legacy = collect_declared_slugs()

    lines = [
        "# 知识—实验覆盖报告",
        "",
        f"> 生成：`scripts/knowledge_coverage.py`（数据源 `knowledgeLinks.json`）",
        "",
        "| 类别 | 知识库 | 已锚定 | 未覆盖 | 覆盖率 |",
        "|---|---|---|---|---|",
    ]
    uncovered: dict[str, list[str]] = {}
    for kind in ("concepts", "formulas"):
        table = links[kind]
        used = used_c if kind == "concepts" else used_f
        missing = sorted(set(table) - used)
        uncovered[kind] = missing
        ratio = f"{len(used & set(table)) / len(table):.0%}" if table else "-"
        lines.append(
            f"| {kind} | {len(table)} | {len(used & set(table))} "
            f"| {len(missing)} | {ratio} |"
        )
    lines += ["", f"遗留旧路径字面量：{sum(legacy.values())} 处（见 knowledge_links_unresolved.md）"]

    print("\n".join(lines))

    if not args.write_report:
        return 0

    for kind, label in (("concepts", "概念"), ("formulas", "公式")):
        table = links[kind]
        lines += ["", f"## 未覆盖{label}（{len(uncovered[kind])}）", ""]
        for slug in uncovered[kind]:
            entry = table[slug]
            lines.append(f"- `{slug}` — {entry['title']}（{entry['path']}）")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[ok] 报告已写出 → {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    raise SystemExit(main())
