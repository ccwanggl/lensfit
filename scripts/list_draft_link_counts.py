"""List draft notes ranked by how many internal links point to them."""

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

    drafts: dict[str, Path] = {}
    for md in VAULT.rglob("*.md"):
        text = md.read_text(encoding="utf-8")
        if text.startswith("---") and "status: draft" in text.split("---", 2)[1]:
            rel_key = str(md.relative_to(VAULT).with_suffix("")).replace("\\", "/")
            drafts[rel_key] = md

    ranked = sorted(((cnt[k], k, p) for k, p in drafts.items()), key=lambda x: -x[0])
    for c, key, _ in ranked[:30]:
        print(f"{c:3d}  {key}")


if __name__ == "__main__":
    main()
