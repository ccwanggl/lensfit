"""Generate knowledgeLinks.json — slug → vault note mapping for obsidian:// deep links.

Scans the OpticKnowledgeSpace vault's `10-概念/` and `20-公式/` directories,
reads each note's YAML frontmatter `id` (e.g. `concept.diffraction-limit`),
strips the namespace prefix to get the slug, and emits a sorted JSON object
with two kind-scoped tables (concepts vs formulas may reuse a slug):

    {
      "concepts": { "<slug>": { "path": "...", "title": "..." }, ... },
      "formulas": { "<slug>": { "path": "...", "title": "..." }, ... }
    }

Resolution is scoped by usage: `linked_concepts` chips look up `concepts`,
`linked_formulas` chips look up `formulas`. This is a metadata-level sync
artifact (ADR-004): rerun after any vault directory reorganization to repair
all inter-repo links. Never edit by hand.

Usage:
    python scripts/generate_knowledge_links.py [--vault PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_VAULT = REPO_ROOT.parent / "OpticKnowledgeSpace"
DEFAULT_OUT = REPO_ROOT / "apps" / "desktop" / "src" / "lab" / "knowledgeLinks.json"

SCAN_DIRS = {"10-概念": "concepts", "20-公式": "formulas"}


@dataclass
class VaultNote:
    kind: str
    slug: str
    path: str  # vault-relative POSIX path, including extension
    title: str


def parse_frontmatter(text: str) -> dict | None:
    """Return the YAML frontmatter dict of a markdown note, or None."""
    if not text.startswith("---"):
        return None
    lines = text.splitlines()
    try:
        end = next(
            i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration:
        return None
    block = "\n".join(lines[1:end])
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise SystemExit("PyYAML is required: pip install pyyaml") from exc
    data = yaml.safe_load(block)
    return data if isinstance(data, dict) else None


def collect_notes(vault_root: Path) -> tuple[list[VaultNote], list[str]]:
    """Scan the vault; return (notes, warnings). Raises SystemExit on same-kind slug collision."""
    notes: list[VaultNote] = []
    warnings: list[str] = []
    by_kind_slug: dict[tuple[str, str], Path] = {}

    for scan_dir, kind in SCAN_DIRS.items():
        dir_path = vault_root / scan_dir
        if not dir_path.is_dir():
            warnings.append(f"目录不存在，已跳过：{scan_dir}")
            continue
        for md_path in sorted(dir_path.rglob("*.md")):
            fm = parse_frontmatter(md_path.read_text(encoding="utf-8"))
            if fm is None:
                warnings.append(f"无 frontmatter，已跳过：{scan_dir}/{md_path.name}")
                continue
            note_id = fm.get("id")
            if not isinstance(note_id, str) or not note_id.strip():
                warnings.append(f"缺少 id 字段，已跳过：{scan_dir}/{md_path.name}")
                continue
            slug = note_id.split(".", 1)[1] if "." in note_id else note_id
            slug = slug.strip()
            key = (kind, slug)
            previous = by_kind_slug.get(key)
            if previous is not None:
                raise SystemExit(
                    f"slug 冲突（{kind}）：{slug!r}\n  - {previous}\n  - {md_path}"
                )
            by_kind_slug[key] = md_path
            title = fm.get("title")
            notes.append(
                VaultNote(
                    kind=kind,
                    slug=slug,
                    path=(Path(scan_dir) / md_path.relative_to(dir_path)).as_posix(),
                    title=title if isinstance(title, str) else slug,
                )
            )
    return notes, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--vault", type=Path, default=DEFAULT_VAULT)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    notes, warnings = collect_notes(args.vault.resolve())
    for warning in warnings:
        print(f"[warn] {warning}")

    table: dict[str, dict[str, dict[str, str]]] = {"concepts": {}, "formulas": {}}
    for note in notes:
        table[note.kind][note.slug] = {"path": note.path, "title": note.title}
    payload = json.dumps(table, ensure_ascii=False, indent=2, sort_keys=True) + "\n"

    args.out.resolve().parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(payload, encoding="utf-8")
    counts = ", ".join(f"{kind} {len(items)}" for kind, items in table.items())
    print(f"[ok] 写出映射（{counts}）→ {args.out}（警告 {len(warnings)} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
