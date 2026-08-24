"""Export endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response as FastAPIResponse
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1", tags=["export"])


class ExportReq(BaseModel):
    requirements: dict
    results: list[dict]
    format: str = Field(default="pdf", pattern=r"^(pdf|excel|csv)$")
    top_k: int = Field(default=10, ge=1, le=1000)
    diagnostics: list[dict] | None = None
    what_if_results: list[dict] | None = None


@router.post("/export")
def export_results(req: ExportReq):
    """导出匹配结果为 PDF、Excel 或 CSV."""
    try:
        if req.format == "pdf":
            from optibench.export.pdf_exporter import generate_pdf_report

            pdf_bytes = generate_pdf_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=optibench-report.pdf"},
            )
        elif req.format == "excel":
            from optibench.export.excel_exporter import generate_excel_report

            excel_bytes = generate_excel_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=excel_bytes,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={"Content-Disposition": "attachment; filename=optibench-report.xlsx"},
            )
        else:  # csv
            from optibench.export.csv_exporter import generate_csv_report

            csv_bytes = generate_csv_report(
                req.requirements, req.results, req.top_k,
                diagnostics=req.diagnostics, what_if_results=req.what_if_results,
            )
            return FastAPIResponse(
                content=csv_bytes,
                media_type="text/csv; charset=utf-8",
                headers={"Content-Disposition": "attachment; filename=optibench-report.csv"},
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")
