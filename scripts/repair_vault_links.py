"""Repair broken Obsidian wiki links inside OpticKnowledgeSpace.

This script:
1. Builds an index of all vault pages (filename, title, aliases).
2. Rewrites Chinese chapter placeholder links (e.g. `../50-learning/第6章`)
   to actual chapter filenames.
3. Creates minimal stub notes for unresolved atomic targets.
4. Fixes same-folder bare links that were mis-resolved to vault root.

Run from the repository root:

    python scripts/repair_vault_links.py [--dry-run]
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE_SPLIT_RE = re.compile(r"(?<!\\)\|")


def load_index() -> dict:
    """Index vault files by (folder, filename), title, and aliases."""
    index = {
        "by_path": {},
        "by_filename": {},
        "by_title": {},
        "by_alias": {},
    }
    for md in sorted(VAULT.rglob("*.md")):
        rel = md.relative_to(VAULT)
        text = md.read_text(encoding="utf-8")
        title = rel.stem
        aliases: list[str] = []
        if text.startswith("---"):
            frontmatter = text.split("---", 2)[1]
            for line in frontmatter.splitlines():
                if line.strip().startswith("title:"):
                    title = line.split(":", 1)[1].strip().strip('"').strip("'")
                if line.strip().startswith("aliases:"):
                    # Simple YAML list parsing
                    for alias_line in frontmatter.splitlines()[frontmatter.splitlines().index(line) + 1:]:
                        alias_line = alias_line.strip()
                        if not alias_line.startswith("-"):
                            break
                        alias = alias_line.lstrip("-").strip().strip('"').strip("'")
                        if alias:
                            aliases.append(alias)
        rel_key = str(rel.with_suffix("")).replace("\\", "/")
        index["by_path"][rel_key] = md
        index["by_filename"][rel.stem] = md
        index["by_title"][title] = md
        for alias in aliases:
            index["by_alias"][alias] = md
    return index


def build_chapter_map(index: dict) -> dict[str, Path]:
    """Map chapter numbers (1, 2, ..., 16) to actual 50-learning files."""
    chapter_map: dict[str, Path] = {}
    prefix_map: dict[str, Path] = {}
    for key, md in index["by_path"].items():
        if key.startswith("50-learning/"):
            stem = Path(key).name
            # Filenames like 00-introduction, 01-light-and-waves
            parts = stem.split("-", 1)
            if len(parts) == 2 and parts[0].isdigit():
                num = int(parts[0])
                prefix_map[str(num)] = md
                chapter_map[f"第{num}章"] = md
    # Also index by title in case chapters are linked by title
    for md in index["by_path"].values():
        rel = md.relative_to(VAULT)
        if str(rel.parent).replace("\\", "/") == "50-learning":
            title = index["by_title"].get(rel.stem, rel.stem)
            chapter_map[title] = md
    return chapter_map, prefix_map


def normalize_link(raw: str) -> tuple[str, str | None]:
    """Return (target, alias) with header anchors removed."""
    # In some notes the pipe was escaped as \|; normalize it to a real separator.
    temp = raw.replace("\\|", "|")
    parts = PIPE_SPLIT_RE.split(temp, 1)
    target = parts[0].strip().split("#", 1)[0].strip()
    alias = parts[1].strip() if len(parts) > 1 else None
    # Drop an alias that is just "filename.md" when target exists without it.
    if alias and alias.lower() == f"{target.lower()}.md":
        alias = None
    return target, alias


def resolve_target(source: Path, target: str, index: dict) -> Path | None:
    """Resolve a wiki-link target using Obsidian-like rules."""
    if not target:
        return None

    # Path-based target
    if "/" in target:
        if target.startswith(("../", "./")):
            candidate = (source.parent / target).resolve()
        else:
            candidate = (VAULT / target).resolve()
        md_candidate = candidate.with_suffix(".md")
        if md_candidate.exists():
            return md_candidate
        if candidate.is_dir():
            for name in ("README.md", "index.md"):
                if (candidate / name).exists():
                    return candidate / name
        return None

    # Bare filename/title/alias: prefer same folder, then vault-wide
    source_rel = source.relative_to(VAULT)
    same_folder = source_rel.parent / target
    keys = [
        str(same_folder).replace("\\", "/"),
        str(same_folder.parent / target).replace("\\", "/"),
    ]
    for key in keys:
        if key in index["by_path"]:
            return index["by_path"][key]

    for lookup in (index["by_filename"], index["by_title"], index["by_alias"]):
        if target in lookup:
            return lookup[target]

    return None


def chapter_target_to_file(target: str, chapter_map: dict[str, Path]) -> Path | None:
    """If target is a Chinese chapter placeholder, return the real chapter file."""
    # Match patterns like "../50-learning/第6章", "50-learning/第6章", "第6章工业视觉"
    m = re.search(r"(?:50-learning/)?第(\d+)章", target)
    if not m:
        return None
    num = m.group(1)
    return chapter_map.get(f"第{int(num)}章")


def make_link(target: str, alias: str | None) -> str:
    if alias and alias != target:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def repair(dry_run: bool = False) -> dict:
    index = load_index()
    chapter_map, _ = build_chapter_map(index)

    stats = {"replaced_chapter": 0, "created_stub": 0, "fixed_bare": 0, "already_ok": 0}

    for md_file in sorted(VAULT.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        original_text = text
        source_rel = md_file.relative_to(VAULT)

        def repl(match: re.Match) -> str:
            raw = match.group(1)
            target, alias = normalize_link(raw)

            # 1. Chinese chapter placeholders -> real chapter file
            real_chapter = chapter_target_to_file(target, chapter_map)
            if real_chapter:
                new_target = str(real_chapter.relative_to(VAULT).with_suffix(""))
                stats["replaced_chapter"] += 1
                return make_link(new_target, alias)

            # 2. Try to resolve existing target
            resolved = resolve_target(md_file, target, index)
            if resolved:
                # If it resolved to a same-folder file that was previously
                # mis-detected as broken, still count as OK.
                stats["already_ok"] += 1
                return match.group(0)

            # 3. Create stub for unresolved atomic target
            folder = "10-concepts"
            if target.startswith("../20-formulas/") or "/20-formulas/" in target:
                folder = "20-formulas"
            elif target.startswith("../40-devices/") or "/40-devices/" in target:
                folder = "40-devices"

            # Clean target path
            clean_target = target.strip("./")
            if "/" in clean_target:
                stub_rel = Path(clean_target)
            else:
                stub_rel = Path(folder) / clean_target

            stub_path = VAULT / stub_rel.with_suffix(".md")
            if not stub_path.exists():
                if not dry_run:
                    stub_path.parent.mkdir(parents=True, exist_ok=True)
                    title = stub_rel.stem.replace("-", " ").replace("_", " ")
                    stub_path.write_text(
                        f"""---
id: stub.{stub_rel.stem}
title: {title}
type: concept
domains: []
status: draft
source_ids: []
aliases:
  - {alias or title}
---

# {title}

> 此笔记为自动生成的占位 stub，用于修复断裂的双链。需要补充定义、公式、适用场景和来源。
""",
                        encoding="utf-8",
                    )
                stats["created_stub"] += 1
                # Update index so later links in same run can resolve
                index["by_path"][str(stub_rel)] = stub_path

            new_target = str(stub_rel)
            stats["fixed_bare"] += 1
            return make_link(new_target, alias)

        new_text = LINK_RE.sub(repl, text)
        if new_text != original_text and not dry_run:
            md_file.write_text(new_text, encoding="utf-8")

    return stats


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Repair Obsidian vault wiki links")
    parser.add_argument("--dry-run", action="store_true", help="Print changes without writing")
    args = parser.parse_args()
    stats = repair(dry_run=args.dry_run)
    print(stats)
