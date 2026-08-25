"""Tests for the quiz loader and /api/v1/content/quizzes endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from optibench.api import server as server_module
from optibench.api.server import app
from optibench.content.loader import reset_content_index, resolve_modules_root
from optibench.content.quiz import QuizError, QuizIndex, reset_quiz_index

# ─── Loader: real modules root ───


def test_quiz_index_loads_real_modules():
    index = QuizIndex.build(resolve_modules_root())
    assert index.errors == []
    ids = {q.id for q in index.list_quizzes()}
    assert "geo-optics-imaging-quiz" in ids
    assert "cmos-fundamentals-quiz" in ids

    quiz = index.get("geo-optics-imaging-quiz")
    assert quiz is not None
    assert quiz.module == "20-geometric-optics"
    assert quiz.pass_score == 80
    assert len(quiz.questions) == 8
    for q in quiz.questions:
        assert 0 <= q.correct_index < len(q.options)

    # 概念联动：cmos-fundamentals 教程挂载点
    linked = index.for_concept("cmos-fundamentals")
    assert [q.id for q in linked] == ["cmos-fundamentals-quiz"]
    assert index.for_concept("no-such-concept") == []


# ─── Loader: invalid fixtures on tmp_path ───


def _write(tmp_path, module: str, body: str):
    d = tmp_path / module / "assessment"
    d.mkdir(parents=True)
    (d / "quiz.yaml").write_text(body, encoding="utf-8")


VALID = """
quizzes:
  - id: q1
    title: 测验一
    module: m1
    questions:
      - question: 1+1=?
        options: ["1", "2"]
        correct_index: 1
"""


def test_quiz_index_tmp_root_valid(tmp_path):
    _write(tmp_path, "m1", VALID)
    index = QuizIndex.build(tmp_path)
    assert index.errors == []
    quiz = index.get("q1")
    assert quiz is not None
    assert quiz.pass_score == 80  # 默认值
    assert quiz.questions[0].explanation == ""  # 可选字段默认空串


@pytest.mark.parametrize(
    "body, fragment",
    [
        # 顶层缺 quizzes 列表
        ("quizzes: {}", "quizzes"),
        # 缺必需字段
        ("quizzes:\n  - id: q1\n    title: t\n", "缺少必需字段"),
        # module 与目录不一致
        (
            "quizzes:\n  - id: q1\n    title: t\n    module: other\n"
            "    questions:\n      - question: x\n        options: [a, b]\n"
            "        correct_index: 0\n",
            "与所在模块目录",
        ),
        # correct_index 越界
        (
            "quizzes:\n  - id: q1\n    title: t\n    module: m1\n"
            "    questions:\n      - question: x\n        options: [a, b]\n"
            "        correct_index: 2\n",
            "越界",
        ),
        # options 少于 2 项
        (
            "quizzes:\n  - id: q1\n    title: t\n    module: m1\n"
            "    questions:\n      - question: x\n        options: [a]\n"
            "        correct_index: 0\n",
            "至少 2 个",
        ),
        # pass_score 越界
        (
            "quizzes:\n  - id: q1\n    title: t\n    module: m1\n    pass_score: 120\n"
            "    questions:\n      - question: x\n        options: [a, b]\n"
            "        correct_index: 0\n",
            "0-100",
        ),
        # 非法 YAML
        ("quizzes: [unclosed", "YAML"),
    ],
)
def test_quiz_index_collects_errors(tmp_path, body, fragment):
    _write(tmp_path, "m1", body)
    index = QuizIndex.build(tmp_path)
    assert index.entries == {}
    assert len(index.errors) == 1
    assert fragment in index.errors[0].error
    assert index.errors[0].path.endswith("quiz.yaml")


def test_quiz_index_strict_raises(tmp_path):
    _write(tmp_path, "m1", "quizzes: {}")
    with pytest.raises(QuizError):
        QuizIndex.build(tmp_path, strict=True)


def test_quiz_index_duplicate_id(tmp_path):
    _write(tmp_path, "m1", VALID)
    _write(tmp_path, "m2", VALID.replace("module: m1", "module: m2"))
    index = QuizIndex.build(tmp_path)
    assert len(index.errors) == 1
    assert "重复" in index.errors[0].error


# ─── API ───


@pytest.fixture
def client():
    """Create a TestClient with DB/API key patching (mirrors test_api_content.py)."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    db_engine = sqlalchemy.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_maker = sessionmaker(bind=db_engine)

    original_session_maker = getattr(server_module, "_session_maker", None)
    original_engine = getattr(server_module, "_engine", None)
    original_api_key = getattr(server_module, "_API_KEY", None)

    server_module._session_maker = session_maker
    server_module._engine = None
    server_module._API_KEY = "test-key"

    app.state.mode = "dev"  # bypass API key verification

    reset_content_index()
    reset_quiz_index()
    with TestClient(app) as c:
        yield c
    reset_content_index()
    reset_quiz_index()

    server_module._session_maker = original_session_maker
    server_module._engine = original_engine
    server_module._API_KEY = original_api_key


def test_list_quizzes(client: TestClient):
    res = client.get("/api/v1/content/quizzes")
    assert res.status_code == 200
    data = res.json()
    assert data["errors"] == []
    ids = {item["id"] for item in data["items"]}
    assert "geo-optics-imaging-quiz" in ids
    assert "cmos-fundamentals-quiz" in ids
    item = next(i for i in data["items"] if i["id"] == "geo-optics-imaging-quiz")
    assert item["module"] == "20-geometric-optics"
    assert len(item["questions"]) == 8
    q0 = item["questions"][0]
    assert set(q0) == {"question", "options", "correct_index", "explanation"}


def test_list_quizzes_filter_by_concept(client: TestClient):
    res = client.get("/api/v1/content/quizzes", params={"concept": "cmos-fundamentals"})
    assert res.status_code == 200
    items = res.json()["items"]
    assert [i["id"] for i in items] == ["cmos-fundamentals-quiz"]


def test_get_quiz_detail_and_404(client: TestClient):
    res = client.get("/api/v1/content/quizzes/cmos-fundamentals-quiz")
    assert res.status_code == 200
    data = res.json()
    assert data["concepts"] == ["cmos-fundamentals"]
    assert len(data["questions"]) == 4

    res = client.get("/api/v1/content/quizzes/no-such-quiz")
    assert res.status_code == 404
