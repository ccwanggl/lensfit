"""List Chinese-filename draft notes ranked by incoming links."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE = re.compile(r"(?<!\\)\|")


def main():
    cnt: Counter = Counter()
    for md in VAULT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        for m in LINK_RE.finditer(text):
            raw = m.group(1)
            target = (
                PIPE.split(raw.replace("\\|", "|"), 1)[0]
                .split("#", 1)[0]
                .strip()
                .replace("\\", "/")
            )
            cnt[target] += 1

    drafts = []
    for md in VAULT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if text.startswith("---") and "status: draft" in text.split("---", 2)[1]:
            key = str(md.relative_to(VAULT).with_suffix("")).replace("\\", "/")
            if re.search(r"[\u4e00-\u9fff]", key):
                drafts.append((cnt[key], key))

    lines = [f"{c:3d}  {k}" for c, k in sorted(drafts, key=lambda x: -x[0])]
    Path("chinese_drafts_utf8.txt").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
