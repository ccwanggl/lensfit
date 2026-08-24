"""Tests for matching engine."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from optibench.db.models import Base
from optibench.domains.base import DeviceCombo, Requirements
from optibench.domains.industrial import IndustrialVisionModule
from optibench.domains.photography import PhotographyModule
from optibench.matching.engine import MatchingEngine
from optibench.matching.scoring import ScoringEngine


class TestMatchingEngine:
    @pytest.fixture
    def engine(self):
        db_engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(db_engine)
        session_factory = sessionmaker(bind=db_engine)
        e = MatchingEngine(session_factory)
        e.register_domain(IndustrialVisionModule())
        yield e
        db_engine.dispose()

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


class TestPhotographyScoring:
    """摄影域评分逻辑单元测试."""

    @pytest.fixture
    def photo_module(self):
        return PhotographyModule()

    def test_brand_match_dimension_exists(self, photo_module):
        dims = {d.name for d in photo_module.get_scoring_dimensions()}
        assert "brand_match" in dims

    def test_calculate_derived_brand_score(self, photo_module):
        class FakeLens:
            focal_length_mm = 50.0
            focal_length_min = 50.0
            focal_length_max = 50.0
            max_aperture = 1.8
            image_circle_mm = 43.3
            price_usd = 1000.0
            model = "Canon EF 50mm f/1.8"

        class FakeDet:
            sensor_diag_mm = 43.3
            sensor_format_inch = "FF"

        reqs = Requirements(domain="photography", params={
            "purpose": "portrait",
            "sensor_format": "FF",
            "brand": "Canon",
            "max_aperture": 2.8,
            "budget_usd": 2000,
        })
        combo = DeviceCombo(lens=FakeLens(), detector=FakeDet(), requirements=reqs)
        derived = photo_module.calculate_derived(combo)
        assert derived["brand_score"] == pytest.approx(1.0)

        combo2 = DeviceCombo(
            lens=type("FakeLens", (), {
                "focal_length_mm": 50.0,
                "focal_length_min": 50.0,
                "focal_length_max": 50.0,
                "max_aperture": 1.8,
                "image_circle_mm": 43.3,
                "price_usd": 1000.0,
                "model": "Sony FE 50mm f/1.8",
            })(),
            detector=FakeDet(),
            requirements=reqs,
        )
        derived2 = photo_module.calculate_derived(combo2)
        assert derived2["brand_score"] == pytest.approx(0.2)

    def test_scoring_engine_brand_match(self, photo_module):
        scorer = ScoringEngine()
        derived = {"brand_score": 1.0}
        combo = type("Combo", (), {"derived": derived})()
        assert scorer._score_brand_match(combo) == pytest.approx(1.0)
