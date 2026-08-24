"""Tests for catalog import resource limits."""

import io

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from optibench.api.server import app
from optibench.db.models import Base

TEST_API_KEY = "test-api-key"


@pytest.fixture
def client():
    """Create a test client with an in-memory database."""
    db_url = "sqlite:///:memory:"
    engine = create_engine(
        db_url,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)

    import optibench.api.server as server_module

    server_module._session_maker = session_factory
    server_module._API_KEY = TEST_API_KEY

    with TestClient(app) as c:
        yield c

    server_module._session_maker = None
    server_module._engine = None
    engine.dispose()


@pytest.fixture
def auth_headers():
    """Return API key headers for authenticated requests."""
    return {"X-API-Key": TEST_API_KEY}


_CSV_HEADERS = (
    "manufacturer_name,model,category,focal_length_mm,max_aperture,"
    "image_circle_mm,mount_type,nominal_wd_mm,price_usd\n"
)


def test_import_oversized_file_rejected(client, auth_headers):
    """A file larger than 5 MB is rejected with HTTP 413."""
    oversized = b"a" * (5 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/v1/catalog/import",
        files={"file": ("lenses_import.csv", io.BytesIO(oversized), "text/csv")},
        headers=auth_headers,
    )
    assert resp.status_code == 413
    assert "exceeds maximum" in resp.json()["detail"]


def test_import_disallowed_extension_rejected(client, auth_headers):
    """A file with an unsupported extension is rejected with HTTP 400."""
    resp = client.post(
        "/api/v1/catalog/import",
        files={"file": ("lenses_import.txt", io.BytesIO(b"not a valid file"), "text/plain")},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert "Unsupported file extension" in resp.json()["detail"]


def test_import_excel_too_many_rows_rejected(client, auth_headers):
    """An Excel sheet with more than 10,000 data rows is rejected with HTTP 413."""
    wb = Workbook()
    ws = wb.active
    ws.append(["model", "category"])
    for i in range(10001):
        ws.append([f"Lens-{i}", "industrial"])
    xlsx_bytes = io.BytesIO()
    wb.save(xlsx_bytes)
    xlsx_bytes.seek(0)

    resp = client.post(
        "/api/v1/catalog/import",
        files={
            "file": (
                "lenses_import.xlsx",
                xlsx_bytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
        headers=auth_headers,
    )
    assert resp.status_code == 413
    assert "exceeds maximum" in resp.json()["detail"]


def test_import_valid_csv_still_works(client, auth_headers):
    """Ensure existing CSV import logic is preserved after adding limits."""
    csv_content = (
        _CSV_HEADERS
        + "ImportMfg,IM-35mm,industrial,35,2.8,17,C,150,399\n"
        + "ImportMfg,IM-50mm,industrial,50,2.8,22,C,200,499\n"
    )
    resp = client.post(
        "/api/v1/catalog/import",
        files={
            "file": ("lenses_import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["kind"] == "lenses"
    assert data["inserted"] == 2
    assert data["skipped"] == 0
