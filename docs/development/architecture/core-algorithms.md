# 光学匹配核心算法设计

## 1. 算法体系总览

整个匹配引擎由三大算法层组成：

```
┌─────────────────────────────────────────────┐
│  Layer 3: 智能决策层                           │
│  - 多目标优化 (Pareto / TOPSIS)                │
│  - 约束满足问题 (CSP) 求解                      │
│  - 评分排序引擎                               │
├─────────────────────────────────────────────┤
│  Layer 2: 物理匹配层                           │
│  - 几何光学匹配 (FOV/WD/焦距/NA)               │
│  - 物理光学匹配 (MTF/Nyquist/衍射极限)          │
│  - 光谱匹配 (波段重叠/QE加权)                   │
│  - 机械匹配 (接口/法兰距/像面尺寸)               │
├─────────────────────────────────────────────┤
│  Layer 1: 基础计算层                           │
│  - 薄透镜公式 / 高斯光学                        │
│  - 传感器参数换算                               │
│  - 单位换算与标准化                             │
└─────────────────────────────────────────────┘
```

---

## 2. Layer 1: 基础计算层

### 2.1 传感器标准化计算

传感器尺寸行业惯例用"英寸"表示（如 1/2", 2/3"），但这是**对角线的名义值**，实际尺寸需查表或按经验公式计算。

```python
# 传感器尺寸标准化（对角线名义值 → 实际物理尺寸）
SENSOR_FORMAT_TABLE = {
    "1/4":   {"diag": 4.00,  "w": 3.20,  "h": 2.40,  "aspect": 4/3},
    "1/3":   {"diag": 6.00,  "w": 4.80,  "h": 3.60,  "aspect": 4/3},
    "1/2.3": {"diag": 7.70,  "w": 6.16,  "h": 4.62,  "aspect": 4/3},
    "1/2":   {"diag": 8.00,  "w": 6.40,  "h": 4.80,  "aspect": 4/3},
    "1/1.8": {"diag": 8.93,  "w": 7.18,  "h": 5.32,  "aspect": 4/3},
    "2/3":   {"diag": 11.00, "w": 8.80,  "h": 6.60,  "aspect": 4/3},
    "1":     {"diag": 16.00, "w": 12.80, "h": 9.60,  "aspect": 4/3},
    "4/3":   {"diag": 22.50, "w": 17.30, "h": 13.00, "aspect": 4/3},
    "APS-C": {"diag": 28.30, "w": 22.30, "h": 14.90, "aspect": 3/2},
    "Full Frame": {"diag": 43.30, "w": 36.00, "h": 24.00, "aspect": 3/2},
}

# 当只有分辨率+像元尺寸时
def sensor_size_from_pixels(width_px, height_px, pixel_size_um):
    """从像素数和像元尺寸计算传感器物理尺寸"""
    w_mm = width_px * pixel_size_um / 1000
    h_mm = height_px * pixel_size_um / 1000
    diag_mm = (w_mm**2 + h_mm**2) ** 0.5
    return {"w": w_mm, "h": h_mm, "diag": diag_mm}
```

### 2.2 薄透镜核心公式库

