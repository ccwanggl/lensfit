"""Curriculum loader — parses and validates ``modules/curriculum.yaml``.

Schema spec: ``docs/development/specifications/lab/curriculum-graph.md``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml

NodeKind = Literal["concept", "experiment", "preset", "practice", "assessment"]
NODE_KINDS = ("concept", "experiment", "preset", "practice", "assessment")

_FILENAME = "curriculum.yaml"


class CurriculumError(ValueError):
    """Raised when the curriculum definition violates its schema or graph rules.

    The message always names the offending node / file.
    """


@dataclass
class CurriculumNode:
    id: str
    kind: NodeKind
    ref: str
    title: str
    module: str = ""
    prerequisites: list[str] = field(default_factory=list)


def resolve_curriculum_path() -> Path:
    """Resolve ``curriculum.yaml`` for the current runtime.

    Resolution order mirrors ``optibench.content.loader.resolve_modules_root``:
    ``OPTIBENCH_MODULES_DIR`` → PyInstaller ``sys._MEIPASS/modules`` → source
    checkout ``<repo root>/modules``.
    """
    env = os.environ.get("OPTIBENCH_MODULES_DIR")
    if env:
        return Path(env) / _FILENAME
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass) / "modules" / _FILENAME
    return Path(__file__).resolve().parents[3] / "modules" / _FILENAME


def _validate_node(raw: object, source: Path | str, index: int) -> CurriculumNode:
    where = f"{source}: nodes[{index}]"
    if not isinstance(raw, dict):
        raise CurriculumError(f"{where}: 节点必须是 YAML 映射")
    for field_name in ("id", "kind", "ref", "title"):
        if field_name not in raw:
            raise CurriculumError(f"{where}: 缺少必需字段 '{field_name}'")
        value = raw[field_name]
        if not isinstance(value, str) or not value.strip():
            raise CurriculumError(f"{where}: 字段 '{field_name}' 必须是非空字符串")
    kind = raw["kind"]
    if kind not in NODE_KINDS:
        raise CurriculumError(
            f"{where}: 字段 'kind' 取值非法：{kind!r}，合法取值为 {'/'.join(NODE_KINDS)}"
        )
    prerequisites = raw.get("prerequisites", [])
    if not isinstance(prerequisites, list) or not all(isinstance(x, str) for x in prerequisites):
        raise CurriculumError(f"{where}: 字段 'prerequisites' 必须是字符串列表（可为空列表 []）")
    module = raw.get("module", "")
    if not isinstance(module, str):
        raise CurriculumError(f"{where}: 字段 'module' 必须是字符串")
    return CurriculumNode(
        id=raw["id"],
        kind=kind,
        ref=raw["ref"],
        title=raw["title"],
        module=module,
        prerequisites=list(prerequisites),
    )


def load_curriculum(path: Path) -> list[CurriculumNode]:
    """Load and schema-validate ``curriculum.yaml``.

    Checks: file exists, top-level ``nodes`` list, per-node required fields,
    ``kind`` enum, unique node ids, and that every prerequisite references a
    node defined in the same file (dangling prerequisite → error).
    """
    if not path.is_file():
        raise CurriculumError(f"curriculum 定义文件不存在：{path}")
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        raise CurriculumError(f"{path}: 不是合法 YAML：{e}") from e
    if not isinstance(data, dict) or not isinstance(data.get("nodes"), list):
        raise CurriculumError(f"{path}: 顶层必须是包含 'nodes' 列表的映射")

    nodes = [_validate_node(raw, path.name, i) for i, raw in enumerate(data["nodes"])]

    ids: set[str] = set()
    for node in nodes:
        if node.id in ids:
            raise CurriculumError(f"{path.name}: 节点 id {node.id!r} 重复")
        ids.add(node.id)
    for node in nodes:
        for prereq in node.prerequisites:
            if prereq not in ids:
                raise CurriculumError(
                    f"{path.name}: 节点 {node.id!r} 的先修 {prereq!r} 未定义（悬空先修）"
                )
    return nodes
