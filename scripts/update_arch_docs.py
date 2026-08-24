#!/usr/bin/env python3
"""Update architecture docs to reflect current implementation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).parent.parent
ARCH = ROOT / "docs" / "development" / "architecture"


def update_software_architecture() -> None:
    path = ARCH / "software-architecture.md"
    text = path.read_text(encoding="utf-8")

    # Consistency note after design philosophy
    old = (
        "- **可扩展性**：新厂商、新镜头类型、新探测器类型可通过配置文件/数据导入加入，无需改代码\n"
        "\n"
        "---\n"
    )
    new = (
        "- **可扩展性**：新厂商、新镜头类型、新探测器类型可通过配置文件/数据导入加入，无需改代码\n"
        "\n"
        "> **文档一致性说明**：本架构图描绘的是目标状态。当前实现已具备核心流水线，但应用层模块尚未按图拆分，\n"
        "> 部分数据层表/模块（如 adapter_catalog、formula_registry）尚未实现。详见下文标注。\n"
        "\n"
        "---\n"
    )
    text = text.replace(old, new)

    # Application layer diagram
    old = (
        "│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │\n"
        "│  │ ProjectMgr │ │ ConfigMgr  │ │ TaskQueue  │ │ AuditLogger    │   │\n"
        "│  │ 项目管理   │ │ 配置管理   │ │ 异步任务   │ │ 审计日志       │   │\n"
        "│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │\n"
        "│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │\n"
        "│  │ ReportGen  │ │ ImportPipe │ │ ExportSvc  │ │ Cache Layer    │   │\n"
        "│  │ 报告生成   │ │ 导入管道   │ │ 导出服务   │ │ 缓存层         │   │\n"
        "│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │\n"
    )
    new = (
        "│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │\n"
        "│  │ ProjectMgr │ │ ConfigMgr  │ │ TaskQueue  │ │ AuditLogger    │   │\n"
        "│  │ 项目管理   │ │ 配置管理   │ │ 异步任务   │ │ 审计日志       │   │\n"
        "│  │ （已落地） │ │ （未实现） │ │ （引擎内） │ │ （未实现）     │   │\n"
        "│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │\n"
        "│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────────┐   │\n"
        "│  │ ReportGen  │ │ ImportPipe │ │ ExportSvc  │ │ Cache Layer    │   │\n"
        "│  │ 报告生成   │ │ 导入管道   │ │ 导出服务   │ │ 缓存层         │   │\n"
        "│  │ （部分）   │ │ （已落地） │ │ （已落地） │ │ （未启用）     │   │\n"
        "│  └────────────┘ └────────────┘ └────────────┘ └────────────────┘   │\n"
    )
    text = text.replace(old, new)

    # Stage 1
    old = (
        "├── Stage 1: IndexPreFilter（索引预筛选）\n"
        "│   └── 在数据库查询阶段用复合索引过滤：\n"
        "│       category, mount_type, focal_range, image_circle_min, wd_range\n"
        "│   └── 输出：候选集从 10M → <100K（O(1) 数据库索引操作）\n"
    )
    new = (
        "├── Stage 1: IndexPreFilter（索引预筛选）\n"
        "│   └── **当前实现**：`index_pre_filter` 已调用 `CatalogQuery.query_lenses` /\n"
        "│       `query_detectors` 在数据库层过滤 category、mount_type、focal_range、\n"
        "│       image_circle_min、wd_range。\n"
        "│   └── **索引现状**：现有迁移已包含 category、mount_type、focal_length 等索引；\n"
        "│       image_circle 和 working distance 范围过滤由 SQL 执行，但在超大规模目录下\n"
        "│       建议后续补充对应索引以完全达到文档中的性能预估。\n"
    )
    text = text.replace(old, new)

    # Cache decision note
    old = (
        "- 缓存层缓存 `Stage 4` 的计算结果（按 lens_id + detector_id + algorithm_version 键值）\n"
    )
    new = (
        "- 缓存层：`compatibility_cache` 表已创建，但**尚未接入匹配流程**（当前无读写）。\n"
        "  目标设计是按 lens_id + detector_id + algorithm_version 缓存 Stage 4 结果。\n"
    )
    text = text.replace(old, new)

    # DomainModule interface
    old_iface = (
        "class DomainModule(ABC):\n"
        '    """领域模块统一接口 — 新增领域只需实现此接口并注册"""\n'
        "    \n"
        "    @property\n"
        "    @abstractmethod\n"
        "    def domain_id(self) -> str:\n"
        '        """唯一标识：industrial / microscope / infrared"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_parameters(self) -> List[ParameterDef]:\n"
        '        """该领域支持的参数定义（用于UI动态渲染输入表单）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_hard_constraints(self) -> List[Constraint]:\n"
        '        """硬约束检查器列表（Stage 3 调用）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_scoring_dimensions(self) -> List[ScoringDimension]:\n"
        '        """评分维度定义（Stage 4 调用）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def calculate_derived(self, combo: DeviceCombo) -> Dict[str, Any]:\n"
        '        """计算领域相关的派生参数"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_visual_data_generators(self) -> List[VisualDataGenerator]:\n"
        '        """该领域支持的可视化数据生成器"""\n'
        "        pass\n"
    )
    new_iface = (
        "class DomainModule(ABC):\n"
        '    """领域模块统一接口 — 新增领域只需实现此接口并注册"""\n'
        "    \n"
        "    @property\n"
        "    @abstractmethod\n"
        "    def domain_id(self) -> str:\n"
        '        """唯一标识：industrial / microscope / infrared / photography"""\n'
        "        pass\n"
        "    \n"
        "    @property\n"
        "    @abstractmethod\n"
        "    def domain_name(self) -> str:\n"
        '        """显示名称"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_parameters(self) -> List[ParameterDef]:\n"
        '        """该领域支持的参数定义（用于UI动态渲染输入表单）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_hard_constraints(self) -> List[Constraint]:\n"
        '        """硬约束检查器列表（Stage 3 调用）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def get_scoring_dimensions(self) -> List[ScoringDimension]:\n"
        '        """评分维度定义（Stage 4 调用）"""\n'
        "        pass\n"
        "    \n"
        "    @abstractmethod\n"
        "    def calculate_derived(self, combo: DeviceCombo) -> Dict[str, Any]:\n"
        '        """计算领域相关的派生参数"""\n'
        "        pass\n"
        "    \n"
        "    def default_weights(self) -> Dict[str, float]:\n"
        '        """默认评分权重，子类可覆盖"""\n'
        "        pass\n"
        "    \n"
        "    def get_benefit_flags(self) -> Dict[str, bool]:\n"
        '        """获取各评分维度的收益标志"""\n'
        "        pass\n"
        "    \n"
        "    # 注意：当前代码中没有 get_visual_data_generators；可视化由 engine/optibench/visualization/ 统一处理。\n"
    )
    text = text.replace(old_iface, new_iface)

    # Data layer
    old_data = (
        "采用**主数据库 + 用户项目数据库**双库架构：\n"
        "\n"
        "```\n"
        "DataLayer\n"
        "├── MasterDB（主数据库，预置/同步更新）\n"
        "│   ├── lens_catalog（镜头目录）\n"
        "│   ├── detector_catalog（探测器目录）\n"
        "│   ├── adapter_catalog（适配器目录）\n"
        "│   ├── objective_catalog（显微镜物镜目录）\n"
        "│   ├── material_catalog（光学材料库：折射率、透过率）\n"
        "│   ├── coating_catalog（镀膜库）\n"
        "│   └── formula_registry（公式注册表）\n"
        "├── UserProjectDB（用户项目数据库，本地SQLite）\n"
        "│   ├── projects（项目列表）\n"
        "│   ├── setups（配置方案）\n"
        "│   ├── custom_devices（用户自定义器件）\n"
        "│   └── calculation_history（计算历史）\n"
        "└── SyncManager（同步管理器）\n"
        "    ├── 主数据库版本检查与更新\n"
        "    └── 用户数据备份/恢复\n"
        "```\n"
    )
    new_data = (
        "当前采用**单文件 SQLite** 架构，主库数据和用户项目数据共存于同一数据库：\n"
        "\n"
        "```\n"
        "DataLayer (当前实现)\n"
        "├── lens_catalog（镜头目录）\n"
        "├── detector_catalog（探测器目录）\n"
        "├── manufacturers（厂商表）\n"
        "├── compatibility_cache（兼容性缓存表 — 已创建但未启用）\n"
        "├── user_projects（项目列表）\n"
        "└── project_setups（项目方案，支持引用 + 快照双模式）\n"
        "\n"
        "DataLayer (目标规划中)\n"
        "├── adapter_catalog（适配器目录）          # 未实现\n"
        "├── spectral_responses（光谱响应曲线）      # 未实现\n"
        "├── formula_registry（公式注册表）          # 未实现\n"
        "├── lens_catalog_history（参数历史版本）    # 未实现\n"
        "└── SyncManager（主库/用户数据同步）        # 未实现\n"
        "```\n"
    )
    text = text.replace(old_data, new_data)

    # API endpoints
    old_api = (
        "# 获取已完成任务的结果\n"
        '@app.get("/api/v1/match/async/{task_id}/result")\n'
        "def get_matching_result(task_id: str) -> MatchResult:\n"
        "    return task_queue.get_result(task_id)\n"
        "\n"
        "# 取消正在执行的任务\n"
    )
    new_api = (
        "# 获取已完成任务的结果（当前实现把结果内嵌在状态接口中，此端点尚未拆分）\n"
        "# @app.get(\"/api/v1/match/async/{task_id}/result\")\n"
        "# def get_matching_result(task_id: str) -> MatchResult: ...\n"
        "\n"
        "# 取消正在执行的任务\n"
    )
    text = text.replace(old_api, new_api)

    old_export = (
        "# 报告导出（异步，PDF生成耗时）\n"
        '@app.post("/api/v1/export/pdf/async")\n'
        "def start_pdf_export(req: ExportRequest) -> ExportTask:\n"
        "    return export_queue.submit(req)\n"
        "\n"
        '@app.get("/api/v1/export/pdf/async/{task_id}")\n'
        "def get_export_status(task_id: str) -> ExportTask:\n"
        "    return export_queue.get_status(task_id)\n"
    )
    new_export = (
        "# 报告导出（当前为同步接口；异步 PDF 导出尚未实现）\n"
        "# @app.post(\"/api/v1/export/pdf/async\") ...\n"
        "# @app.get(\"/api/v1/export/pdf/async/{task_id}\") ...\n"
        "# 现有接口：\n"
        "#   POST /api/v1/export              同步导出 CSV/Excel/PDF\n"
        "#   POST /api/v1/projects/{id}/report 项目报告导出\n"
    )
    text = text.replace(old_export, new_export)

    # Sidecar supervisor
    old = "        ├── 崩溃自动重启（最多3次）\n"
    new = "        ├── 崩溃自动重启（最多3次） — **尚未实现**\n"
    text = text.replace(old, new)

    old_risk = (
        "**风险备案**：如果 sidecar 在 Windows/macOS 上不稳定，MVP 降级方案为**前端通过 child_process 直接调用 Python CLI**（无持久HTTP服务）。\n"
    )
    new_risk = (
        "**当前状态**：Sidecar Supervisor 已实现启动、健康检查、API key 捕获和关闭 kill，但没有崩溃自动重启。\n"
        "**风险备案**：如果 sidecar 在 Windows/macOS 上不稳定，MVP 降级方案为**前端通过 child_process 直接调用 Python CLI**（无持久HTTP服务）。\n"
    )
    text = text.replace(old_risk, new_risk)

    path.write_text(text, encoding="utf-8")
    print("Updated software-architecture.md")