```python
import math
from dataclasses import dataclass
from typing import Optional, Tuple

@dataclass
class OpticalParams:
    """光学系统核心参数"""
    focal_length: Optional[float] = None      # 焦距 f (mm)
    working_distance: Optional[float] = None  # 工作距离 WD (mm)
    fov_w: Optional[float] = None             # 水平视场 (mm)
    fov_h: Optional[float] = None             # 垂直视场 (mm)
    sensor_w: Optional[float] = None          # 传感器水平尺寸 (mm)
    sensor_h: Optional[float] = None          # 传感器垂直尺寸 (mm)
    magnification: Optional[float] = None     # 放大倍率 β
    afov_h: Optional[float] = None            # 水平视角 (°)
    afov_v: Optional[float] = None            # 垂直视角 (°)
    extension: Optional[float] = None         # 延长环长度 (mm)

class ThinLensCalculator:
    """薄透镜公式计算器 - 支持已知任意2-3个参数，推导其余参数"""
    
    @staticmethod
    def focal_from_wd_fov(wd: float, fov: float, sensor: float) -> float:
        """
        已知工作距离和视场，求焦距
        精确公式: f = (WD * sensor) / (FOV + sensor)
        近似公式(物距>>传感器时): f ≈ WD * sensor / FOV
        """
        return (wd * sensor) / (fov + sensor)
    
    @staticmethod
    def fov_from_wd_focal(wd: float, focal: float, sensor: float) -> float:
        """已知工作距离和焦距，求视场"""
        return (wd * sensor) / focal - sensor
    
    @staticmethod
    def wd_from_fov_focal(fov: float, focal: float, sensor: float) -> float:
        """已知视场和焦距，求工作距离"""
        return focal * (fov + sensor) / sensor
    
    @staticmethod
    def magnification_from_focal_wd(focal: float, wd: float) -> float:
        """放大倍率 β = f / WD (当 WD >> f 时近似)"""
        # 精确值: β = sensor_size / FOV = f / (WD - f)
        if wd <= focal:
            raise ValueError("工作距离必须大于焦距")
        return focal / (wd - focal)
    
    @staticmethod
    def afov_from_sensor_focal(sensor: float, focal: float) -> float:
        """视角计算: AFOV = 2 * arctan(sensor / (2*f))"""
        return 2 * math.degrees(math.atan(sensor / (2 * focal)))
    
    @staticmethod
    def focal_with_extension(nominal_focal: float, extension: float) -> float:
        """
        加入延长环后的有效焦距变化
        1/f_eff = 1/f_nominal + 1/extension (近似)
        更精确需用透镜公式
        """
        if extension <= 0:
            return nominal_focal
        # 近摄时: 放大倍率 m = extension / f
        # 有效工作距离和视场均会变化
        return nominal_focal  # 实际计算需结合具体系统
    
    def solve(self, params: OpticalParams) -> OpticalParams:
        """
        智能求解器：根据已知参数自动推导未知参数
        规则引擎：按照参数组合优先级依次尝试求解
        """
        result = OpticalParams()
        # 拷贝已知值
        for field in params.__dataclass_fields__:
            setattr(result, field, getattr(params, field))
        
        changed = True
        max_iter = 10
        iteration = 0
        
        while changed and iteration < max_iter:
            changed = False
            iteration += 1
            
            # Rule 1: 已知 WD + sensor + FOV → focal
            if result.focal_length is None and all(v is not None for v in 
                    [result.working_distance, result.sensor_w, result.fov_w]):
                result.focal_length = self.focal_from_wd_fov(
                    result.working_distance, result.fov_w, result.sensor_w)
                changed = True
            
            # Rule 2: 已知 focal + sensor → AFOV
            if result.afov_h is None and all(v is not None for v in 
                    [result.sensor_w, result.focal_length]):
                result.afov_h = self.afov_from_sensor_focal(
                    result.sensor_w, result.focal_length)
                changed = True
            
            # Rule 3: 已知 focal + WD → magnification
            if result.magnification is None and all(v is not None for v in 
                    [result.focal_length, result.working_distance]):
                result.magnification = self.magnification_from_focal_wd(
                    result.focal_length, result.working_distance)
                changed = True
            
            # ... 更多规则可扩展
        
        return result
```

### 2.3 景深计算

```python
def depth_of_field(focal: float, f_number: float, 
                   coc_diameter: float, focus_distance: float) -> Tuple[float, float]:
    """
    景深计算
    
    Args:
        focal: 焦距 (mm)
        f_number: F数
        coc_diameter: 容许弥散圆直径 (mm)
                      通常取 2-3 个像素尺寸，或 sensor_diag / 1500
        focus_distance: 对焦距离 (mm)
    
    Returns:
        (near_limit, far_limit) 景深近端/远端 (mm)
    """
    # 超焦距 H = f^2 / (N * c) + f
    hyperfocal = (focal ** 2) / (f_number * coc_diameter) + focal
    
    # 前景深 ΔL1 = (H * s) / (H + s)  [s = 对焦距离]
    near = (hyperfocal * focus_distance) / (hyperfocal + focus_distance)
    
    # 后景深 ΔL2 = (H * s) / (H - s)
    if focus_distance >= hyperfocal:
        far = float('inf')
    else:
        far = (hyperfocal * focus_distance) / (hyperfocal - focus_distance)
    
    return near, far
```

