"""光学公式库 — 结构化封装现有物理计算函数."""

from __future__ import annotations

from lensfit.core.thin_lens import ThinLensCalculator
from lensfit.core.utils import sensor_coverage_check, nyquist_match, is_mount_compatible
from lensfit.knowledge.base import OpticalFormula, FormulaParam


# ─── 薄透镜成像公式 ───
thin_lens_imaging = OpticalFormula(
    id="thin_lens_imaging",
    name_cn="薄透镜成像公式",
    expression="f = (WD × s) / (FOV + s)",
    latex=r"f = \frac{WD \cdot s}{FOV + s}",
    params=[
        FormulaParam("wd", "工作距离", "mm", "镜头前端到被测面的距离"),
        FormulaParam("fov", "视场宽度", "mm", "被测区域在物方的宽度"),
        FormulaParam("sensor", "传感器宽度", "mm", "传感器感光区域的物理宽度"),
    ],
    outputs=["focal_length"],
    principle="薄透镜近似下，物距、像距与焦距满足高斯公式。工业视觉中常用此公式由工作距离和视场反推所需焦距。",
    assumption="镜头视为薄透镜，视场角较小（近轴近似），忽略畸变影响。",
    domain="all",
    compute_fn=ThinLensCalculator.focal_from_wd_fov,
)

# ─── 放大倍率公式 ───
magnification = OpticalFormula(
    id="magnification",
    name_cn="放大倍率",
    expression="β = f / (WD − f) = 像高 / 物高",
    latex=r"\beta = \frac{f}{WD-f} = \frac{h_{\text{像}}}{h_{\text{物}}}",
    params=[
        FormulaParam("focal", "焦距", "mm"),
        FormulaParam("wd", "工作距离", "mm"),
    ],
    outputs=["magnification"],
    principle="横向放大倍率定义为像高与物高之比。在工业检测中，放大倍率直接决定像素精度（mm/px）。",
    assumption="薄透镜近似，工作距离远大于焦距。",
    domain="all",
    compute_fn=ThinLensCalculator.magnification_from_focal_wd,
)

# ─── 视场计算 ───
fov_from_focal = OpticalFormula(
    id="fov_from_focal",
    name_cn="视场计算",
    expression="FOV = (WD × s) / f − s",
    latex=r"FOV = \frac{WD \cdot s}{f} - s",
    params=[
        FormulaParam("wd", "工作距离", "mm"),
        FormulaParam("focal", "焦距", "mm"),
        FormulaParam("sensor", "传感器宽度", "mm"),
    ],
    outputs=["fov_w"],
    principle="已知焦距和工作距离，计算传感器能覆盖的物方区域大小。",
    assumption="薄透镜近似，镜头无畸变。",
    domain="all",
    compute_fn=ThinLensCalculator.fov_from_wd_focal,
)

# ─── 视角计算 ───
afov_from_focal = OpticalFormula(
    id="afov_from_focal",
    name_cn="视角计算",
    expression="AFOV = 2 × arctan(s / 2f)",
    latex=r"AFOV = 2 \arctan\left(\frac{s}{2f}\right)",
    params=[
        FormulaParam("sensor", "传感器宽度", "mm"),
        FormulaParam("focal", "焦距", "mm"),
    ],
    outputs=["afov_h"],
    principle="视角（Angle of Field of View）描述镜头能看到的场景范围，由传感器尺寸和焦距共同决定。",
    assumption="薄透镜近似。",
    domain="all",
    compute_fn=ThinLensCalculator.afov_from_sensor_focal,
)

# ─── 奈奎斯特采样定理 ───
nyquist_sampling = OpticalFormula(
    id="nyquist_sampling",
    name_cn="奈奎斯特采样定理",
    expression="f_Nyquist = 1 / (2 × p)  [lp/mm]",
    latex=r"f_{\text{Nyquist}} = \frac{1}{2p} \; [\text{lp/mm}]",
    params=[
        FormulaParam("pixel_size_um", "像元尺寸", "μm", "传感器单个像素的物理边长"),
        FormulaParam("lens_mtf50_lpmm", "镜头MTF50", "lp/mm", "可选，镜头在50%对比度下的空间频率"),
        FormulaParam("na", "数值孔径", "", "可选，显微镜物镜的数值孔径"),
    ],
    outputs=["sensor_nyquist_lpmm", "optical_limit_lpmm", "oversampling_ratio", "matched"],
    principle="奈奎斯特-香农采样定理：数字系统能无失真恢复的最高空间频率为采样频率的一半。在成像中，镜头光学分辨率必须高于传感器奈奎斯特频率，否则产生混叠（Aliasing）。",
    assumption="方形像素，无抗混叠滤波器，忽略镜头MTF在截止频率外的衰减。",
    domain="all",
    compute_fn=nyquist_match,
)

