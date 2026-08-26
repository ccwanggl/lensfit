# 软件架构与模块设计

> **文档定位（2026-08 修订，依据 ADR-003 / ADR-004）**：产品定位已转换为**学习辅助第一要务**——应用主壳为学习中心
> （学习路径 / 实验沙盘 / 教程三视图），镜头-传感器选型等工程能力收编为"实践场"。本文档以下章节描述的是
> **实践场（匹配流水线）与实践域内部实现**，按 ADR-003 §5 继续有效；执行计划见
> `docs/development/plans/active/2026-08-learning-first-repositioning-plan.md`。

## 0. 学习优先子系统地图（2026-08 新增）

| 子系统 | 位置 | 说明 |
|---|---|---|
| 内容管道 | `engine/optibench/content/` | 内容合同 v1 校验 + `modules/**/learning/*.md` 只读索引（无 DB 表）；正文阅读外移外部知识库（ADR-004），软件侧双链导航 |
| 课程图 | `engine/optibench/curriculum/` | `modules/curriculum.yaml` 声明式 DAG，环检测 / 悬空引用检测 |
| 实践接口 | `engine/optibench/practice/` | `PracticeActivity` 接口——学习层引用选型能力的**唯一通道**（import 方向受约束） |
| 实验运行时 | `engine/optibench/lab/` | T1/T3 数值仿真实验 + 面包板 preset workbench 运行时 |
| 学习者状态 | `learning_records` 表 | 本地 SQLite 单学习者（无账号系统），migration `004` |
| 新增 API | `routers/content.py` `curriculum.py` `learning.py` `lab.py` | 概念/测验索引、课程图合并进度、GET/PUT 学习进度、实验运行 |
| 前端主壳 | `apps/desktop/src/lab/LearningHub.tsx`(+`hub/`) | 默认首页；PathView / TutorialView / QuizPanel 挂载其内 |
| 四域工作台 | `pages/*Page.tsx` + `components/domain/DomainPageShell` | 实践场分组入口，三栏布局共享壳 |

架构边界（不可违反）：学习层只能经 `PracticeActivity` 引用选型能力；不做账号系统；面包板 checkpoint 门禁不变。

## 1. 设计哲学

- **模块化**：每个光学领域（工业视觉、显微镜、红外）是可插拔的模块
- **引擎+前端分离**：核心匹配引擎与UI解耦，支持多前端（Web、桌面、API）
- **数据库驱动**：所有光学公式、约束、器件参数均来自数据库，而非硬编码
- **可扩展性**：新厂商、新镜头类型、新探测器类型可通过配置文件/数据导入加入，无需改代码

> **文档一致性说明**：本架构图描绘的是目标状态。当前实现已具备核心流水线，但应用层模块尚未按图拆分，
> 部分数据层表/模块（如 adapter_catalog、formula_registry）尚未实现。详见下文标注。

---

## 2. 总体架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                          UI Layer (用户界面层)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐      │
│  │ Web App      │  │ Desktop App  │  │ REST API / SDK       │      │
│  │ (React/TS)   │  │ (Tauri v2)   │  │ (Python FastAPI)     │      │
│  └──────────────┘  └──────────────┘  └──────────────────────┘      │
└───────────────────────────────┬─────────────────────────────────────┘
                                │ HTTP / WebSocket / IPC