---

## 3. Layer 2: 物理匹配层

### 3.1 传感器-镜头像面覆盖匹配（核心算法）

这是防止渐晕的关键检查：

```python
def sensor_coverage_check(sensor_w: float, sensor_h: float, 
                          image_circle_diameter: float) -> dict:
    """
    检查传感器是否被镜头像圆完全覆盖
    
    Returns:
        {
            'fully_covered': bool,      # 是否完全覆盖
            'coverage_ratio': float,    # 传感器在像圆内的面积占比
            'vignetting': bool,         # 是否有渐晕
            'vignetting_corners': bool, # 四角是否渐晕
            'max_safe_sensor_diag': float  # 该镜头支持的最大传感器对角线
        }
    """
    sensor_diag = (sensor_w**2 + sensor_h**2) ** 0.5
    
    # 简单判定：传感器对角线 ≤ 像圆直径 → 安全
    fully_covered = sensor_diag <= image_circle_diameter
    
    # 精确覆盖面积比（传感器矩形与圆形相交面积）
    # 简化计算：使用对角线比例估算
    coverage_ratio = min(1.0, (image_circle_diameter / sensor_diag) ** 2)
    
    # 四角检查：传感器角点到圆心距离 > 像圆半径 → 角部渐晕
    corner_distance = (sensor_w/2)**2 + (sensor_h/2)**2
    vignetting_corners = corner_distance > (image_circle_diameter/2)**2
    
    return {
        'fully_covered': fully_covered,
        'coverage_ratio': coverage_ratio,
        'vignetting': not fully_covered,
        'vignetting_corners': vignetting_corners,
        'max_safe_sensor_diag': image_circle_diameter,
        'margin': (image_circle_diameter - sensor_diag) / image_circle_diameter
    }
```

### 3.2 奈奎斯特采样匹配（工业视觉+显微镜核心）

```python
def nyquist_match(pixel_size_um: float, na: float = None, 
                  lens_mtf50_lpmm: float = None, wavelength_um: float = 0.55) -> dict:
    """
    奈奎斯特采样匹配分析
    
    原理：镜头光学分辨率必须 ≥ 2× 传感器空间采样频率（奈奎斯特定理）
    
    Args:
        pixel_size_um: 像元尺寸 (μm)
        na: 数值孔径（显微镜场景）
        lens_mtf50_lpmm: 镜头MTF50 (线对/mm，工业镜头场景)
        wavelength_um: 工作波长 (μm)，默认可见光0.55
    
    Returns:
        {
            'sensor_nyquist_lpmm': float,     # 传感器奈奎斯特频率
            'optical_limit_lpmm': float,      # 光学极限分辨率
            'matched': bool,                  # 是否匹配
            'oversampling_ratio': float,      # 过采样率
            'recommendation': str             # 建议文本
        }
    """
    # 传感器奈奎斯特频率: 1/(2*pixel_size)
    sensor_nyquist = 1000 / (2 * pixel_size_um)  # lp/mm
    
    if na is not None:
        # 显微镜场景：阿贝衍射极限 d = 0.61*λ/NA
        # 对应空间频率 cutoff = 1/d = NA/(0.61*λ)
        optical_limit = na / (0.61 * wavelength_um)  # lp/mm
        optical_limit_description = f"衍射极限 (NA={na})"
    elif lens_mtf50_lpmm is not None:
        # 工业镜头场景：使用MTF50作为实际可用分辨率
        optical_limit = lens_mtf50_lpmm
        optical_limit_description = f"MTF50={lens_mtf50_lpmm} lp/mm"
    else:
        raise ValueError("必须提供NA或lens_mtf50_lpmm之一")
    
    # 过采样率 = 光学极限 / 奈奎斯特频率
    # > 1.0: 欠采样（镜头分辨率被传感器浪费）
    # 0.5~1.0: 理想匹配
    # < 0.5: 过采样（传感器能力被光学限制）
    oversampling = optical_limit / sensor_nyquist
    
    matched = 0.5 <= oversampling <= 1.2  # 允许一定裕量
    
    if oversampling > 1.2:
        rec = "镜头分辨率高于传感器，建议选用更小像元或更低倍率"
    elif oversampling < 0.5:
        rec = "传感器过采样，镜头光学分辨率不足，建议选用更高NA/MTF镜头"
    else:
        rec = "镜头与传感器匹配良好"
    
    return {
        'sensor_nyquist_lpmm': round(sensor_nyquist, 1),
        'optical_limit_lpmm': round(optical_limit, 1),
        'optical_limit_description': optical_limit_description,
        'matched': matched,
        'oversampling_ratio': round(oversampling, 2),
        'recommendation': rec
    }
```