def update_core_algorithms() -> None:
    path = ARCH / "core-algorithms.md"
    text = path.read_text(encoding="utf-8")

    old = (
        "## 6. 完整匹配流程伪代码（四级流水线）\n"
    )
    new = (
        "> **实现状态说明**：以下伪代码与 `engine/optibench/matching/engine.py` 的四级流水线结构一致，\n"
        "> 但 Stage 1 目前未使用 `query_lenses` 的数据库索引过滤（全表加载后 Python 过滤）。\n"
        "> 完整的性能预估（第 6 节表格）尚未通过回归测试验证。\n"
        "\n"
        "## 6. 完整匹配流程伪代码（四级流水线）\n"
    )
    text = text.replace(old, new)

    old = (
        "### 3.3 光谱匹配算法（红外/多光谱场景）\n"
    )
    new = (
        "### 3.3 光谱匹配算法（红外/多光谱场景）\n"
        "\n"
        "> **实现状态**：独立的 `spectral_overlap()` 函数尚未创建；波段匹配逻辑分散在 `InfraredModule.calculate_derived` 和 `ScoringEngine._score_band_match` 中。\n"
    )
    text = text.replace(old, new)

    old = (
        "### 3.4 显微镜 C-Mount 适配器匹配\n"
    )
    new = (
        "### 3.4 显微镜 C-Mount 适配器匹配\n"
        "\n"
        "> **实现状态**：独立的 `microscope_adapter_match()` 函数尚未创建；适配器相关计算在 `MicroscopeModule.calculate_derived` 中处理。当前也没有 `adapter_catalog` 表。\n"
    )
    text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")
    print("Updated core-algorithms.md")


