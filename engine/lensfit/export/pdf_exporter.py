"""PDF report generator for LensFit match results."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(
    requirements: dict[str, Any],
    results: list[dict[str, Any]],
    top_k: int = 10,
) -> bytes:
    """Generate a PDF report of match results.

    Returns:
        PDF bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#1a56db"),
        spaceAfter=12 * mm,
    )
    heading2 = ParagraphStyle(
        "Heading2",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#1f2937"),
        spaceAfter=6 * mm,
    )
    body_style = styles["BodyText"]
    body_style.fontSize = 10

    story = []

    # Title
    story.append(Paragraph("LensFit 选型报告", title_style))
    story.append(Spacer(1, 4 * mm))

    # Requirements section
    story.append(Paragraph("选型参数", heading2))
    req_data = [
        ["参数", "值"],
        ["传感器尺寸", requirements.get("sensor_size", "-")],
        ["像元尺寸", f"{requirements.get('pixel_size_um', '-')} μm"],
        ["目标尺寸", f"{requirements.get('target_width_mm', '-')} × {requirements.get('target_height_mm', '-')} mm"],
        ["工作距离", f"{requirements.get('working_distance_mm', '-')} mm"],
        ["镜头类型", requirements.get("lens_type", "-")],
        ["接口类型", requirements.get("interface", "-")],
    ]
    req_table = Table(req_data, colWidths=[60 * mm, 100 * mm])
    req_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e5e7eb")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ])
    )
    story.append(req_table)
    story.append(Spacer(1, 8 * mm))

    # Results section
    story.append(Paragraph(f"匹配结果 (Top {min(top_k, len(results))})", heading2))

    if results:
        result_data = [["排名", "镜头", "探测器", "评分", "覆盖度", "渐晕"]]
        for i, r in enumerate(results[:top_k], 1):
            result_data.append([
                str(i),
                r.get("lens_model", f"#{r.get('lens_id', '?')}"),
                r.get("detector_model", f"#{r.get('detector_id', '?')}"),
                f"{r.get('score', 0):.3f}",
                f"{(r.get('coverage_ratio', 0) * 100):.0f}%",
                "是" if r.get("vignetting") else "否",
            ])

        result_table = Table(result_data, colWidths=[15 * mm, 45 * mm, 45 * mm, 20 * mm, 20 * mm, 15 * mm])
        result_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a56db")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (1, 1), (2, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(result_table)
    else:
        story.append(Paragraph("无匹配结果", body_style))

    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(
        "<i>本报告由 LensFit 自动生成。数据仅供参考，最终选型请以厂商规格书为准。</i>",
        ParagraphStyle("Footer", parent=body_style, textColor=colors.grey, fontSize=8),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
