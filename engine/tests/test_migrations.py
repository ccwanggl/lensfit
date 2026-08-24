"""Smoke tests for Alembic migrations."""

from __future__ import annotations

import importlib
import pkgutil
import tempfile
from pathlib import Path

from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

import optibench.db.migrations
import optibench.db.migrations.versions
from optibench.db.models import init_db


def test_all_version_modules_are_importable() -> None:
    """Every migration module under optibench.db.migrations.versions can be imported."""
    versions_package = optibench.db.migrations.versions
    prefix = versions_package.__name__ + "."
    modules = [name for _, name, _ in pkgutil.iter_modules(versions_package.__path__, prefix)]
    assert modules, "expected at least one version module"
    for module_name in modules:
        importlib.import_module(module_name)


def test_upgrade_to_head_sets_latest_alembic_version() -> None:
    """Upgrading a fresh SQLite database to head sets the expected revision."""
    migrations_dir = Path(optibench.db.migrations.__file__).parent
    script_dir = ScriptDirectory(str(migrations_dir))

    head_revision = script_dir.get_current_head()
    assert head_revision is not None, "expected a head revision"

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    try:
        url = f"sqlite:///{db_path}"

        # init_db uses Alembic and explicitly disposes the engine afterwards,
        # avoiding the ResourceWarnings caused by leaving Alembic's engine open.
        init_db(url)

        engine = create_engine(url, connect_args={"check_same_thread": False})
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                row = result.fetchone()
                assert row is not None, "alembic_version table is empty"
                assert row[0] == head_revision
        finally:
            engine.dispose()
    finally:
        Path(db_path).unlink(missing_ok=True)
