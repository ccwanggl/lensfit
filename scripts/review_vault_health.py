"""Comprehensive health review of the LensFit Obsidian vault.

Run from repo root:

    python scripts/review_vault_health.py
"""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE = re.compile(r"(?<!\\)\|")


def normalize_target(raw: str) -> str:
    target = (
        PIPE.split(raw.replace("\\|", "|"), 1)[0]
        .split("#", 1)[0]
        .strip()
        .replace("\\", "/")
    )
    return target


def main():
    # Load all notes
    notes: dict[str, Path] = {}
    statuses: dict[str, str] = {}
    titles: dict[str, str] = {}
    incoming: Counter = Counter()
    outgoing: Counter = Counter()
    folder_counts: Counter = Counter()
    status_counts: Counter = Counter()
    no_visual: list[str] = []

    for md in sorted(VAULT.rglob("*.md")):
        rel = md.relative_to(VAULT)
        rel_key = str(rel.with_suffix("")).replace("\\", "/")
        folder = rel.parts[0] if rel.parts else ""
        folder_counts[folder] += 1

        text = md.read_text(encoding="utf-8")
        title = rel.stem
        status = "unknown"
        if text.startswith("---"):
            try:
                fm = text.split("---", 2)[1]
            except IndexError:
                fm = ""
            for line in fm.splitlines():
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                if line.strip().startswith("status:"):
                    status = line.split(":", 1)[1].strip().strip('"').strip("'")
        statuses[rel_key] = status
        titles[rel_key] = title
        status_counts[status] += 1
        notes[rel_key] = md

        # Visual embed check
        if "![[attachments/visuals/" not in text and rel_key.startswith("10-concepts/"):
            no_visual.append(rel_key)

    # Count links
    for rel_key, md in notes.items():
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            target = normalize_target(m.group(1))
            incoming[target] += 1
            outgoing[rel_key] += 1

    # Orphans: notes with 0 incoming links (excluding maps/readme/inbox)
    orphans = [
        k for k in notes
        if incoming[k] == 0
        and not k.endswith("/README")
        and not k.startswith("00-inbox/")
        and not k.startswith("90-maps/")
        and not k.startswith("templates/")
    ]

    # Draft stubs with incoming links
    draft_stubs = [
        (incoming[k], k, titles.get(k, k))
        for k, s in statuses.items()
        if s == "draft"
    ]
    draft_stubs.sort(key=lambda x: -x[0])

    report_lines = [
        "# Vault Health Review",
        "",
        f"Total notes: {len(notes)}",
        "",
        "## Folder distribution",
    ]
    for folder, count in sorted(folder_counts.items()):
        report_lines.append(f"- {folder}: {count}")

    report_lines += ["", "## Status distribution"]
    for status, count in sorted(status_counts.items(), key=lambda x: -x[1]):
        report_lines.append(f"- {status}: {count}")

    report_lines += ["", f"## Orphan notes (no incoming links): {len(orphans)}"]
    for k in orphans[:30]:
        report_lines.append(f"- {k}")

    report_lines += ["", f"## Top draft stubs by incoming links ({len(draft_stubs)} total)"]
    for c, k, t in draft_stubs[:30]:
        report_lines.append(f"- ({c}) {k} — {t}")

    report_lines += ["", f"## Concept notes without embedded visuals: {len(no_visual)}"]
    for k in sorted(no_visual)[:30]:
        report_lines.append(f"- {k}")

    report = "\n".join(report_lines)
    print(report)
    out = Path("vault_review_report.md")
    out.write_text(report, encoding="utf-8")
    print(f"\nReport saved to {out}")


if __name__ == "__main__":
    main()
