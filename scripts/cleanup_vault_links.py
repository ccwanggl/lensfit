"""Clean up malformed Obsidian wiki links created by earlier repair runs.

Usage from repo root:

    python scripts/cleanup_vault_links.py
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

VAULT = Path("OpticKnowledgeSpace")
LINK_RE = re.compile(r"(?<!\!)\[\[([^\]]+)\]\]")
PIPE_SPLIT_RE = re.compile(r"(?<!\\)\|")

TOP_FOLDERS = {"00-inbox", "10-concepts", "20-formulas", "30-domains", "40-devices",
               "50-learning", "80-sources", "90-maps", "attachments", "copilot", "templates"}

SLUG_FIXES = {
    "50-learning/12-optical-transfer-function": "50-learning/12-otf-and-image-quality",
    "50-learning/13-lighting-design": "50-learning/13-illumination-design",
    "50-learning/13-illumination-system-design": "50-learning/13-illumination-design",
}


def normalize_link(raw: str) -> tuple[str, str | None]:
    temp = raw.replace("\\|", "|")
    parts = PIPE_SPLIT_RE.split(temp, 1)
    target = parts[0].strip().split("#", 1)[0].strip().replace("\\", "/")
    alias = parts[1].strip() if len(parts) > 1 else None
    return target, alias


def clean_target(target: str, source: Path) -> str:
    """Remove duplicated leading folder segments and fix known wrong slugs."""
    # Remove accidental duplicated top-level prefixes such as
    # 10-concepts/10-concepts/50-learning/... -> 50-learning/...
    parts = target.split("/")
    while len(parts) >= 2 and parts[0] == parts[1] and parts[0] in TOP_FOLDERS:
        # If after removing one duplicate we still have a valid top folder,
        # keep stripping until we reach a different top folder or a single folder.
        if len(parts) >= 3 and parts[2] in TOP_FOLDERS:
            parts = parts[2:]
        else:
            break

    # Also strip a single leading source-folder duplicate when it is followed by
    # another top-level folder, e.g. 10-concepts/50-learning/... -> 50-learning/...
    source_folder = source.parent.name
    if len(parts) >= 2 and parts[0] == source_folder and parts[1] in TOP_FOLDERS:
        parts = parts[1:]

    cleaned = "/".join(parts)

    # Fix known renamed/misspelled chapter slugs.
    if cleaned in SLUG_FIXES:
        cleaned = SLUG_FIXES[cleaned]

    return cleaned


def make_link(target: str, alias: str | None) -> str:
    if alias and alias != target:
        return f"[[{target}|{alias}]]"
    return f"[[{target}]]"


def cleanup() -> dict:
    stats = {"rewritten": 0, "files_changed": 0}

    for md_file in sorted(VAULT.rglob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        original = text

        def repl(match: re.Match) -> str:
            raw = match.group(1)
            target, alias = normalize_link(raw)
            cleaned = clean_target(target, md_file)
            # Normalize backslashes to forward slashes even if that is the only change.
            final = cleaned
            if final != raw.replace("\\|", "|"):
                stats["rewritten"] += 1
                return make_link(final, alias)
            return match.group(0)

        new_text = LINK_RE.sub(repl, text)
        if new_text != original:
            md_file.write_text(new_text, encoding="utf-8")
            stats["files_changed"] += 1

    # Delete nested stub directories created by the buggy repair run.
    deleted_dirs = 0
    for folder in TOP_FOLDERS:
        nested = VAULT / folder / folder
        if nested.exists() and nested.is_dir():
            shutil.rmtree(nested)
            deleted_dirs += 1
    stats["deleted_nested_dirs"] = deleted_dirs

    return stats


if __name__ == "__main__":
    import sys
    stats = cleanup()
    print(stats)
    sys.exit(0)