# ─── 传感器覆盖检查 ───
sensor_coverage = OpticalFormula(
    id="sensor_coverage",
    name_cn="传感器覆盖检查",
    expression="coverage_ratio = (image_circle / sensor_diag)²",
    latex=r"\text{coverage\_ratio} = \left(\frac{\text{image\_circle}}{\text{sensor\_diag}}\right)^2",
    params=[
        FormulaParam("sensor_w_mm", "传感器宽度", "mm"),
        FormulaParam("sensor_h_mm", "传感器高度", "mm"),
        FormulaParam("image_circle_mm", "像圈直径", "mm", "镜头能均匀成像的圆形区域直径"),
    ],
    outputs=["coverage_ratio", "vignetting", "fully_covered", "margin"],
    principle="镜头像圈必须大于或等于传感器对角线，否则传感器四角无法接收到足够光线，产生渐晕（暗角）。覆盖比定义为像圈面积与传感器面积之比。",
    assumption="像圈内部亮度均匀，忽略轴外透过率下降。",
    domain="all",
    compute_fn=sensor_coverage_check,
)

# ─── 景深计算 ───
depth_of_field = OpticalFormula(
    id="depth_of_field",
    name_cn="景深计算",
    expression="H = f² / (F × c) + f;  near = H×d / (H+d);  far = H×d / (H−d)",
    latex=r"H = \frac{f^2}{F \cdot c} + f; \quad d_{\text{near}} = \frac{H \cdot d}{H+d}; \quad d_{\text{far}} = \frac{H \cdot d}{H-d}",
    params=[
        FormulaParam("focal", "焦距", "mm"),
        FormulaParam("f_number", "F值", "", "光圈值"),
        FormulaParam("coc_diameter", "弥散圆直径", "mm", "可接受的最大模糊圆直径"),
        FormulaParam("focus_distance", "对焦距离", "mm"),
    ],
    outputs=["near_limit", "far_limit"],
    principle="景深是指在像平面上保持可接受清晰度的物距范围。由超焦距公式推导，光圈越小（F值越大）、焦距越短、弥散圆直径越大，景深越大。",
    assumption="圆孔衍射，弥散圆直径由人眼分辨能力或传感器像素尺寸决定。",
    domain="all",
    compute_fn=ThinLensCalculator.depth_of_field,
)

# ─── 接口兼容性 ───
mount_compatibility = OpticalFormula(
    id="mount_compatibility",
    name_cn="接口兼容性",
    expression="兼容 = mount_lens == mount_detector 或 存在标准转接方案",
    latex=r"\text{兼容} = \text{mount}_{\text{lens}} = \text{mount}_{\text{det}}",
    params=[
        FormulaParam("lens_mount", "镜头接口", ""),
        FormulaParam("det_mount", "探测器接口", ""),
    ],
    outputs=["compatible", "adapter_needed"],
    principle="镜头与相机的机械接口必须匹配，且法兰距（Flange Distance）必须一致，否则无法合焦。C-mount 与 CS-mount 可通过 5mm 垫片转换。",
    assumption="标准接口规格，无自定义改装。",
    domain="all",
    compute_fn=is_mount_compatible,
)

# ─── 像素精度 ───
pixel_accuracy = OpticalFormula(
    id="pixel_accuracy",
    name_cn="像素精度",
    expression="acc = pixel_size / β  [mm/px]",
    latex=r"\text{acc} = \frac{p_{\text{size}}}{\beta} \; [\text{mm/px}]",
    params=[
        FormulaParam("pixel_size_um", "像元尺寸", "μm"),
        FormulaParam("magnification", "放大倍率", "", "系统总放大倍率"),
    ],
    outputs=["pixel_accuracy_mm"],
    principle="每个像素对应的物理尺寸。放大倍率越大，单位像素代表的物理尺寸越小，系统分辨率越高。",
    assumption="无亚像素处理，理想成像。",
    domain="industrial",
    compute_fn=lambda pixel_size_um, magnification: round(pixel_size_um / 1000 / magnification, 6) if magnification else None,
)


# ─── 全局注册表 ───
ALL_FORMULAS: list[OpticalFormula] = [
    thin_lens_imaging,
    magnification,
    fov_from_focal,
    afov_from_focal,
    nyquist_sampling,
    sensor_coverage,
    depth_of_field,
    mount_compatibility,
    pixel_accuracy,
]


def get_formula_by_id(fid: str) -> OpticalFormula | None:
    """通过 ID 查询公式."""
    for f in ALL_FORMULAS:
        if f.id == fid:
            return f
    return None


def list_formulas(domain: str | None = None) -> list[OpticalFormula]:
    """列出公式，可选按领域过滤."""
    if domain is None or domain == "all":
        return ALL_FORMULAS
    return [f for f in ALL_FORMULAS if f.domain in ("all", domain)]
