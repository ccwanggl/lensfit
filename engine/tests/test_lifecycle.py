"""Tests for FastAPI application lifecycle and repeated startup."""

from __future__ import annotations

from fastapi.testclient import TestClient

from optibench.api.server import app


def test_repeated_startup_in_same_process(tmp_path):
    """Shutdown must reset global state so a second lifespan can initialize."""
    db_path = tmp_path / "lifecycle.db"
    app.state.db_url = f"sqlite:///{db_path}"
    app.state.mode = "dev"

    # First startup
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["version"] == "1.1.0"
        resp = client.get("/api/v1/domains")
        assert resp.status_code == 200

    # Second startup in the same process must re-initialize successfully.
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        resp = client.get("/api/v1/domains")
        assert resp.status_code == 200
        assert len(resp.json()["items"]) == 4
