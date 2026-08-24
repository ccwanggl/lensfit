"""CSV report generator for OptiBench match results."""

from __future__ import annotations

import csv
import io
from typing import Any

from optibench.export.sanitize import sanitize_spreadsheet_value


def _sanitize(val: Any) -> str:
    """Prevent CSV formula injection."""
    if val is None:
        return ""
    result = sanitize_spreadsheet_value(str(val))
    return result if isinstance(result, str) else str(result)


def generate_csv_report(
    requirements: dict[str, Any],
    results: list[dict[str, Any]],
    top_k: int = 20,
    diagnostics: list[dict[str, Any]] | None = None,
    what_if_results: list[dict[str, Any]] | None = None,
) -> bytes:
    """Generate a CSV report of match results.

    Args:
        requirements: User input parameters.
        results: Top match results.
        top_k: Max results to include.
        diagnostics: Filter stage diagnostics (optional).
        what_if_results: What-if sensitivity results (optional).

    Returns:
        UTF-8 CSV bytes with BOM for Excel compatibility.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Title
    writer.writerow(["OptiBench 选型报告"])
    writer.writerow([])

    # Requirements
    writer.writerow(["选型参数"])
    req_items = [
        ("传感器尺寸", requirements.get("sensor_size", "-")),
        ("像元尺寸 (μm)", requirements.get("pixel_size_um", "-")),
        ("目标宽度 (mm)", requirements.get("target_width_mm", "-")),
        ("目标高度 (mm)", requirements.get("target_height_mm", "-")),
        ("工作距离 (mm)", requirements.get("working_distance_mm", "-")),
        ("镜头类型", requirements.get("lens_type", "-")),
        ("接口类型", requirements.get("interface", "-")),
    ]
    for k, v in req_items:
        writer.writerow([k, _sanitize(v)])
    writer.writerow([])

    # Results
    writer.writerow([f"匹配结果 (Top {min(top_k, len(results))})"])
    writer.writerow(
        [
            "排名",
            "镜头型号",
            "探测器型号",
            "评分",
            "覆盖度",
            "渐晕",
            "估算焦距 (mm)",
            "放大倍率",
            "匹配理由",
        ]
    )
    for idx, r in enumerate(results[:top_k], start=1):
        derived = r.get("derived", {}) or {}
        writer.writerow(
            [
                idx,
                _sanitize(r.get("lens_model", f"#{r.get('lens_id', '?')}")),
                _sanitize(r.get("detector_model", f"#{r.get('detector_id', '?')}")),
                round(r.get("score", 0), 3),
                f"{(r.get('coverage_ratio', 0) * 100):.0f}%",
                "是" if r.get("vignetting") else "否",
                _sanitize(derived.get("focal_length", "-")),
                _sanitize(derived.get("magnification", "-")),
                _sanitize(r.get("reason", "-")),
            ]
        )
    writer.writerow([])

    # Diagnostics
    if diagnostics:
        writer.writerow(["匹配诊断"])
        writer.writerow(["阶段", "过滤前", "过滤后", "拒绝原因", "建议"])
        for d in diagnostics:
            reasons = d.get("rejected_reasons", {})
            reason_str = "; ".join(f"{k}: {v}" for k, v in reasons.items()) if reasons else "-"
            writer.writerow(
                [
                    _sanitize(d.get("stage", "-")),
                    d.get("before_count", 0),
                    d.get("after_count", 0),
                    _sanitize(reason_str),
                    _sanitize(d.get("suggestion", "-")),
                ]
            )
        writer.writerow([])

    # What-if sensitivity
    if what_if_results and results:
        writer.writerow(["参数敏感性分析"])
        writer.writerow(["结果数量变化", len(what_if_results) - len(results)])
        writer.writerow(["镜头", "基准评分", "调整后评分", "变化"])
        baseline_map = {
            f"{b.get('lens_id')}-{b.get('detector_id')}": b for b in results[:top_k]
        }
        for r in what_if_results[:top_k]:
            key = f"{r.get('lens_id')}-{r.get('detector_id')}"
            baseline = baseline_map.get(key)
            score = r.get("score", 0)
            base_score = baseline.get("score", 0) if baseline else 0
            diff = score - base_score
            writer.writerow(
                [
                    _sanitize(r.get("lens_model", key)),
                    round(base_score, 3) if baseline else "-",
                    round(score, 3),
                    f"{diff:+.3f}" if baseline else "-",
                ]
            )
        writer.writerow([])

    # Footer
    writer.writerow(["本报告由 OptiBench 自动生成。数据仅供参考，最终选型请以厂商规格书为准。"])

    content = output.getvalue()
    return content.encode("utf-8-sig")
