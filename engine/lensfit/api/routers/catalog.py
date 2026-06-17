"""Catalog management endpoints for user-defined lenses and detectors."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
)
from fastapi import (
    Request as _Request,
)
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool

from lensfit.db.models import DetectorCatalog, LensCatalog, Manufacturer

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])

MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB
_ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
_ALLOWED_MIME_TYPES = {
    "text/csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _validate_import_upload(filename: str | None, content_type: str | None) -> None:
    """Validate extension and MIME type before reading upload contents."""
    ext = Path(filename or "").suffix.lower()
    if ext not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension '{ext}'. Allowed: .csv, .xlsx",
        )
    if content_type not in _ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported MIME type '{content_type}'. "
                "Allowed: text/csv, "
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------
def get_db_session(request: _Request):
    """Yield a database session from application state.

    Reading the session maker from ``request.app.state`` avoids relying on
    module-level globals, which can be duplicated when the server is launched
    via ``python -m lensfit.api.server`` (``__main__`` vs the imported module
    are distinct module objects).
    """
    session_maker = request.app.state.session_maker
    if session_maker is None:
        raise RuntimeError("Database session maker not initialized")
    session = session_maker()
    try:
        yield session
    finally:
        session.close()


def _float_or_none(val: Any) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _int_or_none(val: Any) -> int | None:
    if val is None or val == "":
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Lens schemas
# ---------------------------------------------------------------------------
class LensCreate(BaseModel):
    manufacturer_id: int | None = None
    model: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=64)
    status: str = "active"
    focal_length_mm: float | None = None
    focal_length_min: float | None = None
    focal_length_max: float | None = None
    max_aperture: float | None = None
    min_aperture: float | None = None
    image_circle_mm: float | None = None
    min_working_distance_mm: float | None = None
    max_working_distance_mm: float | None = None
    nominal_wd_mm: float | None = None
    mount_type: str | None = None
    length_mm: float | None = None
    weight_g: float | None = None
    price_usd: float | None = None
    na: float | None = None
    wavelength_min_nm: int | None = None
    wavelength_max_nm: int | None = None
    distortion_percent: float | None = None
    mtf50_lpmm: float | None = None


class LensUpdate(BaseModel):
    manufacturer_id: int | None = None
    model: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=64)
    status: str | None = None
    focal_length_mm: float | None = None
    focal_length_min: float | None = None
    focal_length_max: float | None = None
    max_aperture: float | None = None
    min_aperture: float | None = None
    image_circle_mm: float | None = None
    min_working_distance_mm: float | None = None
    max_working_distance_mm: float | None = None
    nominal_wd_mm: float | None = None
    mount_type: str | None = None
    length_mm: float | None = None
    weight_g: float | None = None
    price_usd: float | None = None
    na: float | None = None
    wavelength_min_nm: int | None = None
    wavelength_max_nm: int | None = None
    distortion_percent: float | None = None
    mtf50_lpmm: float | None = None


class LensOut(BaseModel):
    id: int
    manufacturer_id: int | None
    model: str
    category: str
    status: str | None
    focal_length_mm: float | None
    focal_length_min: float | None
    focal_length_max: float | None
    max_aperture: float | None
    min_aperture: float | None
    image_circle_mm: float | None
    min_working_distance_mm: float | None
    max_working_distance_mm: float | None
    nominal_wd_mm: float | None
    mount_type: str | None
    length_mm: float | None
    weight_g: float | None
    price_usd: float | None
    na: float | None
    wavelength_min_nm: int | None
    wavelength_max_nm: int | None
    distortion_percent: float | None
    mtf50_lpmm: float | None
    data_source: str
    verified: bool | None

    model_config = ConfigDict(from_attributes=True)


class DetectorCreate(BaseModel):
    manufacturer_id: int | None = None
    model: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=64)
    sensor_format_inch: str | None = None
    sensor_w_mm: float | None = None
    sensor_h_mm: float | None = None
    sensor_diag_mm: float | None = None
    resolution_w: int | None = None
    resolution_h: int | None = None
    pixel_size_um: float | None = None
    mount_type: str | None = None
    data_interface: str | None = None
    max_fps_full: float | None = None
    price_usd: float | None = None
    netd_mk: float | None = None
    spectral_range_min_um: float | None = None
    spectral_range_max_um: float | None = None


class DetectorUpdate(BaseModel):
    manufacturer_id: int | None = None
    model: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, min_length=1, max_length=64)
    sensor_format_inch: str | None = None
    sensor_w_mm: float | None = None
    sensor_h_mm: float | None = None
    sensor_diag_mm: float | None = None
    resolution_w: int | None = None
    resolution_h: int | None = None
    pixel_size_um: float | None = None
    mount_type: str | None = None
    data_interface: str | None = None
    max_fps_full: float | None = None
    price_usd: float | None = None
    netd_mk: float | None = None
    spectral_range_min_um: float | None = None
    spectral_range_max_um: float | None = None


class DetectorOut(BaseModel):
    id: int
    manufacturer_id: int | None
    model: str
    category: str
    sensor_format_inch: str | None
    sensor_w_mm: float | None
    sensor_h_mm: float | None
    sensor_diag_mm: float | None
    resolution_w: int | None
    resolution_h: int | None
    pixel_size_um: float | None
    mount_type: str | None
    data_interface: str | None
    max_fps_full: float | None
    price_usd: float | None
    netd_mk: float | None
    spectral_range_min_um: float | None
    spectral_range_max_um: float | None
    data_source: str
    verified: bool | None

    model_config = ConfigDict(from_attributes=True)


class LensListOut(BaseModel):
    items: list[LensOut]
    total: int


# ---------------------------------------------------------------------------
# Manufacturer schemas
# ---------------------------------------------------------------------------
class ManufacturerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    name_en: str | None = None
    name_cn: str | None = None
    country: str | None = None
    website: str | None = None


class ManufacturerOut(BaseModel):
    id: int
    name: str
    name_en: str | None
    name_cn: str | None
    country: str | None
    website: str | None
    is_verified: bool | None
    data_source: str | None

    model_config = ConfigDict(from_attributes=True)


class ManufacturerListOut(BaseModel):
    items: list[ManufacturerOut]


# ---------------------------------------------------------------------------
# Manufacturers
# ---------------------------------------------------------------------------
@router.get("/manufacturers", response_model=ManufacturerListOut)
def list_manufacturers(
    session: Session = Depends(get_db_session),
):
    """List all manufacturers."""
    items = session.query(Manufacturer).order_by(Manufacturer.name).all()
    return {"items": items}


@router.post("/manufacturers", response_model=ManufacturerOut, status_code=201)
def create_manufacturer(
    payload: ManufacturerCreate,
    response: Response,
    session: Session = Depends(get_db_session),
):
    """Create a new manufacturer if one with the same name does not exist."""
    existing = (
        session.query(Manufacturer)
        .filter(func.lower(Manufacturer.name) == payload.name.lower())
        .first()
    )
    if existing:
        response.status_code = 200
        return existing
    item = Manufacturer(
        name=payload.name,
        name_en=payload.name_en,
        name_cn=payload.name_cn,
        country=payload.country,
        website=payload.website,
        is_verified=False,
        data_source="user",
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


def _build_lens_stmt(
    category: str | None,
    mount_type: str | None,
    data_source: str | None,
    q: str | None,
):
    from sqlalchemy import or_
    from sqlalchemy import select as core_select

    stmt = core_select(LensCatalog)
    if category:
        stmt = stmt.where(LensCatalog.category.ilike(f"%{category}%"))
    if mount_type:
        stmt = stmt.where(LensCatalog.mount_type.ilike(f"%{mount_type}%"))
    if data_source:
        stmt = stmt.where(LensCatalog.data_source == data_source)
    if q:
        like_q = f"%{q}%"
        stmt = stmt.where(
            or_(
                LensCatalog.model.ilike(like_q),
                LensCatalog.category.ilike(like_q),
                LensCatalog.mount_type.ilike(like_q),
            )
        )
    return stmt


@router.get("/lenses", response_model=LensListOut)
def list_lenses(
    category: str | None = None,
    mount_type: str | None = None,
    data_source: str | None = None,
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=5000),
    sort_by: str | None = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: Session = Depends(get_db_session),
):
    """List lens catalog (seed + user-defined) with pagination and search."""

    stmt = _build_lens_stmt(category, mount_type, data_source, q)
    count_stmt = _build_lens_stmt(category, mount_type, data_source, q).with_only_columns(
        func.count(LensCatalog.id)
    )
    if sort_by and hasattr(LensCatalog, sort_by):
        col = getattr(LensCatalog, sort_by)
        stmt = stmt.order_by(col.desc() if sort_order == "desc" else col.asc())
    total = session.execute(count_stmt).scalar() or 0
    items = list(session.execute(stmt.offset(skip).limit(limit)).scalars().all())
    return {"items": items, "total": total}


@router.post("/lenses", response_model=LensOut, status_code=201)
def create_lens(payload: LensCreate, session: Session = Depends(get_db_session)):
    """Create a user-defined lens."""
    existing = (
        session.query(LensCatalog)
        .filter_by(manufacturer_id=payload.manufacturer_id, model=payload.model)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Lens '{payload.model}' already exists for this manufacturer",
        )
    data = payload.model_dump(exclude_unset=True)
    data["data_source"] = "user"
    data["data_quality_score"] = 1.0
    data["verified"] = False
    item = LensCatalog(**data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/lenses/{lens_id}", response_model=LensOut)
def get_lens(lens_id: int, session: Session = Depends(get_db_session)):
    """Get a single lens by ID."""
    item = session.get(LensCatalog, lens_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lens not found")
    return item


@router.put("/lenses/{lens_id}", response_model=LensOut)
def update_lens(
    lens_id: int,
    payload: LensUpdate,
    session: Session = Depends(get_db_session),
):
    """Update a user-defined lens."""
    item = session.get(LensCatalog, lens_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lens not found")
    if item.data_source != "user":
        raise HTTPException(status_code=403, detail="Cannot modify seed lens")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    duplicate = (
        session.query(LensCatalog)
        .filter_by(manufacturer_id=item.manufacturer_id, model=item.model)
        .filter(LensCatalog.id != item.id)
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"Lens '{item.model}' already exists for this manufacturer",
        )
    session.commit()
    session.refresh(item)
    return item


@router.delete("/lenses/{lens_id}", status_code=204)
def delete_lens(lens_id: int, session: Session = Depends(get_db_session)):
    """Delete a user-defined lens."""
    item = session.get(LensCatalog, lens_id)
    if not item:
        raise HTTPException(status_code=404, detail="Lens not found")
    if item.data_source != "user":
        raise HTTPException(status_code=403, detail="Cannot delete seed lens")
    session.delete(item)
    session.commit()
    return None


# ---------------------------------------------------------------------------
# Detectors
# ---------------------------------------------------------------------------
class DetectorListOut(BaseModel):
    items: list[DetectorOut]
    total: int


def _build_detector_stmt(
    category: str | None,
    mount_type: str | None,
    data_source: str | None,
    q: str | None,
):
    from sqlalchemy import or_
    from sqlalchemy import select as core_select

    stmt = core_select(DetectorCatalog)
    if category:
        stmt = stmt.where(DetectorCatalog.category.ilike(f"%{category}%"))
    if mount_type:
        stmt = stmt.where(DetectorCatalog.mount_type.ilike(f"%{mount_type}%"))
    if data_source:
        stmt = stmt.where(DetectorCatalog.data_source == data_source)
    if q:
        like_q = f"%{q}%"
        stmt = stmt.where(
            or_(
                DetectorCatalog.model.ilike(like_q),
                DetectorCatalog.category.ilike(like_q),
                DetectorCatalog.mount_type.ilike(like_q),
            )
        )
    return stmt


@router.get("/detectors", response_model=DetectorListOut)
def list_detectors(
    category: str | None = None,
    mount_type: str | None = None,
    data_source: str | None = None,
    q: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=5000),
    sort_by: str | None = None,
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    session: Session = Depends(get_db_session),
):
    """List detector catalog (seed + user-defined) with pagination and search."""

    stmt = _build_detector_stmt(category, mount_type, data_source, q)
    count_stmt = _build_detector_stmt(category, mount_type, data_source, q).with_only_columns(
        func.count(DetectorCatalog.id)
    )
    if sort_by and hasattr(DetectorCatalog, sort_by):
        col = getattr(DetectorCatalog, sort_by)
        stmt = stmt.order_by(col.desc() if sort_order == "desc" else col.asc())
    total = session.execute(count_stmt).scalar() or 0
    items = list(session.execute(stmt.offset(skip).limit(limit)).scalars().all())
    return {"items": items, "total": total}


@router.post("/detectors", response_model=DetectorOut, status_code=201)
def create_detector(
    payload: DetectorCreate, session: Session = Depends(get_db_session)
):
    """Create a user-defined detector."""
    existing = (
        session.query(DetectorCatalog)
        .filter_by(manufacturer_id=payload.manufacturer_id, model=payload.model)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Detector '{payload.model}' already exists for this manufacturer",
        )
    data = payload.model_dump(exclude_unset=True)
    data["data_source"] = "user"
    data["data_quality_score"] = 1.0
    data["verified"] = False
    item = DetectorCatalog(**data)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.get("/detectors/{detector_id}", response_model=DetectorOut)
def get_detector(detector_id: int, session: Session = Depends(get_db_session)):
    """Get a single detector by ID."""
    item = session.get(DetectorCatalog, detector_id)
    if not item:
        raise HTTPException(status_code=404, detail="Detector not found")
    return item


@router.put("/detectors/{detector_id}", response_model=DetectorOut)
def update_detector(
    detector_id: int,
    payload: DetectorUpdate,
    session: Session = Depends(get_db_session),
):
    """Update a user-defined detector."""
    item = session.get(DetectorCatalog, detector_id)
    if not item:
        raise HTTPException(status_code=404, detail="Detector not found")
    if item.data_source != "user":
        raise HTTPException(status_code=403, detail="Cannot modify seed detector")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, key, value)
    duplicate = (
        session.query(DetectorCatalog)
        .filter_by(manufacturer_id=item.manufacturer_id, model=item.model)
        .filter(DetectorCatalog.id != item.id)
        .first()
    )
    if duplicate:
        raise HTTPException(
            status_code=409,
            detail=f"Detector '{item.model}' already exists for this manufacturer",
        )
    session.commit()
    session.refresh(item)
    return item


@router.delete("/detectors/{detector_id}", status_code=204)
def delete_detector(detector_id: int, session: Session = Depends(get_db_session)):
    """Delete a user-defined detector."""
    item = session.get(DetectorCatalog, detector_id)
    if not item:
        raise HTTPException(status_code=404, detail="Detector not found")
    if item.data_source != "user":
        raise HTTPException(status_code=403, detail="Cannot delete seed detector")
    session.delete(item)
    session.commit()
    return None


# ---------------------------------------------------------------------------
# Bulk import
# ---------------------------------------------------------------------------
@router.post("/import")
async def import_catalog(
    file: UploadFile = File(...),
    session: Session = Depends(get_db_session),
):
    """Upload a CSV or Excel file of lenses/detectors and import as user data."""
    from lensfit.api.import_pipe import import_from_upload

    _validate_import_upload(file.filename, file.content_type)
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=(
                f"File size {len(content)} bytes exceeds maximum of "
                f"{MAX_UPLOAD_SIZE} bytes (5 MB)"
            ),
        )
    result = await run_in_threadpool(import_from_upload, file.filename or "", content, session)
    return result
