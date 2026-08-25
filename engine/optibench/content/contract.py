"""Content contract v1 — frontmatter schema validation for module concept docs.

Implements the contract defined in
``docs/development/specifications/lab/content-contract.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError

Difficulty = Literal["foundation", "intermediate", "advanced"]
Status = Literal["draft", "published"]

DIFFICULTY_VALUES = ("foundation", "intermediate", "advanced")
STATUS_VALUES = ("draft", "published")

REQUIRED_FIELDS = (
    "id",
    "title",
    "module",
    "difficulty",
    "prerequisites",
    "linked_experiments",
    "status",
)


class ContractError(ValueError):
    """Raised when a concept document violates the content contract.

    The message always names the source file and the offending field(s).
    """


class ConceptMeta(BaseModel):
    """Metadata of a single concept document (frontmatter, without body)."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    module: str
    difficulty: Difficulty
    prerequisites: list[str]
    linked_experiments: list[str]
    status: Status


def split_frontmatter(text: str, source: Path | str) -> tuple[dict[str, Any], str]:
    """Split a markdown document into (frontmatter dict, body).

    Raises :class:`ContractError` when the frontmatter block is missing,
    unterminated, not valid YAML, or not a mapping.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ContractError(f"{source}: 缺少 frontmatter（文件第一行必须是 '---'）")
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        raise ContractError(f"{source}: frontmatter 未闭合（缺少结束的 '---' 行）")
    raw = "\n".join(lines[1:end])
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as e:
        raise ContractError(f"{source}: frontmatter 不是合法 YAML：{e}") from e
    if not isinstance(data, dict):
        raise ContractError(f"{source}: frontmatter 必须是 YAML 映射（key: value）")
    body = "\n".join(lines[end + 1 :]).lstrip("\n")
    return data, body


def validate_concept(data: dict[str, Any], source: Path | str) -> ConceptMeta:
    """Validate a frontmatter dict against the content contract v1.

    Raises :class:`ContractError` with an explicit message on any violation.
    """
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ContractError(f"{source}: 缺少必需字段：{', '.join(missing)}")

    for field in ("id", "title", "module"):
        value = data[field]
        if not isinstance(value, str) or not value.strip():
            raise ContractError(f"{source}: 字段 '{field}' 必须是非空字符串")

    difficulty = data["difficulty"]
    if difficulty not in DIFFICULTY_VALUES:
        raise ContractError(
            f"{source}: 字段 'difficulty' 取值非法：{difficulty!r}，"
            f"合法取值为 {'/'.join(DIFFICULTY_VALUES)}"
        )
    status = data["status"]
    if status not in STATUS_VALUES:
        raise ContractError(
            f"{source}: 字段 'status' 取值非法：{status!r}，"
            f"合法取值为 {'/'.join(STATUS_VALUES)}"
        )

    for field in ("prerequisites", "linked_experiments"):
        value = data[field]
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ContractError(f"{source}: 字段 '{field}' 必须是字符串列表（可为空列表 []）")

    try:
        return ConceptMeta.model_validate(data)
    except ValidationError as e:  # defensive: manual checks above should catch everything
        raise ContractError(f"{source}: frontmatter 校验失败：{e}") from e


def parse_concept_file(path: Path) -> tuple[ConceptMeta, str]:
    """Parse and validate a concept markdown file. Returns (metadata, body)."""
    text = path.read_text(encoding="utf-8")
    data, body = split_frontmatter(text, path)
    meta = validate_concept(data, path)
    return meta, body