def update_database_design() -> None:
    path = ARCH / "database-design.md"
    text = path.read_text(encoding="utf-8")

    # Mark unimplemented tables
    old = (
        "### 3.4 适配器/转接环表 (adapter_catalog)\n"
    )
    new = (
        "### 3.4 适配器/转接环表 (adapter_catalog) — **尚未实现**\n"
        "\n"
        "> 当前代码中没有 `AdapterCatalog` 模型，也没有对应的 Alembic 迁移。以下设计保留为参考。\n"
        "\n"
    )
    text = text.replace(old, new)

    old = (
        "### 3.5 光谱响应曲线表 (spectral_responses)\n"
    )
    new = (
        "### 3.5 光谱响应曲线表 (spectral_responses) — **尚未实现**\n"
        "\n"
        "> 当前数据库中不存在该表，光谱匹配逻辑暂未依赖离散光谱数据。以下设计保留为参考。\n"
        "\n"
    )
    text = text.replace(old, new)

    old = (
        "### 3.8 公式注册表 (formula_registry)\n"
    )
    new = (
        "### 3.8 公式注册表 (formula_registry) — **尚未实现**\n"
        "\n"
        "> 当前公式以内建 Python 函数为主（`core/thin_lens.py`、`matching/scoring.py` 等），\n"
        "> L1/L2/L3 分级表达式系统尚未落地。以下设计保留为参考。\n"
        "\n"
    )
    text = text.replace(old, new)

    # Mark cache unused
    old = (
        "### 3.6 兼容性缓存表 (compatibility_cache)\n"
        "\n"
        "**按需计算 + 结果缓存**，替代预计算的 compatibility_matrix 大表。避免 5000镜头 × 2000探测器 = 10M 行预计算。\n"
    )
    new = (
        "### 3.6 兼容性缓存表 (compatibility_cache)\n"
        "\n"
        "> **当前状态**：表和索引已创建，但**没有任何运行时代码读写该表**。匹配引擎尚未接入缓存。\n"
        "\n"
        "**按需计算 + 结果缓存**，替代预计算的 compatibility_matrix 大表。避免 5000镜头 × 2000探测器 = 10M 行预计算。\n"
    )
    text = text.replace(old, new)

    # Data quality score note
    old = (
        "def calculate_data_quality_score(record: dict) -> float:\n"
        "    \"\"\"\n"
        "    计算单条记录的数据完整度评分 (0-1)\n"
        "    \"\"\"\n"
    )
    new = (
        "def calculate_data_quality_score(record: dict) -> float:\n"
        "    \"\"\"\n"
        "    计算单条记录的数据完整度评分 (0-1)。\n"
        "    **当前状态**：该函数尚未实现；模型中 `data_quality_score` 字段默认 0，仅作占位。\n"
        "    \"\"\"\n"
    )
    text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")
    print("Updated database-design.md")