┌───────────────────────────────▼─────────────────────────────────────┐
│                    Application Layer (应用服务层)                     │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │
│  │ ProjectMgr │ │ ConfigMgr  │ │ TaskQueue  │ │ AuditLogger    │   │
│  │ 项目管理   │ │ 配置管理   │ │ 异步任务   │ │ 审计日志       │   │
│  │ （已落地） │ │ （未实现） │ │ （引擎内） │ │ （未实现）     │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │
│  │ ReportGen  │ │ ImportPipe │ │ ExportSvc  │ │ Cache Layer    │   │
│  │ 报告生成   │ │ 导入管道   │ │ 导出服务   │ │ 缓存层         │   │
│  │ （部分）   │ │ （已落地） │ │ （已落地） │ │ （未启用）     │   │
│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                      Core Engine (核心引擎层)                        │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │              MatchingEngine (通用匹配骨架)                    │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │  │
│  │  │IndexPre  │ │QuickHard │ │FullScore │ │ TOPSIS/Pareto  │ │  │
│  │  │Filter    │ │Filter    │ │Engine    │ │ Ranker         │ │  │
│  │  │索引预筛选 │ │快速硬约束│ │全量评分  │ │ 多目标排序     │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Domain Modules (领域模块，统一 DomainModule 接口)            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────┐ │  │
│  │  │ Industrial│ │ Microscope│ │ Infrared │ │ (可扩展)       │ │  │
│  │  │ Vision    │ │ Imaging   │ │ Imaging  │ │                │ │  │
│  │  │implements │ │implements │ │implements│ │ DomainModule   │ │  │
│  │  │DomainIF   │ │DomainIF   │ │DomainIF  │ │ Interface      │ │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Base Calculators (基础计算层)                                │  │
│  │  ThinLens / SensorStd / DOF / UnitConvert / SpectralCalc     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  VisualDataGen (可视化数据生成 — 纯JSON，不含渲染)             │  │
│  │  SensorCoverageData / FOV_SchematicData / SpectralPlotData   │  │
│  └──────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────┐
│                       Data Layer (数据层)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ MasterDB     │  │ UserProjectDB│  │ CompatibilityCache       │  │
│  │ (主数据库)   │  │ (项目+快照)  │  │ (按需计算缓存)           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ FormulaReg   │  │ PluginReg    │  │ ConfigStore              │  │
│  │ (分级公式库) │  │ (插件注册)   │  │ (用户配置)               │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. 核心模块详细设计

### 3.1 Matching Engine（匹配引擎）

采用**四级流水线 + 领域驱动约束**架构，解决大规模候选集的性能问题。

```
MatchingEngine (通用骨架，无领域知识)
├── InputParser（输入解析器）
│   ├── 已知参数识别
│   ├── 未知参数推断（调用 Base Calculators 互推缺失值）
│   └── 领域路由（根据 domain 字段分发到对应 DomainModule）
│
├── Stage 1: IndexPreFilter（索引预筛选）
│   └── **当前实现**：加载镜头/探测器全表后在 Python 中过滤。
│       `CatalogQuery.query_lenses/query_detectors` 已支持参数化数据库查询，
│       但尚未接入 Stage 1。
│   └── **目标**：在数据库查询阶段用复合索引过滤：
│       category, mount_type, focal_range, image_circle_min, wd_range
│   └── **目标输出**：候选集从 10M → <100K（O(1) 数据库索引操作）
│
├── Stage 2: QuickHardFilter（快速硬约束剪枝）
│   └── 仅执行 O(1) 检查，无复杂物理计算：
│       ├── 像圆覆盖：lens.image_circle >= detector.sensor_diag
│       ├── 接口兼容：mount 直接匹配或已知转接方案存在
│       └── WD 范围：wd 在 lens.min_wd ~ lens.max_wd 内
│   └── 输出：候选集从 100K → <10K
│
├── Stage 3: DomainHardFilter（领域硬约束）
│   └── 调用当前 DomainModule.get_hard_constraints()：
│       ├── Industrial: 畸变上限、远心度（测量场景）
│       ├── Microscope: NA-相机匹配、镜筒长度、无渐晕
│       └── Infrared: 波段重叠、冷屏F数匹配
│   └── 输出：候选集从 10K → <5K
│
├── Stage 4: FullScoring（全量评分）
│   └── 调用当前 DomainModule.get_scoring_dimensions()：
│       ├── 几何匹配度（FOV吻合度）
│       ├── 光学性能分（MTF裕量、奈奎斯特比）
│       ├── 探测器适配分（QE匹配、噪声预算）
│       ├── 机械适配分（接口直接兼容/需转接）
│       └── 经济适配分（成本估算）
│   └── 输出：每个候选的完整评分向量
│
└── Stage 5: ResultRanker（结果排序）
    ├── 按综合加权评分排序
    ├── 按单一维度排序（成本优先/性能优先）
    └── Pareto前沿筛选（多目标非支配解集，展示权衡关系）
```

