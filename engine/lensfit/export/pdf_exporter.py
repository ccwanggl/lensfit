"""PDF report generator for LensFit match results."""

from __future__ import annotations

from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _reason_badge_style(reason: str) -> str:
    """Return a colored prefix based on reason strength."""
    if not reason:
        return ""
    if reason.startswith("✓"):
        return f'<font color="#059669">{reason}</font>'
    if reason.startswith("⚠"):
        return f'<font color="#d97706">{reason}</font>'
    if reason.startswith("∼"):
        return f'<font color="#64748b">{reason}</font>'
    return reason


def generate_pdf_report(
    requirements: dict[str, Any],
    results: list[dict[str, Any]],
    top_k: int = 10,
    diagnostics: list[dict[str, Any]] | None = None,
    what_if_results: list[dict[str, Any]] | None = None,
) -> bytes:
    """Generate a PDF report of match results.

    Args:
        requirements: User input parameters.
        results: Top match results.
        top_k: Max results to include.
        diagnostics: Filter stage diagnostics (optional).
        what_if_results: What-if sensitivity results (optional).

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
    heading3 = ParagraphStyle(
        "Heading3",
        parent=styles["Heading3"],
        fontSize=11,
        textColor=colors.HexColor("#374151"),
        spaceAfter=3 * mm,
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
        [
            "目标尺寸",
            f"{requirements.get('target_width_mm', '-')} × "
            f"{requirements.get('target_height_mm', '-')} mm",
        ],
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

    # Diagnostics section
    if diagnostics:
        story.append(Paragraph("匹配诊断", heading2))
        diag_data = [["阶段", "过滤前", "过滤后", "拒绝原因", "建议"]]
        for d in diagnostics:
            reasons = d.get("rejected_reasons", {})
            reason_str = "; ".join(f"{k}: {v}" for k, v in reasons.items()) if reasons else "-"
            diag_data.append([
                d.get("stage", "-"),
                str(d.get("before_count", 0)),
                str(d.get("after_count", 0)),
                reason_str,
                d.get("suggestion", "-"),
            ])
        diag_table = Table(diag_data, colWidths=[35 * mm, 20 * mm, 20 * mm, 55 * mm, 50 * mm])
        diag_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f59e0b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(diag_table)
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

        result_table = Table(
            result_data,
            colWidths=[15 * mm, 45 * mm, 45 * mm, 20 * mm, 20 * mm, 15 * mm],
        )
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

    # Match reasons section
    reasons_exist = any(r.get("reason") for r in results[:top_k])
    if reasons_exist:
        story.append(Paragraph("匹配理由", heading2))
        for i, r in enumerate(results[:top_k], 1):
            reason = r.get("reason", "")
            if reason:
                story.append(Paragraph(
                    f"#{i} {r.get('lens_model', '')} — {_reason_badge_style(reason)}",
                    body_style,
                ))
        story.append(Spacer(1, 6 * mm))

    # Derivation chain section
    chain_exist = any(r.get("derivation_chain") for r in results[:top_k])
    if chain_exist:
        story.append(Paragraph("推导链", heading2))
        for i, r in enumerate(results[:top_k], 1):
            chain = r.get("derivation_chain", [])
            if chain:
                story.append(Paragraph(f"#{i} {r.get('lens_model', '')}", heading3))
                chain_data = [["步骤", "公式", "输入", "输出", "物理原理"]]
                for step in chain:
                    chain_data.append([
                        step.get("step", "-"),
                        step.get("formula", "-"),
                        str(step.get("inputs", "-"))[:60],
                        str(step.get("output", "-"))[:40],
                        step.get("principle", "-"),
                    ])
                chain_table = Table(
                    chain_data,
                    colWidths=[15 * mm, 40 * mm, 50 * mm, 35 * mm, 40 * mm],
                )
                chain_table.setStyle(
                    TableStyle([
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#10b981")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 8),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1), (-1, -1),
                            [colors.white, colors.HexColor("#f9fafb")],
                        ),
                        ("TOPPADDING", (0, 0), (-1, -1), 3),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                    ])
                )
                story.append(chain_table)
                story.append(Spacer(1, 4 * mm))
        story.append(Spacer(1, 4 * mm))

    # What-if sensitivity section
    if what_if_results and results:
        story.append(Paragraph("参数敏感性分析", heading2))
        story.append(Paragraph(
            f"调整参数后，结果数量变化：{len(what_if_results) - len(results):+d} 个",
            body_style,
        ))
        story.append(Spacer(1, 3 * mm))
        diff_data = [["镜头", "基准评分", "调整后评分", "变化"]]
        baseline_map = {f"{b.get('lens_id')}-{b.get('detector_id')}": b for b in results[:top_k]}
        for r in what_if_results[:top_k]:
            key = f"{r.get('lens_id')}-{r.get('detector_id')}"
            baseline = baseline_map.get(key)
            score = r.get("score", 0)
            base_score = baseline.get("score", 0) if baseline else 0
            diff = score - base_score
            diff_str = f"{diff:+.3f}" if baseline else "N/A"
            diff_color = "#059669" if diff > 0.01 else "#dc2626" if diff < -0.01 else "#64748b"
            diff_data.append([
                r.get("lens_model", key),
                f"{base_score:.3f}" if baseline else "-",
                f"{score:.3f}",
                f'<font color="{diff_color}">{diff_str}</font>',
            ])
        diff_table = Table(diff_data, colWidths=[60 * mm, 30 * mm, 30 * mm, 30 * mm])
        diff_table.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#6366f1")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("ALIGN", (0, 1), (0, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        story.append(diff_table)
        story.append(Spacer(1, 8 * mm))

    story.append(Paragraph(
        "<i>本报告由 LensFit 自动生成。数据仅供参考，最终选型请以厂商规格书为准。</i>",
        ParagraphStyle("Footer", parent=body_style, textColor=colors.grey, fontSize=8),
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
