"""API tests for /api/v1/curriculum endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from optibench.api import server as server_module
from optibench.api.server import app
from optibench.curriculum import reset_curriculum_graph


@pytest.fixture
def client():
    """Create a TestClient with DB/API key patching (mirrors test_api_lab.py)."""
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    db_engine = sqlalchemy.create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    session_maker = sessionmaker(bind=db_engine)

    from optibench.db.models import Base

    Base.metadata.create_all(db_engine)  # curriculum graph 合并 learning_records

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


def test_get_curriculum_graph(client: TestClient):
    res = client.get("/api/v1/curriculum/graph")
    assert res.status_code == 200
    data = res.json()

    nodes = {n["id"]: n for n in data["nodes"]}
    # Coverage
    assert len([n for n in nodes.values() if n["kind"] == "experiment"]) == 34
    assert "single-slit-breadboard" in nodes
    assert "industrial" in nodes
    assert "cmos-fundamentals" in nodes
    # Phase 3: assessment nodes resolve against the quiz index.
    quiz_node = nodes["geo-optics-imaging-quiz"]
    assert quiz_node["kind"] == "assessment"
    assert quiz_node["ref"] == "geo-optics-imaging-quiz"
    assert quiz_node["module"] == "20-geometric-optics"

    # Node shape
    node = nodes["double-slit"]
    assert node["kind"] == "experiment"
    assert node["ref"] == "double-slit"
    assert node["module"] == "30-wave-optics"
    assert sorted(node["prerequisites"]) == ["polarization-malus", "single-slit-diffraction"]
    # Phase 2: empty learning_records → every node merges to not_started.
    assert all(n["status"] == "not_started" for n in nodes.values())

    # Edges mirror prerequisites (prereq -> dependent).
    edges = {(e["from_id"], e["to_id"]) for e in data["edges"]}
    assert ("single-slit-diffraction", "double-slit") in edges
    assert ("double-slit", "grating") in edges
    assert ("cmos-fundamentals", "cmos-spectral-response") in edges
    for from_id, to_id in edges:
        assert from_id in nodes and to_id in nodes