**关键技术决策**：
- 索引预筛选依赖数据库复合索引（见 [数据库设计](database-design.md)）
- 领域硬约束和评分维度由 `DomainModule` 接口提供，MatchingEngine 零领域知识
- 多目标排序使用加权 TOPSIS（默认）+ NSGA-II（Pareto 模式可选）
- 缓存层：`compatibility_cache` 表已创建，但**尚未接入匹配流程**（当前无读写）。
  目标设计是按 lens_id + detector_id + algorithm_version 缓存 Stage 4 结果。

---

### 3.2 Domain Modules（领域模块）

所有领域模块实现统一的 `DomainModule` 接口，MatchingEngine 通过注册表动态加载，**新增领域无需改动引擎代码**。

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DomainModule(ABC):
    """领域模块统一接口 — 新增领域只需实现此接口并注册"""
    
    @property
    @abstractmethod
    def domain_id(self) -> str:
        """唯一标识：industrial / microscope / infrared / photography"""
        pass
    
    @property
    @abstractmethod
    def domain_name(self) -> str:
        """显示名称"""
        pass
    
    @abstractmethod
    def get_parameters(self) -> List[ParameterDef]:
        """该领域支持的参数定义（用于UI动态渲染输入表单）"""
        pass
    
    @abstractmethod
    def get_hard_constraints(self) -> List[Constraint]:
        """硬约束检查器列表（Stage 3 调用）"""
        pass
    
    @abstractmethod
    def get_scoring_dimensions(self) -> List[ScoringDimension]:
        """评分维度定义（Stage 4 调用）"""
        pass
    
    @abstractmethod
    def calculate_derived(self, combo: DeviceCombo) -> Dict[str, Any]:
        """计算领域相关的派生参数"""
        pass
    
    def default_weights(self) -> Dict[str, float]:
        """默认评分权重，子类可覆盖"""
        pass
    
    def get_benefit_flags(self) -> Dict[str, bool]:
        """获取各评分维度的收益标志"""
        pass
    
    # 注意：当前代码中没有 get_visual_data_generators；可视化由 engine/optibench/visualization/ 统一处理。
```

#### 注册与使用

```python
class MatchingEngine:
    def __init__(self):
        self.domains: Dict[str, DomainModule] = {}
    
    def register_domain(self, module: DomainModule):
        self.domains[module.domain_id] = module
    
    def match(self, requirements: Requirements) -> List[MatchResult]:
        domain = self.domains.get(requirements.domain)
        if not domain:
            raise ValueError(f"Unknown domain: {requirements.domain}")
        
        # Stage 1-2: 通用索引预筛选 + 快速硬约束
        candidates = self.index_pre_filter(requirements)
        candidates = self.quick_hard_filter(candidates, requirements)
        
        # Stage 3: 领域硬约束
        hard_constraints = domain.get_hard_constraints()
        candidates = self.apply_constraints(candidates, hard_constraints)
        
        # Stage 4: 领域评分
        scoring_dims = domain.get_scoring_dimensions()
        scored = self.scoring_engine.score(candidates, scoring_dims)
        
        # Stage 5: 通用排序
        return self.ranker.rank(scored)
```

#### 各领域模块实现

#### 3.2.1 IndustrialVisionModule（工业视觉模块）

```
IndustrialVisionModule
├── LensTypes
│   ├── FALens（FA定焦镜头）
│   ├── TelecentricLens（远心镜头）
│   ├── LinescanLens（线扫镜头）
│   └── ZoomLens（变焦镜头）
├── Calculators
│   ├── FOV_WD_Focal（视野-工作距离-焦距三角互算）
│   ├── DOFCalculator（景深计算，含弥散圆直径与像素关系）
│   ├── ExtensionRingCalculator（延长环/接圈计算）
│   ├── ResolutionBudget（分辨率预算：像素精度 vs 光学分辨率）
│   └── LinescanTiming（线扫行频与运动速度匹配）
└── Constraints
    ├── SensorCoverage（传感器覆盖≥像面尺寸）
    ├── WDRange（工作距离在镜头标称范围内）
    ├── DistortionLimit（畸变上限约束）
    └── Telecentricity（远心度约束，测量应用）
