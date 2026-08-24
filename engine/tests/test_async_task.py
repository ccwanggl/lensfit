"""Tests for asynchronous matching task lifecycle."""

from __future__ import annotations

import threading
import time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from optibench.db.models import Base, DetectorCatalog, LensCatalog, Manufacturer
from optibench.domains.base import Requirements
from optibench.domains.industrial import IndustrialVisionModule
from optibench.matching.engine import MatchingEngine


def _build_engine_with_catalog() -> MatchingEngine:
    db_engine = create_engine(
        "sqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(db_engine)
    session_factory = sessionmaker(bind=db_engine)

    with session_factory() as session:
        mfg = Manufacturer(name="TestMfg")
        session.add(mfg)
        session.flush()

        for i in range(200):
            session.add(
                LensCatalog(
                    manufacturer_id=mfg.id,
                    model=f"Lens-{i}",
                    category="FA",
                    focal_length_mm=25.0,
                    image_circle_mm=15.0,
                    price_usd=100.0,
                )
            )
        for i in range(100):
            session.add(
                DetectorCatalog(
                    manufacturer_id=mfg.id,
                    model=f"Det-{i}",
                    category="area_scan_cmos",
                    sensor_w_mm=6.0,
                    sensor_h_mm=4.0,
                    sensor_diag_mm=7.0,
                    pixel_size_um=3.0,
                    resolution_w=1000,
                    resolution_h=1000,
                    price_usd=200.0,
                )
            )
        session.commit()

    engine = MatchingEngine(session_factory)
    engine.register_domain(IndustrialVisionModule())
    return engine, db_engine


@pytest.fixture
def engine():
    engine, db_engine = _build_engine_with_catalog()
    try:
        yield engine
    finally:
        engine.shutdown()
        db_engine.dispose()


class TestAsyncMatching:
    def test_cancel_task_stops_work(self, engine: MatchingEngine):
        """Cancelling a running task should transition it to cancelled promptly."""
        reqs = Requirements(
            domain="industrial",
            params={
                "working_distance_mm": 100,
                "target_width_mm": 50,
                "sensor_size": "2/3",
            },
        )
        task = engine.match_async(reqs)

        # Wait briefly for the task to start executing.
        for _ in range(50):
            if engine.get_task(task.task_id).status == "running":
                break
            time.sleep(0.01)

        cancelled = engine.cancel_task(task.task_id)
        assert cancelled is True

        # The worker should finish quickly after cancellation.
        for _ in range(200):
            status = engine.get_task(task.task_id).status
            if status in ("cancelled", "completed", "failed"):
                break
            time.sleep(0.01)

        assert engine.get_task(task.task_id).status == "cancelled"

    def test_task_queue_capacity_rejects_overflow(self, engine: MatchingEngine):
        """Submitting beyond the combined running+queued limit fails fast."""
        original_semaphore = engine._task_semaphore
        # Reduce capacity to 1 so the second submit is rejected.
        engine._task_semaphore = threading.Semaphore(1)
        try:
            reqs = Requirements(domain="industrial", params={})
            first = engine.match_async(reqs)
            second = engine.match_async(reqs)

            assert first.status != "failed"
            assert second.status == "failed"
            assert "queue is full" in second.error.lower()
        finally:
            engine._task_semaphore = original_semaphore

    def test_progressive_stream_yields_stage_events(self, engine: MatchingEngine):
        """match_progressive() emits intermediate stage events before completion."""
        reqs = Requirements(
            domain="industrial",
            params={
                "working_distance_mm": 100,
                "target_width_mm": 50,
                "sensor_size": "2/3",
            },
        )
        events = list(engine.match_progressive(reqs, top_k=5))

        stages = [ev["stage"] for ev in events]
        assert "completed" in stages
        assert any(stage != "completed" for stage in stages)
        assert "index_pre_filter" in stages
