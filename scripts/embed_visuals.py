"""Embed generated SVG visuals into relevant vault notes.

Run from the repository root:

    python scripts/embed_visuals.py
"""

from __future__ import annotations

from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
VISUALS_DIR = "attachments/visuals"

EMBEDS: dict[str, list[str]] = {
    # Core concepts
    "10-concepts/focal-length.md": ["thin-lens-geometry.svg", "angle-of-view.svg"],
    "10-concepts/image-circle.md": ["image-circle-coverage.svg"],
    "10-concepts/nyquist-frequency.md": ["nyquist-aliasing.svg"],
    "10-concepts/airy-disk.md": ["airy-disk.svg"],
    "10-concepts/depth-of-field.md": ["depth-of-field.svg"],
    "10-concepts/f-number.md": ["aperture-f-number.svg"],
    "10-concepts/refractive-index.md": ["refractive-index.svg"],
    "10-concepts/dispersion.md": ["dispersion.svg"],
    "10-concepts/chromatic-aberration.md": ["chromatic-aberration.svg"],
    "10-concepts/color-temperature.md": ["color-temperature.svg"],
    "10-concepts/multispectral-imaging.md": ["multispectral-hyperspectral.svg"],
    "10-concepts/hyperspectral-imaging.md": ["multispectral-hyperspectral.svg"],
    "10-concepts/spectral-power-distribution.md": ["spectral-power-distribution.svg"],
    "10-concepts/fluorescence.md": ["fluorescence.svg"],
    "10-concepts/raman-scattering.md": ["raman-scattering.svg"],
    "10-concepts/pixel.md": ["nyquist-aliasing.svg"],
    "10-concepts/aliasing.md": ["nyquist-aliasing.svg"],
    # Chinese stub concepts
    "10-concepts/像圈.md": ["image-circle-coverage.svg"],
    "10-concepts/像素精度.md": ["nyquist-aliasing.svg"],
    "10-concepts/全局快门.md": ["global-vs-rolling-shutter.svg"],
    "10-concepts/卷帘快门.md": ["global-vs-rolling-shutter.svg"],
    "10-concepts/动态范围.md": ["sensor-parameter-map.svg"],
    "10-concepts/奈奎斯特频率.md": ["nyquist-aliasing.svg"],
    "10-concepts/工作距离.md": ["lens-selection-checklist.svg"],
    "10-concepts/法兰距.md": ["lens-selection-checklist.svg"],
    "10-concepts/混叠.md": ["nyquist-aliasing.svg"],
    "10-concepts/渐晕.md": ["image-circle-coverage.svg"],
    "10-concepts/焦距.md": ["thin-lens-geometry.svg", "angle-of-view.svg"],
    "10-concepts/瑞利判据.md": ["airy-disk.svg"],
    "10-concepts/色差.md": ["chromatic-aberration.svg"],
    "10-concepts/色温.md": ["color-temperature.svg"],
    "10-concepts/艾里斑.md": ["airy-disk.svg"],
    "10-concepts/衍射极限.md": ["airy-disk.svg"],
    "10-concepts/视场.md": ["angle-of-view.svg"],
    "10-concepts/视角.md": ["angle-of-view.svg"],
    "10-concepts/读出噪声.md": ["sensor-parameter-map.svg"],
    "10-concepts/过采样.md": ["nyquist-aliasing.svg"],
    "10-concepts/近轴近似.md": ["thin-lens-geometry.svg"],
    # Devices
    "40-devices/telecentric-lens.md": ["telecentricity.svg"],
    # Formulas
    "20-formulas/thin-lens-gauss.md": ["thin-lens-geometry.svg"],
    "20-formulas/angle-of-view.md": ["angle-of-view.svg"],
    "20-formulas/coverage-ratio.md": ["image-circle-coverage.svg"],
    "20-formulas/nyquist-frequency.md": ["nyquist-aliasing.svg"],
    "20-formulas/rayleigh-criterion.md": ["airy-disk.svg"],
    # Learning chapters
    "50-learning/05-matching-basics.md": ["image-circle-coverage.svg", "matching-workflow.svg", "lens-selection-checklist.svg"],
    "50-learning/03-lens-parameters.md": ["lens-selection-checklist.svg"],
    "50-learning/04-sensors.md": ["sensor-parameter-map.svg"],
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
