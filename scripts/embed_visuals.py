"""Embed generated SVG visuals into relevant vault notes.

Run from the repository root:

    python scripts/embed_visuals.py
"""

from __future__ import annotations

from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
VISUALS_DIR = "attachments/visuals"

EMBEDS: dict[str, list[str]] = {
    "10-concepts/focal-length.md": ["thin-lens-geometry.svg", "angle-of-view.svg"],
    "10-concepts/image-circle.md": ["image-circle-coverage.svg"],
    "10-concepts/nyquist-frequency.md": ["nyquist-aliasing.svg"],
    "10-concepts/airy-disk.md": ["airy-disk.svg"],
    "10-concepts/depth-of-field.md": ["depth-of-field.svg"],
    "10-concepts/f-number.md": ["aperture-f-number.svg"],
    "20-formulas/thin-lens-gauss.md": ["thin-lens-geometry.svg"],
    "20-formulas/angle-of-view.md": ["angle-of-view.svg"],
    "20-formulas/coverage-ratio.md": ["image-circle-coverage.svg"],
    "20-formulas/nyquist-frequency.md": ["nyquist-aliasing.svg"],
    "50-learning/05-matching-basics.md": ["image-circle-coverage.svg"],
}


def build_section(filenames: list[str]) -> str:
    lines = ["\n## 可视化辅助\n"]
    for fn in filenames:
        caption = fn.replace(".svg", "").replace("-", " ").title()
        lines.append(f"![[{VISUALS_DIR}/{fn}]]")
        lines.append(f"*图：{caption}*\n")
    return "\n".join(lines)


def embed() -> int:
    count = 0
    for rel_path, filenames in EMBEDS.items():
        md_file = VAULT / rel_path
        if not md_file.exists():
            print(f"Missing {md_file}")
            continue
        text = md_file.read_text(encoding="utf-8")
        if "## 可视化辅助" in text:
            continue
        section = build_section(filenames)
        # Try to insert before the last ## 来源 section; otherwise append.
        source_idx = text.rfind("\n## 来源")
        if source_idx == -1:
            new_text = text.rstrip() + section
        else:
            new_text = text[:source_idx] + section + text[source_idx:]
        md_file.write_text(new_text, encoding="utf-8")
        count += 1
    print(f"Embedded visuals in {count} notes")
    return count


if __name__ == "__main__":
    embed()
