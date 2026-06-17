"""List all draft notes with body length."""

from __future__ import annotations

from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")


def main():
    entries = []
    for md in sorted(VAULT.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        if text.startswith("---") and "status: draft" in text.split("---", 2)[1]:
            rel = str(md.relative_to(VAULT)).replace("\\", "/")
            body_len = len(text.split("---", 2)[2])
            entries.append((body_len, rel))

    entries.sort(key=lambda x: x[1])
    lines = [f"{body_len:6d}  {rel}" for body_len, rel in entries]
    lines.append(f"\nTotal drafts: {len(entries)}")
    out = Path("drafts_list_utf8.txt")
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
