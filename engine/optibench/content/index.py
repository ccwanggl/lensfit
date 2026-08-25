"""Read-only content index built by scanning ``modules/**/*.md``.

Only files at ``modules/<module>/learning/*.md`` are treated as concept
documents and validated against the content contract; every other markdown
file (module READMEs, ``projects/``, ``assessment/``) is skipped. No database
tables — the index is a plain in-memory map built at startup.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from optibench.content.contract import (
    ConceptMeta,
    ContractError,
    split_frontmatter,
    validate_concept,
)

logger = logging.getLogger(__name__)


@dataclass
class IndexError:
    """A contract violation collected during index build."""

    path: str
    error: str


@dataclass
class ContentIndex:
    """Read-only index: concept id -> metadata + body file path."""

    root: Path
    entries: dict[str, ConceptMeta] = field(default_factory=dict)
    bodies: dict[str, Path] = field(default_factory=dict)
    errors: list[IndexError] = field(default_factory=list)

    @classmethod
    def build(cls, root: Path, strict: bool = False) -> ContentIndex:
        """Scan ``root`` and build the index.

        With ``strict=True`` the first contract violation raises
        :class:`ContractError`; otherwise violations are collected into
        ``index.errors`` and the offending files are skipped.
        """
        index = cls(root=root)
        if not root.is_dir():
            logger.warning("content modules root does not exist: %s", root)
            return index

        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(root)
            parts = rel.parts
            # Only modules/<module>/learning/<name>.md are concept docs.
            if len(parts) != 3 or parts[1] != "learning":
                continue
            try:
                text = path.read_text(encoding="utf-8")
                data, _body = split_frontmatter(text, rel)
                meta = validate_concept(data, rel)
                if meta.module != parts[0]:
                    raise ContractError(
                        f"{rel}: 字段 'module' 取值 {meta.module!r} "
                        f"与所在模块目录 {parts[0]!r} 不一致"
                    )
                if meta.id in index.entries:
                    raise ContractError(
                        f"{rel}: 概念 id {meta.id!r} 重复，"
                        f"与 {index.bodies[meta.id].relative_to(root)} 冲突"
                    )
            except ContractError as e:
                if strict:
                    raise
                index.errors.append(IndexError(path=str(rel), error=str(e)))
                logger.warning("content index skipped %s: %s", rel, e)
                continue
            index.entries[meta.id] = meta
            index.bodies[meta.id] = path
        return index

    def list_concepts(self) -> list[ConceptMeta]:
        return list(self.entries.values())

    def get(self, concept_id: str) -> ConceptMeta | None:
        return self.entries.get(concept_id)

    def get_body(self, concept_id: str) -> str | None:
        path = self.bodies.get(concept_id)
        if path is None:
            return None
        text = path.read_text(encoding="utf-8")
        _data, body = split_frontmatter(text, path)
        return body