### 3.3 光谱匹配算法（红外/多光谱场景）

> **实现状态**：独立的 `spectral_overlap()` 函数尚未创建；波段匹配逻辑分散在 `InfraredModule.calculate_derived` 和 `ScoringEngine._score_band_match` 中。

> **实现状态**：独立的 `spectral_overlap()` 函数尚未创建；波段匹配逻辑分散在 `InfraredModule.calculate_derived` 和 `ScoringEngine._score_band_match` 中。

> **实现状态**：独立的 `spectral_overlap()` 函数尚未创建；波段匹配逻辑分散在 `InfraredModule.calculate_derived` 和 `ScoringEngine._score_band_match` 中。

> **实现状态**：独立的 `spectral_overlap()` 函数尚未创建；波段匹配逻辑分散在 `InfraredModule.calculate_derived` 和 `ScoringEngine._score_band_match` 中。

```python
from typing import List, Tuple

def spectral_overlap(lens_band: Tuple[float, float], 
                     detector_qe: List[Tuple[float, float]],
                     source_spectrum: List[Tuple[float, float]] = None) -> dict:
    """
    光谱波段匹配分析
    
    Args:
        lens_band: 镜头透过波段 (λ_min, λ_max) nm
        detector_qe: 探测器QE曲线 [(λ, qe), ...]
        source_spectrum: 光源光谱 [(λ, intensity), ...] (可选)
    
    Returns:
        {
            'overlap_band': Tuple[float, float],  # 有效重叠波段
            'overlap_ratio': float,               # 波段重叠度 (0-1)
            'system_qe_max': float,               # 系统峰值QE
            'system_qe_avg': float,               # 系统平均QE（在重叠波段内）
            'signal_budget': float                # 预估信号量
        }
    """
    det_min = min(wl for wl, _ in detector_qe)
    det_max = max(wl for wl, _ in detector_qe)
    
    overlap_min = max(lens_band[0], det_min)
    overlap_max = min(lens_band[1], det_max)
    
    if overlap_min >= overlap_max:
        return {'overlap_band': None, 'overlap_ratio': 0, 
                'system_qe_max': 0, 'signal_budget': 0,
                'warning': '镜头波段与探测器响应无重叠！'}
    
    # 波段重叠度
    lens_range = lens_band[1] - lens_band[0]
    det_range = det_max - det_min
    overlap_range = overlap_max - overlap_min
    overlap_ratio = overlap_range / min(lens_range, det_range)
    
    # 计算重叠波段内的系统QE（镜头透过率×探测器QE）
    # 简化模型：假设镜头在通带内透过率=1，通带外=0
    system_qe_values = [qe for wl, qe in detector_qe 
                        if overlap_min <= wl <= overlap_max]
    
    system_qe_max = max(system_qe_values) if system_qe_values else 0
    system_qe_avg = sum(system_qe_values) / len(system_qe_values) if system_qe_values else 0
    
    return {
        'overlap_band': (overlap_min, overlap_max),
        'overlap_ratio': round(overlap_ratio, 2),
        'system_qe_max': round(system_qe_max, 3),
        'system_qe_avg': round(system_qe_avg, 3),
        'signal_budget': round(system_qe_avg * overlap_ratio, 3)
    }
```

### 3.4 显微镜 C-Mount 适配器匹配

> **实现状态**：独立的 `microscope_adapter_match()` 函数尚未创建；适配器相关计算在 `MicroscopeModule.calculate_derived` 中处理。当前也没有 `adapter_catalog` 表。

