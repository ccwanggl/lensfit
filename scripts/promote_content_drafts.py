"""Promote draft notes with substantial content to reviewed.

Skips templates and notes whose filenames contain Chinese characters (those
are filled separately with definitions).
"""

from __future__ import annotations

import re
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
MIN_BODY_LEN = 400


def has_chinese(filename: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", filename))


def main():
    updated = 0
    for md in sorted(VAULT.rglob("*.md")):
        rel = md.relative_to(VAULT)
        rel_str = str(rel).replace("\\", "/")
        if rel_str.startswith("templates/"):
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        fm = parts[1]
        body = parts[2]
        if "status: draft" not in fm:
            continue
        if has_chinese(rel.name):
            continue
        if len(body) < MIN_BODY_LEN:
            continue

        lines = []
        changed = False
        for line in fm.splitlines():
            if line.strip().startswith("status:"):
                lines.append("status: reviewed")
                changed = True
            else:
                lines.append(line)
        if not changed:
            continue
        new_text = "---\n" + "\n".join(lines) + "---" + body
        md.write_text(new_text, encoding="utf-8")
        updated += 1
        print(f"Promoted: {rel_str} (body {len(body)} chars)")
    print(f"\nPromoted {updated} content drafts to reviewed")


if __name__ == "__main__":
    main()
