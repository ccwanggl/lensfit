"""物理约束库 — 结构化封装现有约束检查逻辑."""

from __future__ import annotations

from lensfit.core.utils import is_mount_compatible
from lensfit.knowledge.base import OpticalConstraint, ConstraintViolation


def _check_image_circle_coverage(combo) -> tuple[bool, dict]:
    lens = combo.lens
    det = combo.detector
    image_circle = getattr(lens, "image_circle_mm", None) or 0
    sensor_diag = getattr(det, "sensor_diag_mm", None) or 0
    ok = image_circle >= sensor_diag * 0.95
    return ok, {
        "image_circle": image_circle,
        "sensor_diag": round(sensor_diag, 2),
        "margin": round((image_circle - sensor_diag) / image_circle, 2) if image_circle > 0 else 0,
    }


def _check_mount_compatible(combo) -> tuple[bool, dict]:
    lens = combo.lens
    det = combo.detector
    lens_mount = getattr(lens, "mount_type", "")
    det_mount = getattr(det, "mount_type", "")
    compatible, adapter = is_mount_compatible(lens_mount, det_mount)
    return compatible, {
        "lens_mount": lens_mount,
        "det_mount": det_mount,
        "adapter": adapter or "无",
    }


def _check_wd_in_range(combo) -> tuple[bool, dict]:
    lens = combo.lens
    reqs = combo.requirements
    if not reqs:
        return True, {}
    wd = reqs.params.get("working_distance_mm")
    if wd is None:
        return True, {}
    min_wd = getattr(lens, "min_working_distance_mm", None)
    max_wd = getattr(lens, "max_working_distance_mm", None)
    ok = True
    if min_wd is not None and wd < min_wd:
        ok = False
    if max_wd is not None and wd > max_wd:
        ok = False
    return ok, {
        "wd": wd,
        "min_wd": min_wd,
        "max_wd": max_wd,
    }


def _check_nyquist_satisfied(combo) -> tuple[bool, dict]:
    lens = combo.lens
    det = combo.detector
    pixel_size = getattr(det, "pixel_size_um", 0) or 0
    mtf50 = getattr(lens, "mtf50_lpmm", 0) or 0
    if pixel_size <= 0 or mtf50 <= 0:
        return True, {}  # 无数据时放行
    sensor_nyquist = 1000 / (2 * pixel_size)
    oversampling = mtf50 / sensor_nyquist
    ok = 0.5 <= oversampling <= 1.2
    return ok, {
        "pixel_size_um": pixel_size,
        "mtf50_lpmm": mtf50,
        "sensor_nyquist_lpmm": round(sensor_nyquist, 1),
        "oversampling_ratio": round(oversampling, 2),
    }


def _check_distortion_limit(combo) -> tuple[bool, dict]:
    lens = combo.lens
    distortion = getattr(lens, "distortion_percent", None)
    if distortion is None:
        return True, {}
    ok = distortion <= 2.0
    return ok, {
        "distortion_percent": distortion,
        "limit": 2.0,
    }


# ─── 约束实例化 ───
image_circle_coverage = OpticalConstraint(
    id="image_circle_coverage",
    name_cn="像圈覆盖约束",
    principle="镜头像圈必须至少覆盖传感器感光区域，否则成像边缘会出现亮度衰减（渐晕），影响测量精度。",
    check_fn=_check_image_circle_coverage,
    failure_explanation_tpl="镜头像圈 {image_circle}mm 不足以覆盖传感器对角线 {sensor_diag}mm，覆盖裕量仅 {margin}，会导致渐晕。",
    suggestion="建议：选用像圈更大的镜头，或缩小传感器靶面（如从 2/3\" 改为 1/2\"）。",
    severity="error",
)

mount_compatible = OpticalConstraint(
    id="mount_compatible",
    name_cn="接口兼容约束",
    principle="镜头与相机的机械接口必须匹配，且法兰距一致。接口不匹配时无法安装或无法合焦。",
    check_fn=_check_mount_compatible,
    failure_explanation_tpl="镜头接口 {lens_mount} 与相机接口 {det_mount} 不兼容，无法直接安装。",
    suggestion="建议：更换为相同接口的镜头/相机，或使用标准转接环（如 {adapter}）。",
    severity="error",
)

wd_in_range = OpticalConstraint(
    id="wd_in_range",
    name_cn="工作距离范围约束",
    principle="每支镜头都有标称的工作距离范围。超出此范围时，镜头无法对焦或像质严重下降。",
    check_fn=_check_wd_in_range,
    failure_explanation_tpl="目标工作距离 {wd}mm 超出镜头标称范围 {min_wd}–{max_wd}mm。",
    suggestion="建议：调整工作距离至镜头标称范围内，或选用工作距离范围更宽的镜头。",
    severity="warning",
)

nyquist_satisfied = OpticalConstraint(
    id="nyquist_satisfied",
    name_cn="奈奎斯特采样约束",
    principle="镜头光学分辨率应高于传感器奈奎斯特频率，否则高频细节无法被采样，产生混叠伪影。",
    check_fn=_check_nyquist_satisfied,
    failure_explanation_tpl="镜头 MTF50={mtf50_lpmm} lp/mm，传感器奈奎斯特频率={sensor_nyquist_lpmm} lp/mm，过采样率 {oversampling_ratio}，不匹配。",
    suggestion="建议：过采样率偏低时选用更高分辨率镜头；过采样率过高时选用更小像元或更低倍率。",
    severity="warning",
)

distortion_limit = OpticalConstraint(
    id="distortion_limit",
    name_cn="畸变上限约束",
    principle="镜头畸变使直线在图像中弯曲，影响精密尺寸测量。工业测量通常要求畸变 < 2%。",
    check_fn=_check_distortion_limit,
    failure_explanation_tpl="镜头畸变 {distortion_percent}% 超过上限 {limit}%，会引入测量误差。",
    suggestion="建议：选用低畸变镜头（< 1%），或通过标定补偿畸变。",
    severity="warning",
)


# ─── 全局注册表 ───
ALL_CONSTRAINTS: list[OpticalConstraint] = [
    image_circle_coverage,
    mount_compatible,
    wd_in_range,
    nyquist_satisfied,
    distortion_limit,
]


def get_constraint_by_id(cid: str) -> OpticalConstraint | None:
    """通过 ID 查询约束."""
    for c in ALL_CONSTRAINTS:
        if c.id == cid:
            return c
    return None


def check_all_constraints(combo) -> list[ConstraintViolation]:
    """检查所有约束，返回违规列表."""
    violations: list[ConstraintViolation] = []
    for c in ALL_CONSTRAINTS:
        if c.check_fn is None:
            continue
        ok, context = c.check_fn(combo)
        if not ok:
            violations.append(ConstraintViolation(
                constraint_id=c.id,
                constraint_name=c.name_cn,
                explanation=c.format_failure(context),
                suggestion=c.suggestion,
                severity=c.severity,
                context=context,
            ))
    return violations