> **实现状态**：独立的 `microscope_adapter_match()` 函数尚未创建；适配器相关计算在 `MicroscopeModule.calculate_derived` 中处理。当前也没有 `adapter_catalog` 表。

> **实现状态**：独立的 `microscope_adapter_match()` 函数尚未创建；适配器相关计算在 `MicroscopeModule.calculate_derived` 中处理。当前也没有 `adapter_catalog` 表。

> **实现状态**：独立的 `microscope_adapter_match()` 函数尚未创建；适配器相关计算在 `MicroscopeModule.calculate_derived` 中处理。当前也没有 `adapter_catalog` 表。

```python
def microscope_adapter_match(objective_mag: float, eyepiece_mag: float,
                             sensor_diag_inch: float, 
                             field_number_mm: float = 22.0) -> dict:
    """
    显微镜 C-Mount 适配器匹配计算
    
    Args:
        objective_mag: 物镜标称倍率 (如 10x)
        eyepiece_mag: 目镜倍率 (如 10x)
        sensor_diag_inch: 传感器对角线英寸 (如 "1/2" → 0.5)
        field_number: 视场数 (mm)，标准常为 22mm 或 26.5mm
    
    Returns:
        {
            'intermediate_image_diameter': float,  # 中间像直径 (mm)
            'recommended_adapter': str,            # 推荐适配器倍率
            'camera_fov_mm': float,                # 相机实际视野 (mm)
            'eyepiece_fov_mm': float,              # 目镜视野 (mm)
            'fov_match_ratio': float,              # 视野匹配度
            'vignetting_risk': bool                # 渐晕风险
        }
    """
    # 中间像直径 = 视场数 / 物镜倍率
    intermediate_dia = field_number / objective_mag
    
    # 传感器物理对角线 (mm) ≈ 名义英寸 × 16mm (经验系数)
    sensor_diag_mm = sensor_diag_inch * 16.0
    
    # 推荐适配器倍率 ≈ 传感器名义尺寸（英寸值作为小数）
    # 例：1/2" → 0.5x，2/3" → 0.67x
    recommended_adapter = sensor_diag_inch
    
    # 相机实际视野 = 中间像直径 × 适配器倍率 / 物镜倍率
    # 简化：camera_fov = field_number × adapter / objective
    camera_fov = field_number * recommended_adapter / objective_mag
    
    # 目镜视野（参考）
    eyepiece_fov = field_number / objective_mag
    
    # 视野匹配度
    fov_ratio = camera_fov / eyepiece_fov
    
    # 渐晕风险：中间像直径 × 适配器 < 传感器对角线
    projected_image_dia = intermediate_dia * recommended_adapter
    vignetting = projected_image_dia < sensor_diag_mm
    
    return {
        'intermediate_image_diameter': round(intermediate_dia, 2),
        'recommended_adapter': f"{recommended_adapter:.2f}x",
        'camera_fov_mm': round(camera_fov, 3),
        'eyepiece_fov_mm': round(eyepiece_fov, 3),
        'fov_match_ratio': round(fov_ratio, 2),
        'vignetting_risk': vignetting,
        'safe_adapter_range': (sensor_diag_mm / intermediate_dia * 0.9,
                               sensor_diag_mm / intermediate_dia * 1.1)
    }
```

---

## 4. Layer 3: 智能决策层

### 4.1 约束满足问题 (CSP) 建模

将匹配问题建模为约束满足问题：

