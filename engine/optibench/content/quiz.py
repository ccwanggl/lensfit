"""Quiz loader — scans ``modules/<module>/assessment/quiz.yaml``.

Spec: ``docs/development/specifications/lab/assessment-quizzes.md``.

Mirrors the concept content index: a read-only in-memory map built at
startup, no database tables. Invalid quizzes are collected into
``QuizIndex.errors`` (or raise immediately with ``strict=True``).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_FILENAME = "quiz.yaml"


class QuizError(ValueError):
    """Raised when a quiz definition violates its schema.

    The message always names the source file and the offending quiz/field.
    """


@dataclass
class QuizQuestion:
    question: str
    options: list[str]
    correct_index: int
    explanation: str = ""


@dataclass
class Quiz:
    id: str
    title: str
    module: str
    concepts: list[str] = field(default_factory=list)
    pass_score: int = 80
    questions: list[QuizQuestion] = field(default_factory=list)


@dataclass
class QuizIndexError:
    """A schema violation collected during index build."""

    path: str
    error: str


def _validate_question(raw: object, where: str) -> QuizQuestion:
    if not isinstance(raw, dict):
        raise QuizError(f"{where}: 题目必须是 YAML 映射")
    question = raw.get("question")
    if not isinstance(question, str) or not question.strip():
        raise QuizError(f"{where}: 字段 'question' 必须是非空字符串")
    options = raw.get("options")
    if (
        not isinstance(options, list)
        or len(options) < 2
        or not all(isinstance(o, str) and o.strip() for o in options)
    ):
        raise QuizError(f"{where}: 字段 'options' 必须是至少 2 个非空字符串的列表")
    correct_index = raw.get("correct_index")
    if not isinstance(correct_index, int) or isinstance(correct_index, bool):
        raise QuizError(f"{where}: 字段 'correct_index' 必须是整数")
    if not 0 <= correct_index < len(options):
        raise QuizError(
            f"{where}: 字段 'correct_index' 取值 {correct_index} 越界"
            f"（options 共 {len(options)} 项）"
        )
    explanation = raw.get("explanation", "")
    if not isinstance(explanation, str):
        raise QuizError(f"{where}: 字段 'explanation' 必须是字符串")
    return QuizQuestion(
        question=question,
        options=list(options),
        correct_index=correct_index,
        explanation=explanation,
    )


def _validate_quiz(raw: object, source: Path | str, index: int, module_dir: str) -> Quiz:
    where = f"{source}: quizzes[{index}]"
    if not isinstance(raw, dict):
        raise QuizError(f"{where}: 测验必须是 YAML 映射")
    for field_name in ("id", "title", "module", "questions"):
        if field_name not in raw:
            raise QuizError(f"{where}: 缺少必需字段 '{field_name}'")
    for field_name in ("id", "title", "module"):
        value = raw[field_name]
        if not isinstance(value, str) or not value.strip():
            raise QuizError(f"{where}: 字段 '{field_name}' 必须是非空字符串")
    if raw["module"] != module_dir:
        raise QuizError(
            f"{where}: 字段 'module' 取值 {raw['module']!r} "
            f"与所在模块目录 {module_dir!r} 不一致"
        )
    concepts = raw.get("concepts", [])
    if not isinstance(concepts, list) or not all(isinstance(c, str) for c in concepts):
        raise QuizError(f"{where}: 字段 'concepts' 必须是字符串列表（可为空列表 []）")
    pass_score = raw.get("pass_score", 80)
    if (
        not isinstance(pass_score, int)
        or isinstance(pass_score, bool)
        or not 0 <= pass_score <= 100
    ):
        raise QuizError(f"{where}: 字段 'pass_score' 必须是 0-100 的整数")
    questions_raw = raw["questions"]
    if not isinstance(questions_raw, list) or not questions_raw:
        raise QuizError(f"{where}: 字段 'questions' 必须是非空列表")
    questions = [
        _validate_question(q, f"{where}.questions[{i}]")
        for i, q in enumerate(questions_raw)
    ]
    return Quiz(
        id=raw["id"],
        title=raw["title"],
        module=raw["module"],
        concepts=list(concepts),
        pass_score=pass_score,
        questions=questions,
    )


@dataclass
class QuizIndex:
    """Read-only index: quiz id -> quiz definition."""

    root: Path
    entries: dict[str, Quiz] = field(default_factory=dict)
    errors: list[QuizIndexError] = field(default_factory=list)

    @classmethod
    def build(cls, root: Path, strict: bool = False) -> QuizIndex:
        """Scan ``root/<module>/assessment/quiz.yaml`` and build the index.

        With ``strict=True`` the first violation raises :class:`QuizError`;
        otherwise violations are collected into ``index.errors`` and the
        offending files are skipped.
        """
        index = cls(root=root)
        if not root.is_dir():
            logger.warning("content modules root does not exist: %s", root)
            return index

        for path in sorted(root.glob(f"*/assessment/{_FILENAME}")):
            rel = path.relative_to(root)
            module_dir = rel.parts[0]
            try:
                try:
                    data = yaml.safe_load(path.read_text(encoding="utf-8"))
                except yaml.YAMLError as e:
                    raise QuizError(f"{rel}: 不是合法 YAML：{e}") from e
                if not isinstance(data, dict) or not isinstance(data.get("quizzes"), list):
                    raise QuizError(f"{rel}: 顶层必须是包含 'quizzes' 列表的映射")
                for i, raw in enumerate(data["quizzes"]):
                    quiz = _validate_quiz(raw, rel, i, module_dir)
                    if quiz.id in index.entries:
                        raise QuizError(f"{rel}: 测验 id {quiz.id!r} 重复")
                    index.entries[quiz.id] = quiz
            except QuizError as e:
                if strict:
                    raise
                index.errors.append(QuizIndexError(path=str(rel), error=str(e)))
                logger.warning("quiz index skipped %s: %s", rel, e)
                continue
        return index

    def list_quizzes(self) -> list[Quiz]:
        return list(self.entries.values())

    def get(self, quiz_id: str) -> Quiz | None:
        return self.entries.get(quiz_id)

    def for_concept(self, concept_id: str) -> list[Quiz]:
        """Quizzes linked to a concept (tutorial-view mount point)."""
        return [q for q in self.entries.values() if concept_id in q.concepts]


_INDEX: QuizIndex | None = None


def get_quiz_index() -> QuizIndex:
    """Return the shared quiz index, building it on first access."""
    global _INDEX
    if _INDEX is None:
        from optibench.content.loader import resolve_modules_root

        _INDEX = QuizIndex.build(resolve_modules_root())
    return _INDEX


def reset_quiz_index() -> None:
    """Drop the cached index (used by tests)."""
    global _INDEX
    _INDEX = None
