"""Tests for matching engine."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from lensfit.db.models import Base
from lensfit.domains.base import Requirements
from lensfit.domains.industrial import IndustrialVisionModule
from lensfit.matching.engine import MatchingEngine


class TestMatchingEngine:
    @pytest.fixture
    def engine(self):
        db_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(db_engine)
        session_factory = sessionmaker(bind=db_engine)
        e = MatchingEngine(session_factory)
        e.register_domain(IndustrialVisionModule())
        return e

    def test_register_domain(self, engine):
        assert "industrial" in engine.domains
        domain = engine.get_domain("industrial")
        assert domain.domain_id == "industrial"

    def test_unknown_domain_raises(self, engine):
        with pytest.raises(ValueError):
            engine.get_domain("unknown")

    def test_match_async_creates_task(self, engine):
        reqs = Requirements(domain="industrial", params={})
        task = engine.match_async(reqs)
        assert task.task_id is not None
        assert task.status in ("pending", "running", "failed")
        assert task.task_id in engine._tasks
