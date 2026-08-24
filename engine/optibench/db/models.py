"""SQLAlchemy database models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Manufacturer(Base):
    """厂商表."""

    __tablename__ = "manufacturers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    name_en: Mapped[str | None] = mapped_column(String)
    name_cn: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    website: Mapped[str | None] = mapped_column(String)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    data_source: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    lenses: Mapped[list[LensCatalog]] = relationship(back_populates="manufacturer")
    detectors: Mapped[list[DetectorCatalog]] = relationship(back_populates="manufacturer")


class LensCatalog(Base):
    """镜头目录表."""

    __tablename__ = "lens_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturers.id"))

    model: Mapped[str] = mapped_column(String, nullable=False)
    sku: Mapped[str | None] = mapped_column(String)
    category: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, default="active")

    # 光学参数
    focal_length_mm: Mapped[float | None] = mapped_column(Float)
    focal_length_min: Mapped[float | None] = mapped_column(Float)
    focal_length_max: Mapped[float | None] = mapped_column(Float)
    max_aperture: Mapped[float | None] = mapped_column(Float)
    min_aperture: Mapped[float | None] = mapped_column(Float)
    image_circle_mm: Mapped[float | None] = mapped_column(Float)

    # 工作距离
    min_working_distance_mm: Mapped[float | None] = mapped_column(Float)
    max_working_distance_mm: Mapped[float | None] = mapped_column(Float)
    nominal_wd_mm: Mapped[float | None] = mapped_column(Float)

    # 机械参数
    mount_type: Mapped[str | None] = mapped_column(String)
    mount_flange_mm: Mapped[float | None] = mapped_column(Float)
    outer_diameter_mm: Mapped[float | None] = mapped_column(Float)
    length_mm: Mapped[float | None] = mapped_column(Float)
    weight_g: Mapped[float | None] = mapped_column(Float)

    # 性能参数
    mtf50_lpmm: Mapped[float | None] = mapped_column(Float)
    distortion_percent: Mapped[float | None] = mapped_column(Float)
    telecentricity_deg: Mapped[float | None] = mapped_column(Float)
    na: Mapped[float | None] = mapped_column(Float)
    working_f_number: Mapped[float | None] = mapped_column(Float)

    # 光谱参数
    wavelength_min_nm: Mapped[int | None] = mapped_column(Integer)
    wavelength_max_nm: Mapped[int | None] = mapped_column(Integer)
    coating_type: Mapped[str | None] = mapped_column(String)

    # 商业参数
    price_usd: Mapped[float | None] = mapped_column(Float)
    datasheet_url: Mapped[str | None] = mapped_column(String)
    image_url: Mapped[str | None] = mapped_column(String)

    # 元数据
    data_source: Mapped[str | None] = mapped_column(String)
    data_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    manufacturer: Mapped[Manufacturer] = relationship(back_populates="lenses")

    __table_args__ = (
        # 核心复合索引 — 匹配引擎 Stage 1 使用
        Index("ix_lens_category", "category"),
        Index("ix_lens_mount_type", "mount_type"),
        Index("ix_lens_focal_length", "focal_length_mm"),
        Index("ix_lens_wavelength", "wavelength_min_nm", "wavelength_max_nm"),
        Index("ix_lens_price", "price_usd"),
        Index("ix_lens_data_source", "data_source"),
        Index("ix_lens_manufacturer_id", "manufacturer_id"),
        {"sqlite_autoincrement": True},
    )


class DetectorCatalog(Base):
    """探测器目录表."""

    __tablename__ = "detector_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey("manufacturers.id"))

    model: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)

    # 传感器物理参数
    sensor_format_inch: Mapped[str | None] = mapped_column(String)
    sensor_w_mm: Mapped[float | None] = mapped_column(Float)
    sensor_h_mm: Mapped[float | None] = mapped_column(Float)
    sensor_diag_mm: Mapped[float | None] = mapped_column(Float)

    # 分辨率参数
    resolution_w: Mapped[int | None] = mapped_column(Integer)
    resolution_h: Mapped[int | None] = mapped_column(Integer)
    pixel_size_um: Mapped[float | None] = mapped_column(Float)

    # 性能参数 (EMVA 1288)
    quantum_efficiency_peak: Mapped[float | None] = mapped_column(Float)
    read_noise_e: Mapped[float | None] = mapped_column(Float)
    dark_current_e_s: Mapped[float | None] = mapped_column(Float)
    full_well_e: Mapped[float | None] = mapped_column(Float)
    dynamic_range_db: Mapped[float | None] = mapped_column(Float)

    # 红外探测器专用
    netd_mk: Mapped[float | None] = mapped_column(Float)
    spectral_range_min_um: Mapped[float | None] = mapped_column(Float)
    spectral_range_max_um: Mapped[float | None] = mapped_column(Float)

    # 接口与数据
    mount_type: Mapped[str | None] = mapped_column(String)
    data_interface: Mapped[str | None] = mapped_column(String)
    max_fps_full: Mapped[float | None] = mapped_column(Float)

    # 商业参数
    price_usd: Mapped[float | None] = mapped_column(Float)
    datasheet_url: Mapped[str | None] = mapped_column(String)

    # 元数据
    data_source: Mapped[str | None] = mapped_column(String)
    data_quality_score: Mapped[float] = mapped_column(Float, default=0.0)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    manufacturer: Mapped[Manufacturer] = relationship(back_populates="detectors")

    __table_args__ = (
        Index("ix_detector_category", "category"),
        Index("ix_detector_mount_type", "mount_type"),
        Index("ix_detector_sensor_format", "sensor_format_inch"),
        Index("ix_detector_pixel_size", "pixel_size_um"),
        Index("ix_detector_data_source", "data_source"),
        Index("ix_detector_manufacturer_id", "manufacturer_id"),
        {"sqlite_autoincrement": True},
    )


class CompatibilityCache(Base):
    """兼容性缓存表 — 按需计算 + LRU 淘汰."""

    __tablename__ = "compatibility_cache"

    cache_key: Mapped[str] = mapped_column(String, primary_key=True)
    lens_id: Mapped[int] = mapped_column(Integer, nullable=False)
    detector_id: Mapped[int] = mapped_column(Integer, nullable=False)
    adapter_id: Mapped[int | None] = mapped_column(Integer)

    result_json: Mapped[str] = mapped_column(Text, nullable=False)
    is_compatible: Mapped[bool] = mapped_column(Boolean, default=True)
    compatibility_score: Mapped[float | None] = mapped_column(Float)
    coverage_ratio: Mapped[float | None] = mapped_column(Float)
    nyquist_ratio: Mapped[float | None] = mapped_column(Float)
    vignetting_risk: Mapped[bool] = mapped_column(Boolean, default=False)

    algorithm_version: Mapped[str] = mapped_column(String, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    access_count: Mapped[int] = mapped_column(Integer, default=1)
    last_accessed: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Project(Base):
    """用户项目表."""

    __tablename__ = "user_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    domain: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    setups: Mapped[list[ProjectSetup]] = relationship(back_populates="project")


class ProjectSetup(Base):
    """项目方案表 — 引用 + 快照双模式."""

    __tablename__ = "project_setups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("user_projects.id"))
    name: Mapped[str] = mapped_column(String, nullable=False)

    # 引用目录
    lens_id: Mapped[int | None] = mapped_column(ForeignKey("lens_catalog.id"))
    detector_id: Mapped[int | None] = mapped_column(ForeignKey("detector_catalog.id"))
    adapter_id: Mapped[int | None] = mapped_column(Integer)

    # 快照
    lens_snapshot: Mapped[str | None] = mapped_column(Text)
    detector_snapshot: Mapped[str | None] = mapped_column(Text)
    adapter_snapshot: Mapped[str | None] = mapped_column(Text)
    snapshot_version: Mapped[int | None] = mapped_column(Integer)
    snapshot_date: Mapped[datetime | None] = mapped_column(DateTime)
    drift_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    drift_details: Mapped[str | None] = mapped_column(Text)

    # 自定义参数
    custom_lens_params: Mapped[str | None] = mapped_column(Text)
    custom_detector_params: Mapped[str | None] = mapped_column(Text)

    # 计算结果缓存
    calculated_params: Mapped[str | None] = mapped_column(Text)

    # 匹配结果快照（含 reason, derivation_chain, diagnostics, score_vector）
    match_result_snapshot: Mapped[str | None] = mapped_column(Text)

    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped[Project] = relationship(back_populates="setups")


def init_db(db_url: str = "sqlite:///optibench.db") -> None:
    """初始化数据库.

    使用 Alembic 迁移管理 schema，确保模型定义与迁移脚本保持一致，
    避免 ``Base.metadata.create_all`` 与后续 migration 产生索引冲突。
    """
    from pathlib import Path

    from alembic import command
    from alembic.config import Config
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    engine_dir = Path(__file__).parent.parent.parent
    alembic_cfg = Config(str(engine_dir / "alembic.ini"))
    # 让 script_location 指向 alembic.ini 所在目录下的相对路径，避免依赖 CWD
    alembic_cfg.set_main_option(
        "script_location", str(engine_dir / "optibench" / "db" / "migrations")
    )
    # Keep the URL configured as well; some Alembic internals still reference it
    # even when a connection is provided explicitly.
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Provide our own connection/engine so we can dispose it explicitly after the
    # upgrade. NullPool closes connections immediately on return, which avoids
    # the ResourceWarnings caused by Alembic keeping an engine alive.
    engine = create_engine(
        db_url,
        connect_args={"check_same_thread": False},
        poolclass=NullPool,
    )
    with engine.connect() as connection:
        alembic_cfg.attributes["connection"] = connection
        command.upgrade(alembic_cfg, "head")
    engine.dispose()