```python
from dataclasses import dataclass
from typing import Callable, List, Any

@dataclass
class Constraint:
    name: str
    check: Callable[[Any], bool]  # 约束检查函数
    weight: float = 1.0           # 约束权重（硬约束=∞）
    hard: bool = False            # 是否为硬约束（不可违反）

class MatchingCSP:
    """镜头-探测器匹配的约束满足问题求解器"""
    
    def __init__(self):
        self.constraints: List[Constraint] = []
        self.candidates: List[Any] = []  # 候选器件组合
    
    def add_hard_constraint(self, name: str, check_fn: Callable):
        """添加硬约束（必须满足，否则直接淘汰）"""
        self.constraints.append(Constraint(name, check_fn, weight=float('inf'), hard=True))
    
    def add_soft_constraint(self, name: str, check_fn: Callable, weight: float = 1.0):
        """添加软约束（满足度影响评分）"""
        self.constraints.append(Constraint(name, check_fn, weight=weight, hard=False))
    
    def filter_candidates(self, candidates: List[Any]) -> List[Any]:
        """用硬约束过滤候选集"""
        valid = []
        for candidate in candidates:
            if all(c.check(candidate) for c in self.constraints if c.hard):
                valid.append(candidate)
        return valid
    
    def score_candidate(self, candidate: Any) -> float:
        """计算候选组合的软约束满足得分"""
        score = 0.0
        for c in self.constraints:
            if not c.hard:
                satisfaction = float(c.check(candidate))  # 可扩展为连续满足度
                score += satisfaction * c.weight
        return score
```

### 4.2 预定义约束库

```python
def build_standard_constraints(requirements: dict) -> MatchingCSP:
    """构建标准工业视觉场景的约束集"""
    csp = MatchingCSP()
    
    # ===== 硬约束 =====
    
    # H1: 像面尺寸 ≥ 传感器尺寸（无渐晕）
    csp.add_hard_constraint(
        "sensor_coverage",
        lambda combo: combo.lens.image_circle >= combo.detector.diag * 1.0
    )
    
    # H2: 接口兼容（直接兼容或已知转接方案）
    csp.add_hard_constraint(
        "interface_compatible",
        lambda combo: combo.lens.mount in combo.detector.compatible_mounts
        or combo.adapter is not None
    )
    
    # H3: 工作距离在镜头标称范围内
    csp.add_hard_constraint(
        "wd_in_range",
        lambda combo: (combo.lens.min_wd is None or combo.requirements.wd >= combo.lens.min_wd)
        and (combo.lens.max_wd is None or combo.requirements.wd <= combo.lens.max_wd)
    )
    
    # H4: 光谱波段重叠（红外/多光谱场景）
    csp.add_hard_constraint(
        "spectral_overlap",
        lambda combo: combo.spectral_overlap_ratio > 0.1
    )
    
    # ===== 软约束（影响评分）=====
    
    # S1: FOV吻合度（越接近目标FOV越好，但不要小于目标）
    csp.add_soft_constraint("fov_accuracy", 
        lambda c: 1.0 if c.actual_fov >= c.req_fov * 0.95 else 0.5,
        weight=3.0)
    
    # S2: 传感器覆盖裕量（像圆比传感器大10-20%为最佳）
    csp.add_soft_constraint("coverage_margin",
        lambda c: 1.0 - abs(c.coverage_margin - 0.15),
        weight=2.0)
    
    # S3: 接口直接兼容（不需要转接环加分）
    csp.add_soft_constraint("direct_mount",
        lambda c: 1.0 if c.adapter is None else 0.7,
        weight=1.0)
    
    # S4: 奈奎斯特匹配（理想过采样率 0.5-1.0）
    csp.add_soft_constraint("nyquist_match",
        lambda c: 1.0 if 0.5 <= c.nyquist_ratio <= 1.2 else 0.3,
        weight=2.5)
    
    # S5: 成本效益（预留接口）
    csp.add_soft_constraint("cost_efficiency",
        lambda c: c.cost_score if hasattr(c, 'cost_score') else 0.5,
        weight=1.5)
    
    return csp
```

### 4.3 多目标排序算法