```

#### 3.2.2 MicroscopeModule（显微镜模块）

```
MicroscopeModule
├── Components
│   ├── Objective（物镜：NA、WD、放大倍率、视场数FN）
│   ├── Eyepiece（目镜：视场数、倍率）
│   ├── CMountAdapter（C-Mount适配器：reducer倍率）
│   ├── Camera（相机：传感器尺寸、像素）
│   └── IntermediateOptics（中间光学：tube lens焦距）
├── Calculators
│   ├── TotalMagnification（总放大倍率 = 物镜 × 目镜 × 适配器 × 数码变焦）
│   ├── FOV_at_Sensor（传感器上实际视野）
│   ├── FOV_at_Eyepiece（目镜视场 vs 相机视场对比）
│   ├── NA_Resolution（阿贝分辨率 = 0.61λ/NA）
│   ├── Nyquist_Pixel（奈奎斯特像素尺寸 ≤ 0.61λ/(2×NA)）
│   ├── VignettingPredictor（渐晕预测：传感器对角线 vs 像圆直径）
│   └── ParfocalityCheck（齐焦性检查）
└── Constraints
    ├── Adapter_Sensor_Match（适配器倍率与传感器尺寸匹配）
    ├── NA_Camera_Match（物镜NA与相机分辨率匹配）
    ├── TubeLengthMatch（镜筒长度匹配：160mm/∞等）
    └── VignettingFree（无渐晕约束）
```

**关键创新点**：
- 自动计算并可视化"显微镜圆形像场"与"矩形传感器"的关系
- 渐晕预测：当传感器对角线 > 像圆直径时，精确计算四个角的暗区比例

#### 3.2.3 InfraredModule（红外成像模块）

```
InfraredModule
├── Components
│   ├── IRLens（红外镜头：焦距、F数、波段、镀膜）
│   ├── IRDetector（红外探测器：像元尺寸、像元数、波段响应、NETD）
│   └── Optics（光学窗口、滤光片）
├── Calculators
│   ├── IFOV_Calculator（瞬时视场角 = 像元尺寸 / 焦距）
│   ├── MRTD_Estimator（最小可分辨温差估算）
│   ├── FOV_Thermal（热成像视场计算）
│   ├── SpotSize（测量光斑尺寸 = 距离 × IFOV）
│   └── EnergyConcentration（能量集中度/弥散斑分析）
└── Constraints
    ├── BandOverlap（镜头透过波段与探测器响应波段重叠度）
    ├── FNumber_Match（F数与探测器最佳匹配）
    ├── ColdShield_FNumber（冷屏F数匹配，制冷型探测器）
    └── SpatialResolution（空间分辨率 vs 目标尺寸匹配）
```

---

### 3.3 Visualizer（可视化引擎）— 数据生成与渲染分离

**原则**：引擎层只输出"可视化数据"（纯JSON），前端负责"渲染呈现"。避免前后端往返和平台差异。

```
VisualDataGen (引擎层 — Core Engine)
├── SensorCoverageData
│   └── 输出: {sensor_rect, image_circle, vignetting_regions, coverage_ratio}
├── FOVSchematicData
│   └── 输出: {camera_pos, lens_pos, fov_cone, target_rect, wd_line}
├── MTFNyquistData
│   └── 输出: {mtf_curve_points, nyquist_frequency, cutoff_frequency}
├── SpectralOverlapData
│   └── 输出: {lens_band, detector_qe_curve, overlap_band, overlap_ratio}
└── ComparisonRadarData
    └── 输出: {dimensions: ["成本","分辨率","FOV"], schemes: [{name, values}]}

Frontend Renderers (前端层 — UI Layer)
├── SensorCoverageCanvas
│   └── 用 Fabric.js / HTML5 Canvas 绘制矩形、圆、多边形裁剪
├── FOVSchematicSVG
│   └── 用 SVG 绘制光路示意图
├── MTFNyquistChart
│   └── 用 Recharts / D3 绘制曲线图
├── SpectralOverlapChart
│   └── 用 Recharts 绘制波段重叠面积图
└── ComparisonRadarChart
    └── 用 Recharts Radar 绘制多方案雷达对比

