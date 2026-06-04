"""Excel report generator for LensFit match results."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


def generate_excel_report(
    requirements: dict[str, Any],
    results: list[dict[str, Any]],
    top_k: int = 20,
) -> bytes:
    """Generate an Excel report of match results.

    Returns:
        Excel bytes
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "选型报告"

    # Styles
    title_font = Font(size=16, bold=True, color="1A56DB")
    header_font = Font(size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1A56DB", end_color="1A56DB", fill_type="solid")
    thin_border = Border(
        left=Side(style="thin", color="D1D5DB"),
        right=Side(style="thin", color="D1D5DB"),
        top=Side(style="thin", color="D1D5DB"),
        bottom=Side(style="thin", color="D1D5DB"),
    )
    alt_fill = PatternFill(start_color="F9FAFB", end_color="F9FAFB", fill_type="solid")

    # Title
    ws["A1"] = "LensFit 选型报告"
    ws["A1"].font = title_font
    ws.merge_cells("A1:F1")

    # Requirements
    ws["A3"] = "选型参数"
    ws["A3"].font = Font(size=12, bold=True)
    req_items = [
        ("传感器尺寸", requirements.get("sensor_size", "-")),
        ("像元尺寸 (μm)", requirements.get("pixel_size_um", "-")),
        ("目标宽度 (mm)", requirements.get("target_width_mm", "-")),
        ("目标高度 (mm)", requirements.get("target_height_mm", "-")),
        ("工作距离 (mm)", requirements.get("working_distance_mm", "-")),
        ("镜头类型", requirements.get("lens_type", "-")),
        ("接口类型", requirements.get("interface", "-")),
    ]
    # Results header
    result_start = 13
    ws[f"A{result_start}"] = "排名"
    ws[f"B{result_start}"] = "镜头型号"
    ws[f"C{result_start}"] = "探测器型号"
    ws[f"D{result_start}"] = "评分"
    ws[f"E{result_start}"] = "覆盖度"
    ws[f"F{result_start}"] = "渐晕"
    ws[f"G{result_start}"] = "估算焦距 (mm)"
    ws[f"H{result_start}"] = "放大倍率"

    for col in range(1, 9):
        cell = ws.cell(row=result_start, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = thin_border

    def _sanitize(val):
        """防 Excel 公式注入：以 = + - @ 开头的字符串前加单引号."""
        if isinstance(val, str) and val and val[0] in "=+-@":
            return "'" + val
        return val

    # Sanitize requirement values
    for i, (k, v) in enumerate(req_items, start=4):
        ws[f"A{i}"] = k
        ws[f"B{i}"] = _sanitize(v)
        ws[f"A{i}"].font = Font(bold=True)

    # Results data
    for idx, r in enumerate(results[:top_k], start=1):
        row = result_start + idx
        derived = r.get("derived", {})
        ws.cell(row=row, column=1, value=idx)
        ws.cell(row=row, column=2, value=_sanitize(r.get("lens_model", f"#{r.get('lens_id', '?')}")))
        ws.cell(row=row, column=3, value=_sanitize(r.get("detector_model", f"#{r.get('detector_id', '?')}")))
        ws.cell(row=row, column=4, value=round(r.get("score", 0), 3))
        ws.cell(row=row, column=5, value=f"{(r.get('coverage_ratio', 0) * 100):.0f}%")
        ws.cell(row=row, column=6, value="是" if r.get("vignetting") else "否")
        ws.cell(row=row, column=7, value=derived.get("focal_length", "-"))
        ws.cell(row=row, column=8, value=derived.get("magnification", "-"))

        for col in range(1, 9):
            cell = ws.cell(row=row, column=col)
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="center", vertical="center")
            if idx % 2 == 0:
                cell.fill = alt_fill

    # Auto column width
    for col in range(1, 9):
        ws.column_dimensions[get_column_letter(col)].width = 18
    ws.column_dimensions["B"].width = 28
    ws.column_dimensions["C"].width = 28

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()