```python
import numpy as np
from typing import List

def topsis_rank(candidates: List[Any], 
                criteria: List[str],
                weights: List[float],
                benefit_flags: List[bool]) -> List[Tuple[Any, float]]:
    """
    TOPSIS 多属性决策排序算法
    
    Args:
        candidates: 候选方案列表
        criteria: 评价指标名称列表
        weights: 指标权重列表
        benefit_flags: True=效益型（越大越好），False=成本型（越小越好）
    
    Returns:
        [(candidate, closeness_coefficient), ...] 按 closeness 降序排列
    """
    # 构建决策矩阵
    matrix = []
    for c in candidates:
        row = [getattr(c, crit, 0) for crit in criteria]
        matrix.append(row)
    
    X = np.array(matrix, dtype=float)
    
    # 1. 向量归一化
    norm = np.sqrt((X**2).sum(axis=0))
    X_norm = X / norm
    
    # 2. 加权
    W = np.array(weights)
    X_weighted = X_norm * W
    
    # 3. 确定正理想解和负理想解
    ideal_best = np.zeros(len(criteria))
    ideal_worst = np.zeros(len(criteria))
    
    for j, is_benefit in enumerate(benefit_flags):
        if is_benefit:
            ideal_best[j] = X_weighted[:, j].max()
            ideal_worst[j] = X_weighted[:, j].min()
        else:
            ideal_best[j] = X_weighted[:, j].min()
            ideal_worst[j] = X_weighted[:, j].max()
    
    # 4. 计算欧氏距离
    d_best = np.sqrt(((X_weighted - ideal_best)**2).sum(axis=1))
    d_worst = np.sqrt(((X_weighted - ideal_worst)**2).sum(axis=1))
    
    # 5. 计算相对贴近度
    closeness = d_worst / (d_best + d_worst)
    
    # 排序
    ranked = sorted(zip(candidates, closeness), key=lambda x: x[1], reverse=True)
    return ranked
```

### 4.4 Pareto 前沿筛选

```python
def pareto_front(candidates: List[Any], 
                 objectives: List[str],
                 maximize: List[bool]) -> List[Any]:
    """
    筛选 Pareto 最优解集（非支配解）
    
    适用于需要同时优化多个冲突目标的场景：
    - 成本 vs 性能
    - 分辨率 vs 景深
    - 视场 vs 放大倍率
    """
    pareto = []
    for c1 in candidates:
        dominated = False
        for c2 in candidates:
            if c1 is c2:
                continue
            # 检查 c2 是否支配 c1
            better_or_equal = True
            strictly_better = False
            for obj, is_max in zip(objectives, maximize):
                v1 = getattr(c1, obj)
                v2 = getattr(c2, obj)
                if is_max:
                    if v2 < v1:
                        better_or_equal = False
                        break
                    elif v2 > v1:
                        strictly_better = True
                else:
                    if v2 > v1:
                        better_or_equal = False
                        break
                    elif v2 < v1:
                        strictly_better = True
            
            if better_or_equal and strictly_better:
                dominated = True
                break
        
        if not dominated:
            pareto.append(c1)
    
    return pareto
```

---

## 5. 完整匹配流程伪代码（四级流水线）

