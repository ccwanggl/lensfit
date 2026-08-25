"""API tests for /api/v1/learning endpoints and curriculum status merge."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from optibench.api import server as server_module
from optibench.api.server import app
from optibench.curriculum import reset_curriculum_graph


@pytest.fixture
def client():
    """TestClient with in-memory DB (tables created directly; migrations are
    covered separately in test_learning_records.py)."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from optibench.db.models import Base

    db_engine = sqlalchemy.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(db_engine)
    session_maker = sessionmaker(bind=db_engine)

    original_session_maker = getattr(server_module, "_session_maker", None)
    original_engine = getattr(server_module, "_engine", None)
    original_api_key = getattr(server_module, "_API_KEY", None)

    server_module._session_maker = session_maker
    server_module._engine = None
    server_module._API_KEY = "test-key"

    app.state.mode = "dev"  # bypass API key verification

    reset_curriculum_graph()
    with TestClient(app) as c:
        yield c
    reset_curriculum_graph()

    server_module._session_maker = original_session_maker
    server_module._engine = original_engine
    server_module._API_KEY = original_api_key


def test_put_then_get_progress(client: TestClient):
    res = client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "experiment", "item_id": "thin-lens", "status": "completed"},
    )
    assert res.status_code == 200
    item = res.json()
    assert item["learner_id"] == "default"
    assert item["item_id"] == "thin-lens"
    assert item["status"] == "completed"
    assert item["score"] is None
    assert item["updated_at"]

    res = client.get("/api/v1/learning/progress")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) == 1
    assert items[0]["item_id"] == "thin-lens"


def test_put_upserts_existing_record(client: TestClient):
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "concept", "item_id": "cmos-fundamentals", "status": "viewed"},
    )
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "concept", "item_id": "cmos-fundamentals", "status": "completed"},
    )
    items = client.get("/api/v1/learning/progress").json()["items"]
    assert len(items) == 1
    assert items[0]["status"] == "completed"


def test_get_progress_filters_by_item_kind(client: TestClient):
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "experiment", "item_id": "thin-lens", "status": "completed"},
    )
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "concept", "item_id": "cmos-fundamentals", "status": "viewed"},
    )
    items = client.get("/api/v1/learning/progress?item_kind=experiment").json()["items"]
    assert [i["item_id"] for i in items] == ["thin-lens"]


def test_scored_record_keeps_score(client: TestClient):
    res = client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "quiz", "item_id": "foundations-1", "status": "scored", "score": 0.8},
    )
    assert res.status_code == 200
    assert res.json()["score"] == 0.8


def test_score_rejected_for_non_scored_status(client: TestClient):
    res = client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "experiment", "item_id": "thin-lens", "status": "viewed", "score": 1.0},
    )
    assert res.status_code == 422


def test_curriculum_graph_merges_learning_status(client: TestClient):
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "experiment", "item_id": "thin-lens", "status": "completed"},
    )
    client.put(
        "/api/v1/learning/progress",
        json={"item_kind": "concept", "item_id": "cmos-fundamentals", "status": "viewed"},
    )
    res = client.get("/api/v1/curriculum/graph")
    assert res.status_code == 200
    nodes = {n["id"]: n for n in res.json()["nodes"]}
    assert nodes["thin-lens"]["status"] == "completed"
    assert nodes["cmos-fundamentals"]["status"] == "viewed"
    assert nodes["double-slit"]["status"] == "not_started"