ReportRenderer (后端 — Application Layer)
├── ChartRasterizer
│   └── 用 matplotlib / svglib 将 VisualDataGen 的输出渲染为 SVG/PNG
│   └── 嵌入 PDF 报告，保证跨平台一致性
└── PDFAssembler
    └── 用 reportlab 组装参数表 + 图表 + 结论
```

**前后端协作示例**：

```python
# 引擎 API：只生成数据
@app.post("/api/v1/visualize/coverage")
def generate_coverage_data(req: CoverageRequest) -> CoverageData:
    return visual_data_gen.sensor_coverage(req.lens_id, req.detector_id)

# 前端：用 Canvas 渲染
function renderCoveragePlot(canvas, data) {
    canvas.drawRect(data.sensor_rect, { fill: 'blue', stroke: 'navy' });
    canvas.drawCircle(data.image_circle, { stroke: 'green', strokeWidth: 2 });
    data.vignetting_regions.forEach(poly => {
        canvas.drawPolygon(poly.points, { fill: 'red', opacity: 0.3 });
    });
    // 交互：鼠标悬停显示坐标和覆盖百分比
}
```

---

### 3.4 Database Layer（数据层）

当前采用**单文件 SQLite** 架构，主库数据和用户项目数据共存于同一数据库：

```
DataLayer (当前实现)
├── lens_catalog（镜头目录）
├── detector_catalog（探测器目录）
├── manufacturers（厂商表）
├── compatibility_cache（兼容性缓存表 — 已创建但未启用）
├── user_projects（项目列表）
└── project_setups（项目方案，支持引用 + 快照双模式）

DataLayer (目标规划中)
├── adapter_catalog（适配器目录）          # 未实现
├── spectral_responses（光谱响应曲线）      # 未实现
├── formula_registry（公式注册表）          # 未实现
├── lens_catalog_history（参数历史版本）    # 未实现
└── SyncManager（主库/用户数据同步）        # 未实现
```

---

## 4. 接口设计（API Layer）

### 4.1 异步任务模型

匹配计算在大规模库查询时可能耗时数秒，必须采用异步模型防止UI冻结。

```python
from enum import Enum
from datetime import datetime
from typing import Optional, List

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class MatchingTask:
    task_id: str
    status: TaskStatus
    progress: float          # 0.0 ~ 1.0
    total_candidates: int
    filtered_candidates: int
    result: Optional[List[MatchResult]]
    error: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
```

### 4.2 REST API 端点

```python
# 启动异步匹配，立即返回任务ID
@app.post("/api/v1/match/async")
def start_matching(req: MatchRequest) -> MatchingTask:
    return task_queue.submit(req)

# 轮询任务状态（前端进度条）
@app.get("/api/v1/match/async/{task_id}")
def get_matching_status(task_id: str) -> MatchingTask:
    return task_queue.get_status(task_id)

# 获取已完成任务的结果
@app.get("/api/v1/match/async/{task_id}/result")
def get_matching_result(task_id: str) -> MatchResult:
    return task_queue.get_result(task_id)

# 取消正在执行的任务
@app.delete("/api/v1/match/async/{task_id}")
def cancel_matching(task_id: str) -> bool:
    return task_queue.cancel(task_id)

# 可视化数据生成（同步，<100ms）
@app.post("/api/v1/visualize/coverage")
def generate_coverage_data(req: CoverageRequest) -> CoverageData:
    return visual_data_gen.sensor_coverage(req.lens_id, req.detector_id)

