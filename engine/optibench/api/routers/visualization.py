"""Visualization data endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from optibench.api.deps import get_db_session
from optibench.db.catalog import CatalogQuery

router = APIRouter(prefix="/api/v1/visualize", tags=["visualization"])


class CoverageReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)


@router.post("/coverage")
def generate_coverage_data(req: CoverageReq, session: Session = Depends(get_db_session)):
    """生成传感器覆盖图几何数据."""
    from optibench.visualization.coverage import CoveragePlotData

    catalog = CatalogQuery(session)
    lens = catalog.get_lens_by_id(req.lens_id)
    det = catalog.get_detector_by_id(req.detector_id)

    if not lens or not det:
        raise HTTPException(status_code=404, detail="Lens or detector not found")

    plot = CoveragePlotData(
        sensor_w=det.sensor_w_mm or 0,
        sensor_h=det.sensor_h_mm or 0,
        image_circle=lens.image_circle_mm or 0,
    )
    return plot.generate()


class MtfReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)


@router.post("/mtf")
def generate_mtf_data(req: MtfReq, session: Session = Depends(get_db_session)):
    """生成镜头 MTF 曲线数据（基于 mtf50_lpmm 估算）."""
    from optibench.visualization.mtf import MtfPlotData

    catalog = CatalogQuery(session)
    lens = catalog.get_lens_by_id(req.lens_id)
    det = catalog.get_detector_by_id(req.detector_id)

    if not lens or not det:
        raise HTTPException(status_code=404, detail="Lens or detector not found")

    mtf50 = lens.mtf50_lpmm
    if mtf50 is None or mtf50 <= 0:
        raise HTTPException(
            status_code=422, detail="Lens has no valid MTF50 data for plotting"
        )

    plot = MtfPlotData(
        mtf50_lpmm=mtf50,
        pixel_size_um=det.pixel_size_um,
    )
    return plot.generate()


class CocReq(BaseModel):
    lens_id: int = Field(..., ge=1)
    detector_id: int = Field(..., ge=1)
    focus_distance_m: float = Field(default=2.0, gt=0)


@router.post("/coc")
def generate_coc_data(req: CocReq, session: Session = Depends(get_db_session)):
    """生成摄影景深/弥散圆数据（基于镜头与传感器参数估算）."""
    from optibench.visualization.coc import CocPlotData

    catalog = CatalogQuery(session)
    lens = catalog.get_lens_by_id(req.lens_id)
    det = catalog.get_detector_by_id(req.detector_id)

    if not lens or not det:
        raise HTTPException(status_code=404, detail="Lens or detector not found")

    focal_length = lens.focal_length_mm
    max_aperture = lens.max_aperture
    if not focal_length or focal_length <= 0:
        raise HTTPException(
            status_code=422, detail="Lens has no valid focal length for CoC plot"
        )
    if not max_aperture or max_aperture <= 0:
        raise HTTPException(
            status_code=422, detail="Lens has no valid aperture for CoC plot"
        )
    if (
        not det.sensor_w_mm
        or det.sensor_w_mm <= 0
        or not det.sensor_h_mm
        or det.sensor_h_mm <= 0
    ):
        raise HTTPException(
            status_code=422, detail="Detector has no valid sensor dimensions for CoC plot"
        )
    if not det.pixel_size_um or det.pixel_size_um <= 0:
        raise HTTPException(
            status_code=422, detail="Detector has no valid pixel size for CoC plot"
        )

    plot = CocPlotData(
        focal_length_mm=focal_length,
        max_aperture=max_aperture,
        sensor_w_mm=det.sensor_w_mm,
        sensor_h_mm=det.sensor_h_mm,
        pixel_size_um=det.pixel_size_um,
        focus_distance_m=req.focus_distance_m,
    )
    return plot.generate()
