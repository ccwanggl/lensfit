"""Promote selected vault notes from draft to reviewed."""

from __future__ import annotations

from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")

FILES = [
    # Core concepts with visuals and content
    "10-concepts/focal-length.md",
    "10-concepts/dispersion.md",
    "10-concepts/chromatic-aberration.md",
    "10-concepts/f-number.md",
    "10-concepts/nyquist-frequency.md",
    "10-concepts/spectral-power-distribution.md",
    "10-concepts/color-temperature.md",
    "10-concepts/depth-of-field.md",
    "10-concepts/image-circle.md",
    "10-concepts/refractive-index.md",
    "10-concepts/aliasing.md",
    "10-concepts/fluorescence.md",
    "10-concepts/hyperspectral-imaging.md",
    "10-concepts/airy-disk.md",
    "10-concepts/multispectral-imaging.md",
    "10-concepts/pixel.md",
    "10-concepts/raman-scattering.md",
    # Devices
    "40-devices/telecentric-lens.md",
    # Formulas
    "20-formulas/angle-of-view.md",
    "20-formulas/coverage-ratio.md",
    "20-formulas/rayleigh-criterion.md",
    "20-formulas/thin-lens-gauss.md",
    "20-formulas/nyquist-frequency.md",
]


def main():
    updated = 0
    for rel in FILES:
        md = VAULT / rel
        if not md.exists():
            print(f"Missing {rel}")
            continue
        text = md.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        fm = parts[1]
        body = parts[2]
        lines = []
        changed = False
        for line in fm.splitlines():
            if line.strip().startswith("status:"):
                current = line.split(":", 1)[1].strip().strip('"').strip("'")
                if current != "reviewed":
                    lines.append("status: reviewed")
                    changed = True
                else:
                    lines.append(line)
            else:
                lines.append(line)
        if not changed:
            continue
        new_text = "---\n" + "\n".join(lines) + "---" + body
        md.write_text(new_text, encoding="utf-8")
        updated += 1
    print(f"Promoted {updated} notes to reviewed")


if __name__ == "__main__":
    main()
