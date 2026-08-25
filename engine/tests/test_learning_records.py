"""Tests for the learning_records table migration (004) and model."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.pool import NullPool

import optibench.db.migrations


def _alembic_cfg(url: str) -> Config:
    engine_dir = Path(optibench.db.migrations.__file__).parent.parent.parent.parent
    cfg = Config(str(engine_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(engine_dir / "optibench" / "db" / "migrations"))
    cfg.set_main_option("sqlalchemy.url", url)
    return cfg


def _run(cfg: Config, url: str, fn) -> None:
    engine = create_engine(url, connect_args={"check_same_thread": False}, poolclass=NullPool)
    with engine.connect() as conn:
        cfg.attributes["connection"] = conn
        fn(cfg)
    engine.dispose()


def _table_names(url: str) -> set[str]:
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            return {
                r[0]
                for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            }
    finally:
        engine.dispose()


@pytest.fixture
def db_url():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    yield f"sqlite:///{db_path}"
    Path(db_path).unlink(missing_ok=True)


def test_upgrade_creates_learning_records(db_url: str) -> None:
    cfg = _alembic_cfg(db_url)
    _run(cfg, db_url, lambda c: command.upgrade(c, "head"))
    assert "learning_records" in _table_names(db_url)

    engine = create_engine(db_url)
    try:
        with engine.connect() as conn:
            cols = [r[1] for r in conn.execute(text("PRAGMA table_info(learning_records)"))]
            assert cols == [
                "id",
                "learner_id",
                "item_kind",
                "item_id",
                "status",
                "score",
                "updated_at",
            ]
            assert conn.execute(text("SELECT version_num FROM alembic_version")).scalar() == "004"
    finally:
        engine.dispose()


def test_downgrade_drops_and_reupgrade_restores(db_url: str) -> None:
    cfg = _alembic_cfg(db_url)
    _run(cfg, db_url, lambda c: command.upgrade(c, "head"))
    _run(cfg, db_url, lambda c: command.downgrade(c, "0ac6c641b5d7"))
    assert "learning_records" not in _table_names(db_url)

    _run(cfg, db_url, lambda c: command.upgrade(c, "head"))
    assert "learning_records" in _table_names(db_url)
