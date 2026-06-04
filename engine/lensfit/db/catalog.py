"""Database catalog query utilities."""

from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from lensfit.db.models import DetectorCatalog, LensCatalog


class CatalogQuery:
    """镜头/探测器目录查询器."""

    def __init__(self, session: Session):
        self.session = session

    def query_lenses(
        self,
        category: str | None = None,
        mount_type: str | None = None,
        focal_min: float | None = None,
        focal_max: float | None = None,
        image_circle_min: float | None = None,
        wd_min: float | None = None,
        wd_max: float | None = None,
        limit: int = 10000,
    ) -> list[LensCatalog]:
        """查询镜头目录 — Stage 1 索引预筛选."""
        stmt = select(LensCatalog)

        if category:
            stmt = stmt.where(
                func.lower(LensCatalog.category) == category.lower()
            )
        if mount_type:
            stmt = stmt.where(
                func.lower(LensCatalog.mount_type) == mount_type.lower()
            )
        if focal_min is not None:
            stmt = stmt.where(LensCatalog.focal_length_mm >= focal_min)
        if focal_max is not None:
            stmt = stmt.where(LensCatalog.focal_length_mm <= focal_max)
        if image_circle_min is not None:
            stmt = stmt.where(LensCatalog.image_circle_mm >= image_circle_min)
        if wd_min is not None:
            stmt = stmt.where(
                (LensCatalog.max_working_distance_mm >= wd_min)
                | (LensCatalog.max_working_distance_mm.is_(None))
            )
        if wd_max is not None:
            stmt = stmt.where(
                (LensCatalog.min_working_distance_mm <= wd_max)
                | (LensCatalog.min_working_distance_mm.is_(None))
            )

        stmt = stmt.limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def query_detectors(
        self,
        category: str | None = None,
        sensor_format: str | None = None,
        mount_type: str | None = None,
        limit: int = 5000,
    ) -> list[DetectorCatalog]:
        """查询探测器目录 — Stage 1 索引预筛选."""
        stmt = select(DetectorCatalog)

        if category:
            stmt = stmt.where(
                func.lower(DetectorCatalog.category) == category.lower()
            )
        if sensor_format:
            stmt = stmt.where(
                func.lower(DetectorCatalog.sensor_format_inch) == sensor_format.lower()
            )
        if mount_type:
            stmt = stmt.where(
                func.lower(DetectorCatalog.mount_type) == mount_type.lower()
            )

        stmt = stmt.limit(limit)
        return list(self.session.execute(stmt).scalars().all())

    def get_lens_by_id(self, lens_id: int) -> LensCatalog | None:
        """根据ID获取镜头."""
        return self.session.get(LensCatalog, lens_id)

    def get_detector_by_id(self, detector_id: int) -> DetectorCatalog | None:
        """根据ID获取探测器."""
        return self.session.get(DetectorCatalog, detector_id)
