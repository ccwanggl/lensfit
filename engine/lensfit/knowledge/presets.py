"""专业预设配置方案 — 行业推荐镜头-传感器配对.

每个预设代表一个经过验证的典型应用场景配置，包含推荐参数、
镜头规格、传感器规格及专业备注。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PresetConfig:
    """专业预设配置."""

    id: str
    name_cn: str
    name_en: str
    domain: str  # "industrial" | "photography" | "microscope" | "infrared"
    description: str
    difficulty: str = "intermediate"  # "beginner" | "intermediate" | "professional"
    # 输入参数（对应各 domain 的 Parameters）
    params: dict[str, Any] = field(default_factory=dict)
    # 推荐镜头规格（不要求 catalog 中存在，仅作参考）
    lens_recommendations: list[dict[str, Any]] = field(default_factory=list)
    # 推荐传感器规格
    detector_recommendations: list[dict[str, Any]] = field(default_factory=list)
    # 专业备注
    notes: str = ""
    # 相关行业标准
    standards: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name_cn": self.name_cn,
            "name_en": self.name_en,
            "domain": self.domain,
            "description": self.description,
            "difficulty": self.difficulty,
            "params": self.params,
            "lens_recommendations": self.lens_recommendations,
            "detector_recommendations": self.detector_recommendations,
            "notes": self.notes,
            "standards": self.standards,
        }


# ═══════════════════════════════════════════════════════════════════════
# 工业视觉 — Industrial Vision
# ═══════════════════════════════════════════════════════════════════════

PRESET_INDUSTRIAL_PCB_SMT = PresetConfig(
    id="industrial_pcb_smt",
    name_cn="PCB SMT 焊点检测",
    name_en="PCB SMT Solder Joint Inspection",
    domain="industrial",
    description="针对 PCB 表面贴装焊点的高精度检测方案，要求亚像素级精度和低畸变。",
    difficulty="professional",
    params={
        "sensor_format": "2/3",
        "pixel_size_um": 3.45,
        "resolution": "5MP",
        "target_fov_w_mm": 20.0,
        "target_fov_h_mm": 15.0,
        "working_distance_mm": 150.0,
        "mount_type": "C-mount",
        "required_accuracy_mm": 0.01,
        "max_distortion_percent": 0.5,
        "lighting_type": " coaxial",
    },
    lens_recommendations=[
        {
            "type": "telecentric",
            "focal_length_mm": 35.0,
            "working_distance_mm": 150.0,
            "distortion_percent": 0.05,
            "mtf50_lpmm": 120.0,
            "notes": "双远心镜头可消除透视畸变，保证测量精度",
        },
        {
            "type": "macro",
            "focal_length_mm": 50.0,
            "working_distance_mm": 100.0,
            "distortion_percent": 0.3,
            "notes": "备选：高分辨率微距镜头，成本较低",
        },
    ],
    detector_recommendations=[
        {
            "model": "Sony IMX250 / 2/3\" 5MP",
            "resolution": "2448×2048",
            "pixel_size_um": 3.45,
            "sensor_format": "2/3",
            "mount_type": "C-mount",
            "notes": "全局快门，高动态范围，适合高速产线",
        },
        {
            "model": "Sony IMX264 / 2/3\" 5MP",
            "resolution": "2448×2048",
            "pixel_size_um": 3.45,
            "sensor_format": "2/3",
            "mount_type": "C-mount",
            "notes": "Pregius 技术，低噪声，适合弱光环境",
        },
    ],
    notes=(
        "PCB 焊点检测的核心矛盾是分辨率与景深。"
        "推荐像素精度 ≤ 10μm，即 0.01mm/px。"
        "双远心镜头可消除透视误差，但成本较高（¥8,000–20,000）。"
        "若预算有限，可选用低畸变微距镜头 + 软件标定补偿。"
    ),
    standards=["IPC-A-610", "IPC-J-STD-001"],
)

PRESET_INDUSTRIAL_LARGE_PART = PresetConfig(
    id="industrial_large_part",
    name_cn="大型零部件尺寸测量",
    name_en="Large Part Dimensional Measurement",
    domain="industrial",
    description="汽车/航空大型零部件（>200mm）的高精度尺寸测量，兼顾大视场与精度。",
    difficulty="intermediate",
    params={
        "sensor_format": "1.1",
        "pixel_size_um": 3.2,
        "resolution": "12MP",
        "target_fov_w_mm": 300.0,
        "target_fov_h_mm": 200.0,
        "working_distance_mm": 800.0,
        "mount_type": "F-mount",
        "required_accuracy_mm": 0.05,
        "max_distortion_percent": 1.0,
    },
    lens_recommendations=[
        {
            "type": "large_format",
            "focal_length_mm": 50.0,
            "image_circle_mm": 22.0,
            "distortion_percent": 0.5,
            "notes": "大靶面镜头覆盖 1.1\" 传感器，像圈 ≥ 17.6mm",
        },
        {
            "type": "large_format",
            "focal_length_mm": 35.0,
            "image_circle_mm": 28.0,
            "notes": "更广角，适合更大视场或更近工作距离",
        },
    ],
    detector_recommendations=[
        {
            "model": "Sony IMX304 / 1.1\" 12MP",
            "resolution": "4096×3000",
            "pixel_size_um": 3.2,
            "sensor_format": "1.1",
            "mount_type": "F-mount",
            "notes": "大靶面高分辨率，适合大视场精密测量",
        },
    ],
    notes=(
        "大型零件测量需特别注意镜头像圈覆盖。"
        "1.1\" 传感器对角线约 17.6mm，要求镜头像圈 ≥ 18mm。"
        "工作距离较长时（>500mm），建议选用抗震性能好的镜头结构。"
    ),
    standards=["ISO 10360", "VDI/VDE 2634"],
)

PRESET_INDUSTRIAL_HIGH_SPEED = PresetConfig(
    id="industrial_high_speed",
    name_cn="高速产线缺陷检测",
    name_en="High-Speed Production Line Inspection",
    domain="industrial",
    description="饮料瓶、食品包装等高速产线（>500 瓶/分钟）的在线缺陷检测。",
    difficulty="intermediate",
    params={
        "sensor_format": "1/2",
        "pixel_size_um": 4.5,
        "resolution": "2MP",
        "target_fov_w_mm": 80.0,
        "target_fov_h_mm": 60.0,
        "working_distance_mm": 300.0,
        "mount_type": "C-mount",
        "required_accuracy_mm": 0.1,
        "max_distortion_percent": 2.0,
        "max_fps": 500,
    },
    lens_recommendations=[
        {
            "type": "standard",
            "focal_length_mm": 25.0,
            "distortion_percent": 1.0,
            "notes": "标准 C-mount 工业镜头，性价比高",
        },
    ],
    detector_recommendations=[
        {
            "model": "Sony IMX392 / 1/2\" 2.3MP",
            "resolution": "1920×1200",
            "pixel_size_um": 4.5,
            "sensor_format": "1/2",
            "mount_type": "C-mount",
            "max_fps": 500,
            "notes": "Pregius S 技术，高帧率全局快门",
        },
    ],
    notes=(
        "高速检测的关键是全局快门 + 短曝光。"
        "建议搭配频闪光源（Strobe），曝光时间 < 50μs 冻结运动。"
        "接口优先选 10GigE 或 CoaXPress，避免带宽瓶颈。"
    ),
    standards=["ISO 9001"],
)

# ═══════════════════════════════════════════════════════════════════════
# 摄影 — Photography
# ═══════════════════════════════════════════════════════════════════════

PRESET_PHOTO_PORTRAIT = PresetConfig(
    id="photo_portrait_85",
    name_cn="人像摄影（85mm 定焦）",
    name_en="Portrait Photography (85mm Prime)",
    domain="photography",
    description="经典人像焦段，提供自然透视和优美背景虚化（bokeh）。",
    difficulty="beginner",
    params={
        "sensor_format": "Full Frame",
        "focal_length_mm": 85.0,
        "max_aperture": 1.8,
        "subject_distance_m": 2.5,
        "creative_style": "bokeh",
    },
    lens_recommendations=[
        {
            "model": "85mm f/1.4 GM / Art",
            "max_aperture": 1.4,
            "notes": "顶级人像头，焦外如奶油般化开",
        },
        {
            "model": "85mm f/1.8",
            "max_aperture": 1.8,
            "notes": "性价比之选，重量轻便，适合户外人像",
        },
    ],
    detector_recommendations=[
        {
            "model": "Full Frame 24–45MP",
            "sensor_format": "Full Frame",
            "notes": "全画幅保证足够的像素密度和动态范围",
        },
    ],
    notes=(
        "85mm 被称为『人像镜皇』，因其透视接近人眼单眼视角，"
        "且在中距离（2–3m）拍摄时能保持自然的面部比例。"
        "f/1.4–f/2.8 可获得浅景深，突出主体。"
    ),
    standards=[],
)

PRESET_PHOTO_LANDSCAPE = PresetConfig(
    id="photo_landscape_wide",
    name_cn="风光摄影（广角）",
    name_en="Landscape Photography (Wide Angle)",
    domain="photography",
    description="大场景风光摄影，要求大景深、高分辨率和低畸变。",
    difficulty="intermediate",
    params={
        "sensor_format": "Full Frame",
        "focal_length_mm": 16.0,
        "max_aperture": 2.8,
        "subject_distance_m": 5.0,
        "creative_style": "sharp",
    },
    lens_recommendations=[
        {
            "model": "16–35mm f/2.8 GM / Z",
            "focal_length_mm": 16.0,
            "max_aperture": 2.8,
            "notes": "顶级广角变焦，边缘画质优异",
        },
        {
            "model": "14mm f/1.8 GM / Art",
            "focal_length_mm": 14.0,
            "max_aperture": 1.8,
            "notes": "超广角定焦，适合星空和建筑",
        },
    ],
    detector_recommendations=[
        {
            "model": "Full Frame 40–60MP",
            "sensor_format": "Full Frame",
            "notes": "高像素保证大幅面打印和裁切空间",
        },
    ],
    notes=(
        "风光摄影通常使用小光圈（f/8–f/11）获得最大景深。"
        "超焦距对焦技巧：对焦在超焦距距离，使前景到无限远都清晰。"
        "建议使用三脚架 + 快门线，避免机震。"
    ),
    standards=[],
)

PRESET_PHOTO_MACRO = PresetConfig(
    id="photo_macro_100",
    name_cn="微距摄影（1:1 百微）",
    name_en="Macro Photography (1:1 100mm)",
    domain="photography",
    description="昆虫、花卉、珠宝等微距题材，要求 1:1 放大倍率和长工作距离。",
    difficulty="intermediate",
    params={
        "sensor_format": "Full Frame",
        "focal_length_mm": 100.0,
        "max_aperture": 2.8,
        "subject_distance_m": 0.3,
        "creative_style": "sharp",
    },
    lens_recommendations=[
        {
            "model": "100mm f/2.8 Macro",
            "magnification": 1.0,
            "working_distance_mm": 150.0,
            "notes": "经典百微，1:1 放大，工作距离适中",
        },
        {
            "model": "90mm f/2.8 Macro",
            "magnification": 1.0,
            "notes": "轻量化替代方案",
        },
    ],
    detector_recommendations=[
        {
            "model": "Full Frame 24–45MP",
            "sensor_format": "Full Frame",
            "notes": "高像素捕捉微小细节",
        },
    ],
    notes=(
        "微距摄影景深极浅（mm 级），常需焦点包围（Focus Stacking）。"
        "建议使用环形闪光灯或双头闪光灯补光。"
        "100mm 微距比 50mm/60mm 工作距离更长，不易惊扰昆虫。"
    ),
    standards=[],
)

# ═══════════════════════════════════════════════════════════════════════
# 显微镜 — Microscopy
# ═══════════════════════════════════════════════════════════════════════

PRESET_MICRO_BIOLOGICAL = PresetConfig(
    id="micro_bio_brightfield",
    name_cn="生物明场观察",
    name_en="Biological Brightfield Microscopy",
    domain="microscope",
    description="常规生物切片明场观察，如 HE 染色组织切片。",
    difficulty="beginner",
    params={
        "microscope_type": "compound",
        "magnification": 400.0,
        "objective_na": 0.65,
        "sensor_format": "1/1.8",
        "pixel_size_um": 2.4,
        "resolution": "5MP",
    },
    lens_recommendations=[
        {
            "model": "Plan Achromat 10×/0.25 + 40×/0.65",
            "na": 0.65,
            "working_distance_mm": 0.6,
            "notes": "平场消色差物镜，性价比高，适合教学",
        },
        {
            "model": "Plan Apo 40×/0.95",
            "na": 0.95,
            "notes": "平场复消色差，更高分辨率，适合研究",
        },
    ],
    detector_recommendations=[
        {
            "model": "1/1.8\" 5MP 彩色相机",
            "resolution": "2592×1944",
            "pixel_size_um": 2.4,
            "sensor_format": "1/1.8",
            "notes": "彩色相机适合明场和相差观察",
        },
    ],
    notes=(
        "生物明场的标准配置是 10×/0.25 和 40×/0.65 物镜。"
        "总放大倍率 = 物镜倍率 × 目镜倍率（通常 10×）。"
        "数码显微镜的总放大倍率 = 物镜 × 相机适配器倍率 × (显示器对角线 / 传感器对角线)。"
        "NA 0.65 时，光学分辨率约 0.4μm（绿光 550nm）。"
    ),
    standards=["ISO 8037", "ISO 8578"],
)

PRESET_MICRO_FLUORESCENCE = PresetConfig(
    id="micro_fluorescence",
    name_cn="荧光显微成像（GFP）",
    name_en="Fluorescence Microscopy (GFP)",
    domain="microscope",
    description="GFP 等绿色荧光蛋白的激发与成像，要求高 NA 和 cooled 相机。",
    difficulty="professional",
    params={
        "microscope_type": "compound",
        "magnification": 600.0,
        "objective_na": 1.4,
        "sensor_format": "2/3",
        "pixel_size_um": 6.5,
        "resolution": "1.4MP",
    },
    lens_recommendations=[
        {
            "model": "Plan Apo 60×/1.40 Oil",
            "na": 1.4,
            "immersion": "oil",
            "working_distance_mm": 0.21,
            "notes": "油浸物镜，NA 1.4 接近可见光理论极限",
        },
        {
            "model": "Plan Apo 40×/1.30 Oil",
            "na": 1.3,
            "immersion": "oil",
            "notes": "稍低倍率，更大视场",
        },
    ],
    detector_recommendations=[
        {
            "model": "科学级 CMOS（sCMOS）单色",
            "resolution": "2048×2048",
            "pixel_size_um": 6.5,
            "sensor_format": "2/3",
            "read_noise_e": 1.0,
            "notes": "制冷 sCMOS，低噪声，适合弱光荧光",
        },
        {
            "model": "EMCCD",
            "resolution": "512×512",
            "notes": "单分子检测级灵敏度，但成本高、速度慢",
        },
    ],
    notes=(
        "荧光成像的信噪比（SNR）是关键。"
        "NA 1.4 油浸物镜的集光能力 ≈ NA² = 1.96，是干镜（NA 0.75）的 3.5 倍。"
        "sCMOS 相机的读出噪声 < 2e⁻，远优于普通 CMOS（> 10e⁻）。"
        "GFP 激发峰 488nm，发射峰 509nm，需匹配滤光片组。"
    ),
    standards=["ISO 10934"],
)

PRESET_MICRO_STEREO = PresetConfig(
    id="micro_stereo",
    name_cn="体视显微镜（解剖/装配）",
    name_en="Stereo Microscope (Dissection/Assembly)",
    domain="microscope",
    description="电路板返修、解剖、精密装配等需要大工作距离和立体视觉的场景。",
    difficulty="beginner",
    params={
        "microscope_type": "stereo",
        "magnification": 40.0,
        "objective_na": 0.1,
        "sensor_format": "1/2.3",
        "pixel_size_um": 1.55,
        "resolution": "12MP",
    },
    lens_recommendations=[
        {
            "model": "Zoom Body 0.7–4.5× + 10× Eyepiece",
            "zoom_range": "0.7–4.5×",
            "total_mag": "7–45×",
            "working_distance_mm": 110.0,
            "notes": "标准体视变焦主体，工作距离 110mm",
        },
        {
            "model": "Zoom Body 0.63–5.0× + 10× Eyepiece",
            "zoom_range": "0.63–5.0×",
            "total_mag": "6.3–50×",
            "working_distance_mm": 150.0,
            "notes": "长工作距离版本，适合操作空间大的场景",
        },
    ],
    detector_recommendations=[
        {
            "model": "1/2.3\" 12MP 彩色相机",
            "resolution": "4000×3000",
            "pixel_size_um": 1.55,
            "sensor_format": "1/2.3",
            "notes": "高像素捕捉细节，适合记录和教学",
        },
    ],
    notes=(
        "体视显微镜的总放大倍率 = 变焦倍率 × 目镜倍率。"
        "10× 目镜是最常用配置，可换 15× 或 20× 提高倍率但减小视野。"
        "工作距离（WD）是体视显微镜的关键指标，决定操作空间。"
        "三目接口可外接相机，但会损失部分光强（约 20%）。"
    ),
    standards=["ISO 8036"],
)

# ═══════════════════════════════════════════════════════════════════════
# 红外成像 — Infrared
# ═══════════════════════════════════════════════════════════════════════

PRESET_IR_THERMAL = PresetConfig(
    id="ir_thermal_lwir",
    name_cn="热成像（非制冷 LWIR）",
    name_en="Thermal Imaging (Uncooled LWIR)",
    domain="infrared",
    description="工业测温、安防监控、建筑热桥检测等长波红外应用。",
    difficulty="intermediate",
    params={
        "spectral_band": "LWIR",
        "wavelength_min_um": 8.0,
        "wavelength_max_um": 14.0,
        "sensor_format": "1/2",
        "pixel_size_um": 12.0,
        "resolution": "640×512",
        "required_accuracy_mK": 50.0,
        "focal_length_mm": 19.0,
    },
    lens_recommendations=[
        {
            "model": "19mm f/1.0 LWIR",
            "focal_length_mm": 19.0,
            "f_number": 1.0,
            "material": "Germanium",
            "notes": "标准视场，Ge 透镜透过率 > 90%@8–14μm",
        },
        {
            "model": "13mm f/1.0 LWIR",
            "focal_length_mm": 13.0,
            "f_number": 1.0,
            "notes": "广角版本，适合建筑检测和狭小空间",
        },
    ],
    detector_recommendations=[
        {
            "model": "VOx Microbolometer 640×512",
            "resolution": "640×512",
            "pixel_size_um": 12.0,
            "netd_mk": 40.0,
            "spectral_range": "8–14μm",
            "notes": "非制冷氧化钒微测辐射热计，NETD < 50mK",
        },
        {
            "model": "VOx Microbolometer 384×288",
            "resolution": "384×288",
            "pixel_size_um": 17.0,
            "netd_mk": 60.0,
            "notes": "经济型，适合预算敏感项目",
        },
    ],
    notes=(
        "LWIR（8–14μm）镜头必须使用锗（Ge）、硒化锌（ZnSe）或硫系玻璃，"
        "普通光学玻璃在此波段不透明。"
        "非制冷探测器 NETD 典型值 30–60mK，制冷型（MCT）可达 < 20mK 但成本高。"
        "发射率校正和反射干扰是测温精度的主要挑战。"
    ),
    standards=["ISO 18434-1", "NFPA 70B"],
)

PRESET_IR_SWIR = PresetConfig(
    id="ir_swir_inspection",
    name_cn="SWIR 硅片/水分检测",
    name_en="SWIR Silicon Wafer/Moisture Inspection",
    domain="infrared",
    description="半导体硅片内部缺陷检测、农产品水分含量检测等短波红外应用。",
    difficulty="professional",
    params={
        "spectral_band": "SWIR",
        "wavelength_min_um": 0.9,
        "wavelength_max_um": 1.7,
        "sensor_format": "1/2",
        "pixel_size_um": 5.0,
        "resolution": "640×512",
        "required_accuracy_mK": None,
        "focal_length_mm": 25.0,
    },
    lens_recommendations=[
        {
            "model": "25mm f/1.4 SWIR",
            "focal_length_mm": 25.0,
            "f_number": 1.4,
            "material": "CaF₂ + Glass",
            "notes": "复消色差 SWIR 镜头，覆盖 900–1700nm",
        },
    ],
    detector_recommendations=[
        {
            "model": "InGaAs 640×512",
            "resolution": "640×512",
            "pixel_size_um": 5.0,
            "spectral_range": "0.9–1.7μm",
            "notes": "制冷型 InGaAs，量子效率 > 80%@1.0–1.6μm",
        },
    ],
    notes=(
        "SWIR 波段（0.9–1.7μm）对硅是半透明的，可检测晶圆内部缺陷和应力。"
        "水在 1450nm 和 1940nm 有强吸收峰，SWIR 可用于水分定量检测。"
        "InGaAs 探测器需要热电制冷（TEC）以降低暗电流。"
        "镜头需特殊镀膜（SWIR AR Coating）以减少反射损失。"
    ),
    standards=["SEMI M59", "ASTM E1652"],
)

# ═══════════════════════════════════════════════════════════════════════
# 全局注册表
# ═══════════════════════════════════════════════════════════════════════

ALL_PRESETS: list[PresetConfig] = [
    # Industrial
    PRESET_INDUSTRIAL_PCB_SMT,
    PRESET_INDUSTRIAL_LARGE_PART,
    PRESET_INDUSTRIAL_HIGH_SPEED,
    # Photography
    PRESET_PHOTO_PORTRAIT,
    PRESET_PHOTO_LANDSCAPE,
    PRESET_PHOTO_MACRO,
    # Microscopy
    PRESET_MICRO_BIOLOGICAL,
    PRESET_MICRO_FLUORESCENCE,
    PRESET_MICRO_STEREO,
    # Infrared
    PRESET_IR_THERMAL,
    PRESET_IR_SWIR,
]


def list_presets(domain: str | None = None) -> list[PresetConfig]:
    """列出预设，可选按领域过滤."""
    if domain is None or domain == "all":
        return ALL_PRESETS
    return [p for p in ALL_PRESETS if p.domain == domain]


def get_preset_by_id(pid: str) -> PresetConfig | None:
    """通过 ID 查询预设."""
    for p in ALL_PRESETS:
        if p.id == pid:
            return p
    return None
