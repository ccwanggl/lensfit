"""Audit Obsidian wiki links inside OpticKnowledgeSpace.

Reports broken internal links. Run from the repository root:

    python scripts/audit_vault_links.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE_SPLIT_RE = re.compile(r"(?<!\\)\|")


def load_index() -> dict:
    index = {"by_path": {}, "by_filename": {}, "by_title": {}, "by_alias": {}}
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


def normalize_link(raw: str) -> tuple[str, str | None]:
    temp = raw.replace("\\|", "|")
    parts = PIPE_SPLIT_RE.split(temp, 1)
    target = parts[0].strip().split("#", 1)[0].strip()
    alias = parts[1].strip() if len(parts) > 1 else None
    return target, alias


def resolve_target(source: Path, target: str, index: dict) -> Path | None:
    if not target:
        return None
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


def audit() -> int:
    index = load_index()
    broken: list[tuple[Path, int, str]] = []
    seen = set()

    for md_file in sorted(VAULT.rglob("*.md")):
        # Plugin-generated conversation files are not part of the knowledge graph.
        if "copilot/copilot-conversations" in str(md_file).replace("\\", "/"):
            continue
        lines = md_file.read_text(encoding="utf-8").splitlines()
        for line_no, line in enumerate(lines, start=1):
            for match in LINK_RE.finditer(line):
                raw = match.group(1)
                target, _ = normalize_link(raw)
                if resolve_target(md_file, target, index) is None:
                    key = (str(md_file), raw)
                    if key not in seen:
                        seen.add(key)
                        broken.append((md_file, line_no, raw))

    for src, line_no, raw in broken:
        print(f"{src.relative_to(VAULT.parent)}:{line_no}  [[{raw}]]")

    print(f"\nTotal unique broken links: {len(broken)}")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(audit())