# 报告导出（当前为同步接口；异步 PDF 导出尚未实现）
# @app.post("/api/v1/export/pdf/async") ...
# @app.get("/api/v1/export/pdf/async/{task_id}") ...
# 现有接口：
#   POST /api/v1/export              同步导出 CSV/Excel/PDF
#   POST /api/v1/projects/{id}/report 项目报告导出
```

**路由组织**：`optibench/api/server.py` 仅负责应用组装与生命周期，各业务域已拆分为 `optibench/api/routers/` 下的独立 FastAPI 路由模块：

| 路由模块 | 前缀 | 说明 |
|---|---|---|
| `catalog.py` | `/api/v1/catalog` | 镜头/探测器/厂商目录 + 批量导入 |
| `domains.py` | `/api/v1/domains` | 领域发现与参数定义 |
| `matching.py` | `/api/v1` | 光学计算、异步匹配、SSE 流式匹配 |
| `knowledge.py` | `/api/v1/knowledge` | 公式、约束、推理、预设 |
| `visualization.py` | `/api/v1/visualize` | 覆盖、MTF、景深/CoC 数据 |
| `projects.py` | `/api/v1` | 项目/方案 CRUD、项目报告 |
| `export.py` | `/api/v1` | 结果导出 CSV/Excel/PDF |

### 4.3 同步调用示例（SDK层包装）

```python
from optibench import MatchingEngine, Project

proj = Project.create(name="PCB检测项目", domain="industrial")

# SDK内部走异步API，但包装为同步接口（自动轮询）
engine = MatchingEngine()
results = engine.match(requirements, top_k=10, timeout=30)

# 或者显式异步（大库查询场景）
task = engine.match_async(requirements)
while not task.done:
    print(f"进度: {task.progress:.0%} ({task.filtered_candidates}/{task.total_candidates})")
    time.sleep(0.5)
results = task.result
```

---

## 5. 部署架构

### 5.1 单机版（MVP首选）

Tauri 桌面壳 + Python FastAPI 本地服务（sidecar 模式）。关键设计：**Sidecar Supervisor** 管理 Python 进程生命周期。

```
[Desktop App (Tauri)]
    │
    ├── Frontend (React SPA)
    ├── Sidecar Supervisor (Rust)
    │   ├── 启动 Python 引擎（随机端口，避免冲突）
    │   ├── 健康检查轮询（启动时最多等待10秒）
    │   ├── 崩溃自动重启（最多3次）
    │   └── Tauri关闭时强制终止Python进程
    │
    ├── Python Engine (FastAPI)
    │   ├── Core Engine
    │   └── SQLite 本地数据库
    │
    └── 静态资源 (HTML/CSS/JS)
```

**Sidecar Supervisor 关键逻辑**：

```rust
struct EngineSupervisor {
    process: Arc<Mutex<Option<Child>>>,
    port: u16,  // 随机选择可用端口
}

impl EngineSupervisor {
    fn start() -> Result<Self, String> {
        let port = pick_unused_port()?;
        let child = Command::new_sidecar("optibench-engine")
            .args(&["--port", &port.to_string()])
            .spawn()?;
        wait_for_healthy(format!("http://127.0.0.1:{}/health", port), timeout=10)?;
        Ok(Self { process: Arc::new(Mutex::new(Some(child))), port })
    }
    fn shutdown(&self) {
        if let Ok(mut guard) = self.process.lock() {
            if let Some(mut child) = guard.take() {
                let _ = child.kill();  // 防止僵尸进程
            }
        }
    }
}
```

**当前状态**：Sidecar Supervisor 已实现启动、健康检查、API key 捕获和关闭 kill，但没有崩溃自动重启。
**风险备案**：如果 sidecar 在 Windows/macOS 上不稳定，MVP 降级方案为**前端通过 child_process 直接调用 Python CLI**（无持久HTTP服务）。

### 5.2 客户端-服务器版（企业版）

```
[Web Browser] ←──HTTP/WebSocket──→ [Backend API (Python/FastAPI)]
                                         │
                                         ├── Core Engine
                                         ├── PostgreSQL 主数据库
                                         ├── Redis 缓存 + 任务队列
                                         └── MinIO 对象存储(报告/PDF)
```

### 5.3 混合架构（推荐长期路线）

```
[Desktop App] ←──同步──→ [Cloud Service]
    │                        │
    ├── 本地引擎+DB          ├── 共享数据库
    ├── 隐私项目             ├── 团队协作
    └── 离线可用             └── 集中数据更新
```