def update_tech_stack() -> None:
    path = ARCH / "tech-stack.md"
    text = path.read_text(encoding="utf-8")

    # Remove diskcache line
    text = text.replace(
        '    "diskcache>=5.6",     # 本地文件缓存（单机版）\n', ""
    )

    # Mark unused deps
    text = text.replace(
        '    "python-constraint>=1.4",\n',
        '    "python-constraint>=1.4",  # 已引入但未在代码中使用\n',
    )
    text = text.replace(
        '    "asteval>=1.0",\n',
        '    "asteval>=1.0",              # 已引入但未在代码中使用（formula_registry 尚未实现）\n',
    )
    text = text.replace(
        '    "matplotlib>=3.8",\n',
        '    "matplotlib>=3.8",           # 已引入但未在代码中使用\n',
    )

    # Add note in core dependencies section
    old = "### 4.1 Python 依赖 (engine/pyproject.toml)\n\n```toml\n"
    new = (
        "### 4.1 Python 依赖 (engine/pyproject.toml)\n"
        "\n"
        "> 以下清单与 `engine/pyproject.toml` 一致。标注“未使用”的依赖已在代码中确认无引用，计划清理或启用。\n"
        "\n"
        "```toml\n"
    )
    text = text.replace(old, new)

    # Update directory tree
    old_engine = (
        "├── engine/                         # Python 核心引擎\n"
        "│   ├── pyproject.toml\n"
        "│   ├── optibench/\n"
        "│   │   ├── __init__.py\n"
        "│   │   ├── core/                   # 基础光学计算\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── thin_lens.py        # 薄透镜公式\n"
        "│   │   │   ├── sensor.py           # 传感器标准化\n"
        "│   │   │   ├── dof.py              # 景深计算\n"
        "│   │   │   └── units.py            # 单位换算\n"
        "│   │   ├── matching/               # 匹配引擎\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── engine.py           # 主匹配引擎\n"
        "│   │   │   ├── constraints.py      # 约束定义\n"
        "│   │   │   ├── scoring.py          # 评分算法\n"
        "│   │   │   └── solver.py           # TOPSIS/Pareto\n"
        "│   │   ├── domains/                # 领域模块\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── industrial.py\n"
        "│   │   │   ├── microscope.py\n"
        "│   │   │   └── infrared.py\n"
        "│   │   ├── db/                     # 数据访问层\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── models.py           # SQLAlchemy模型\n"
        "│   │   │   ├── catalog.py          # 目录查询\n"
        "│   │   │   └── migrations/         # Alembic迁移\n"
        "│   │   ├── visualization/          # 可视化数据生成\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── coverage_plot.py    # 覆盖图数据\n"
        "│   │   │   └── report.py           # 报告生成\n"
        "│   │   └── api/                    # 对外API（FastAPI）\n"
        "│   │       ├── __init__.py\n"
        "│   │       └── server.py\n"
        "│   └── tests/                      # 单元测试\n"
        "│       ├── test_thin_lens.py\n"
        "│       ├── test_matching.py\n"
        "│       └── test_compatibility.py\n"
    )
    new_engine = (
        "├── engine/                         # Python 核心引擎\n"
        "│   ├── pyproject.toml\n"
        "│   ├── alembic.ini\n"
        "│   ├── build_sidecar.py            # PyInstaller 打包脚本\n"
        "│   ├── optibench/\n"
        "│   │   ├── __init__.py\n"
        "│   │   ├── __main__.py             # 命令行入口\n"
        "│   │   ├── core/                   # 基础光学计算\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── thin_lens.py        # 薄透镜公式 + 景深计算\n"
        "│   │   │   ├── sensor.py           # 传感器标准化\n"
        "│   │   │   ├── types.py            # 共享数据类型\n"
        "│   │   │   └── utils.py            # 通用工具\n"
        "│   │   ├── matching/               # 匹配引擎\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── engine.py           # 主匹配引擎 + 流水线\n"
        "│   │   │   └── scoring.py          # 评分与 TOPSIS 排序\n"
        "│   │   ├── domains/                # 领域模块\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── base.py             # DomainModule 接口\n"
        "│   │   │   ├── industrial.py\n"
        "│   │   │   ├── microscope.py\n"
        "│   │   │   ├── infrared.py\n"
        "│   │   │   └── photography.py      # 摄影领域（已加入）\n"
        "│   │   ├── db/                     # 数据访问层\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── models.py           # SQLAlchemy 模型\n"
        "│   │   │   ├── catalog.py          # 目录查询（参数化）\n"
        "│   │   │   └── migrations/         # Alembic 迁移\n"
        "│   │   ├── visualization/          # 可视化数据生成\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   ├── coverage.py         # 传感器覆盖图数据\n"
        "│   │   │   ├── coc.py              # 弥散圆/景深图数据\n"
        "│   │   │   └── mtf.py              # MTF 曲线数据\n"
        "│   │   ├── export/                 # 报告导出\n"
        "│   │   │   ├── csv_exporter.py\n"
        "│   │   │   ├── excel_exporter.py\n"
        "│   │   │   ├── pdf_exporter.py\n"
        "│   │   │   └── sanitize.py\n"
        "│   │   ├── knowledge/              # 知识推理与预设\n"
        "│   │   │   ├── base.py\n"
        "│   │   │   ├── constraints.py\n"
        "│   │   │   ├── engine.py\n"
        "│   │   │   ├── formulas.py\n"
        "│   │   │   └── presets.py\n"
        "│   │   ├── physics/                # 物理常数\n"
        "│   │   │   ├── __init__.py\n"
        "│   │   │   └── constants.py\n"
        "│   │   └── api/                    # 对外 API（FastAPI）\n"
        "│   │       ├── __init__.py\n"
        "│   │       ├── server.py           # 路由、生命周期、认证（待拆分）\n"
        "│   │       ├── catalog_router.py   # 器件目录 CRUD + 导入\n"
        "│   │       └── import_pipe.py      # CSV/Excel 导入管道\n"
        "│   └── tests/                      # 单元/集成测试\n"
        "│       ├── test_api.py\n"
        "│       ├── test_matching.py\n"
        "│       ├── test_migrations.py\n"
        "│       ├── test_lifecycle.py\n"
        "│       └── test_catalog_import.py\n"
    )
    text = text.replace(old_engine, new_engine)

    old_db = (
        "├── database/                       # 数据库与数据\n"
        "│   ├── schema.sql                  # 完整Schema\n"
        "│   ├── seed_data/                  # 种子数据\n"
        "│   │   ├── lenses/\n"
        "│   │   ├── detectors/\n"
        "│   │   └── manufacturers.csv\n"
        "│   └── import_scripts/             # 数据导入脚本\n"
        "│       ├── crawler/\n"
        "│       └── pdf_parser/\n"
    )
    new_db = (
        "├── database/                       # 数据库与数据\n"
        "│   ├── seed_data/                  # 种子数据\n"
        "│   │   └── import_scripts/\n"
        "│   └── import_scripts/             # 数据导入脚本\n"
        "│       └── ...\n"
        "> **注意**：Schema 由 Alembic 迁移管理，不存在单独的 `schema.sql`。\n"
    )
    text = text.replace(old_db, new_db)

    old_github = (
        "├── .github/\n"
        "    └── workflows/\n"
        "        ├── ci.yml\n"
        "        └── release.yml\n"
    )
    new_github = (
        "├── .github/\n"
        "    └── workflows/\n"
        "        ├── ci.yml                  # 已存在\n"
        "        └── release.yml             # 尚未创建\n"
    )
    text = text.replace(old_github, new_github)

    # Add release.yml note after CI/CD snippet
    old = (
        "      - name: Upload Artifacts\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: optibench-${{ matrix.platform }}\n"
        "          path: apps/desktop/src-tauri/target/release/bundle/\n"
        "```\n"
        "\n"
        "### 7.2 发布产物\n"
    )
    new = (
        "      - name: Upload Artifacts\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: optibench-${{ matrix.platform }}\n"
        "          path: apps/desktop/src-tauri/target/release/bundle/\n"
        "```\n"
        "\n"
        "> **注意**：当前仓库中 `.github/workflows/release.yml` 尚未创建，仅有 `ci.yml`。\n"
        "> 上述 release 流水线为目标设计，需在后续迭代中落地。\n"
        "\n"
        "### 7.2 发布产物\n"
    )
    text = text.replace(old, new)

    path.write_text(text, encoding="utf-8")
    print("Updated tech-stack.md")


if __name__ == "__main__":
    update_software_architecture()
    update_core_algorithms()
    update_database_design()
    update_tech_stack()
    print("Done")