```python
def full_matching_pipeline(requirements: dict, catalog: CatalogDB, 
                           domain: DomainModule, cache: Cache) -> MatchingResult:
    """
    四级流水线匹配流程 — 解决大规模候选集的性能问题
    """
    # Step 0: 参数标准化与补全
    reqs = normalize_requirements(requirements)
    optical_params = ThinLensCalculator().solve(reqs.to_optical_params())
    
    # =====================================================================
    # Stage 1: IndexPreFilter（索引预筛选）— O(1) 数据库索引操作
    # =====================================================================
    candidate_lenses = catalog.query_lenses(
        # 复合索引 (category, mount_type, focal_length_mm, image_circle_mm, min_wd, max_wd)
        category=reqs.lens_type,
        mount_type=reqs.preferred_mounts,
        focal_min=optical_params.focal_estimate_range[0],
        focal_max=optical_params.focal_estimate_range[1],
        image_circle_min=reqs.sensor_diag * 0.8,  # 允许略小的像圆（适配器/Reducer场景）
        wd_min=reqs.working_distance_mm * 0.5 if reqs.working_distance_mm else None,
        wd_max=reqs.working_distance_mm * 2.0 if reqs.working_distance_mm else None,
        limit=10000  # 安全上限，防止全表扫描
    )
    candidate_detectors = catalog.query_detectors(
        sensor_format=reqs.sensor_size,
        mount_type=reqs.preferred_mounts,
        limit=5000
    )
    stage1_count = len(candidate_lenses) * len(candidate_detectors)
    
    # =====================================================================
    # Stage 2: QuickHardFilter（快速硬约束剪枝）— O(1) 每项检查
    # =====================================================================
    quick_valid = []
    for lens in candidate_lenses:
        for det in candidate_detectors:
            # 2a: 像圆覆盖（传感器对角线 <= 像圆直径 × 1.05 裕量）
            if det.sensor_diag > lens.image_circle * 1.05:
                continue
            # 2b: 接口兼容（直接兼容或已知转接方案）
            if not is_mount_compatible(lens.mount, det.mount, adapter_catalog):
                continue
            # 2c: WD范围
            if reqs.working_distance_mm:
                if lens.min_wd and reqs.working_distance_mm < lens.min_wd:
                    continue
                if lens.max_wd and reqs.working_distance_mm > lens.max_wd:
                    continue
            quick_valid.append(LensDetectorCombo(lens, det, reqs))
    
    # 2d: 如果仍然太多，按关键维度分层采样
    if len(quick_valid) > 5000:
        quick_valid = smart_sampler(quick_valid, max_samples=5000)
    
    # =====================================================================
    # Stage 3: DomainHardFilter（领域硬约束）— 调用 DomainModule
    # =====================================================================
    domain_constraints = domain.get_hard_constraints()
    domain_valid = []
    for combo in quick_valid:
        # 检查该组合是否满足当前领域的所有硬约束
        if all(constraint.check(combo) for constraint in domain_constraints):
            domain_valid.append(combo)
    
    # =====================================================================
    # Stage 4: FullScoring（全量评分）— 缓存结果避免重复计算
    # =====================================================================
    scored = []
    for combo in domain_valid:
        cache_key = f"compat:{combo.lens.id}:{combo.detector.id}:{ALGORITHM_VERSION}"
        cached = cache.get(cache_key)
        
        if cached:
            combo.score_vector = cached
        else:
            # 4a: 领域派生参数计算
            combo.derived = domain.calculate_derived(combo)
            # 4b: 通用物理计算
            combo.coverage = sensor_coverage_check(det.sensor_w, det.sensor_h, lens.image_circle)
            combo.nyquist = nyquist_match(det.pixel_size_um, lens_mtf50_lpmm=lens.mtf50)
            # 4c: 领域评分维度
            combo.score_vector = domain_scoring_engine.score(combo, domain.get_scoring_dimensions())
            # 4d: 写入缓存（24小时过期）
            cache.set(cache_key, combo.score_vector, expire=86400)
        
        scored.append(combo)
    
    # =====================================================================
    # Stage 5: Ranking（结果排序）
    # =====================================================================
    ranked = topsis_rank(
        scored,
        criteria=domain.get_scoring_dimensions_names(),
        weights=reqs.scoring_weights or domain.default_weights(),
        benefit_flags=domain.get_benefit_flags()
    )
    
    pareto = pareto_front(
        scored,
        objectives=['score', 'cost'],
        maximize=[True, False]
    )
    
    return MatchingResult(
        top_matches=ranked[:20],
        pareto_front=pareto,
        stage_counts={
            'stage1_raw': stage1_count,
            'stage2_quick_filtered': len(quick_valid),
            'stage3_domain_filtered': len(domain_valid),
            'stage4_scored': len(scored)
        }
    )
```

---

## 6. 算法性能预估

| 场景 | 候选镜头数 | 候选探测器数 | 组合数 | 硬约束过滤后 | 响应时间预估 |
|------|:---------:|:----------:|:-----:|:----------:|:----------:|
| 小型库（测试） | 50 | 30 | 1,500 | ~300 | <10ms |
| 中型库（单领域） | 500 | 200 | 100,000 | ~5,000 | <100ms |
| 大型库（全领域） | 5,000 | 2,000 | 10,000,000 | ~50,000 | <500ms |
| 超大规模 | 50,000 | 10,000 | 500M | ~200,000 | <2s |

**优化策略**：
1. **索引预过滤**：在数据库查询阶段就用焦距范围、接口类型做B-Tree索引过滤
2. **分层剪枝**：先生成镜头候选，再用每个镜头的像面尺寸反推兼容传感器尺寸范围
3. **并行计算**：候选组合的物理计算可完全并行（多线程/多进程）
4. **缓存**：相同需求参数的查询结果缓存（LRU）
