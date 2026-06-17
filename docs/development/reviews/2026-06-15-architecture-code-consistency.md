# LensFit 架构文档与代码实现一致性检查

> 检查日期：2026-06-15  
> 检查范围：`docs/development/architecture/` 下的四份文档与 `engine/`、`apps/desktop/` 当前实现  
> 检查方式：静态对照 + 关键代码路径抽查 + 依赖清单核对

---

## 1. 总体结论

当前代码已经实现了文档中描述的**大部分核心概念**：

- 四级匹配流水线（`index_pre_filter` → `quick_hard_filter` → `apply_domain_constraints` → `score_candidates` → `rank_results`）已落地。
- `DomainModule` 抽象接口已存在并被四个领域实现。
- Tauri + Python sidecar 的桌面架构已运行，健康检查、随机端口、API key 传递均已实现。
- 可视化数据生成（coverage / MTF / CoC）和报告导出（CSV / Excel / PDF）已存在。

但存在**两类显著不一致**：

1. **文档过度描述尚未实现的模块**：例如独立的 ProjectMgr / ConfigMgr / AuditLogger、适配器目录、光谱响应表、公式注册表、异步 PDF 导出等。
2. **实现细节与文档描述有偏差**：例如缓存表未使用、sidecar supervisor 没有自动重启、部分 API 端点未实现等。

> **本次修复后**：四份架构文档已更新，未实现内容已明确标注；`python-constraint`、`asteval`、`matplotlib` 已从依赖中移除；`server.py` 已拆分为 `lensfit/api/routers/` 下的独立路由模块。

当前文档适合作为“目标架构”阅读，但若作为新成员的 onboarding 材料，会误导其对已实现能力的判断。建议把未实现部分明确标注为 `TODO / 规划中`，并修正已变更的实现细节。

---

## 2. 按文档逐项核对

### 2.1 `software-architecture.md`

| 文档描述 | 代码实际 | 一致性 | 说明 |
|---|---|:---:|:---|
| 应用层包含 ProjectMgr / ConfigMgr / TaskQueue / AuditLogger / ReportGen / ImportPipe / ExportSvc / Cache Layer | 项目管理、匹配、可视化、导出等能力已拆分为 `lensfit/api/routers/` 下独立路由；TaskQueue 仍在 `MatchingEngine` 内部；无独立 ConfigMgr / AuditLogger / Cache Layer | ⚠️ 部分 | `server.py` 仅负责应用组装与生命周期；独立业务模块仍缺失 |
| MatchingEngine 四级流水线：IndexPreFilter / QuickHardFilter / DomainHardFilter / FullScoring / ResultRanker | `engine.py` 中对应 `_match_one_pass` 调用 `index_pre_filter`、`quick_hard_filter`、`apply_domain_constraints`、`score_candidates`、`rank_results` | ✅ 基本一致 | 领域约束阶段的方法名是 `apply_domain_constraints`，文档写为 `DomainHardFilter` |
| Stage 1 在数据库查询阶段用复合索引过滤，候选从 10M → <100K | `index_pre_filter` 目前加载全部镜头/探测器后在 Python 中过滤；`CatalogQuery.query_lenses` 已支持参数化查询但未被调用 | ❌ 不一致 | 性能潜力未发挥，大数据量时会是瓶颈 |
| `DomainModule` 接口含 `get_parameters`、`get_hard_constraints`、`get_scoring_dimensions`、`calculate_derived`、`get_visual_data_generators` | 实际接口无 `get_visual_data_generators`；可视化由 `visualization/` 包直接根据 lens/det 尺寸计算 | ❌ 不一致 | 新增领域不需要提供可视化生成器 |
| 多目标排序使用加权 TOPSIS + NSGA-II（Pareto 模式可选） | `TopsisRanker` 已实现；代码中无 Pareto 排序器，Pareto 筛选目前在前端 `CompareParetoToolbar` 中做 | ⚠️ 部分 | 后端算法文档与前端实现分离 |
| 缓存层缓存 Stage 4 结果，键为 `lens_id + detector_id + algorithm_version` | `compatibility_cache` 表存在但**没有任何代码读写它** | ❌ 未使用 | 整个缓存机制尚未接入匹配流程 |
| VisualDataGen 输出 SensorCoverageData / FOVSchematicData / MTFNyquistData / SpectralOverlapData / ComparisonRadarData | 实际只有 `CoveragePlotData`、`MtfCurve`、`CocChart`；无 FOV 示意图、光谱重叠、雷达图数据生成器 | ⚠️ 部分 | 雷达图在前端用 Recharts 直接绘制 |
| 数据层为 MasterDB + UserProjectDB 双库，含 SyncManager / FormulaReg / PluginReg / ConfigStore | 实际只有单个 SQLite 文件，同时存放目录和用户项目；无 SyncManager、FormulaReg、PluginReg、ConfigStore | ❌ 不一致 | 文档中多个数据层模块未实现 |
| 异步任务模型端点含 `/api/v1/match/async/{task_id}/result` | `/api/v1/match/async/{task_id}/result` 已实现 | ✅ 一致 | — |
| 存在 `/api/v1/export/pdf/async` 与 `/api/v1/export/pdf/async/{task_id}` | 实际只有同步 `/api/v1/export` 和 `/api/v1/projects/{project_id}/report` | ❌ 不一致 | PDF 导出未走异步任务模型 |
| Sidecar Supervisor 含崩溃自动重启（最多 3 次） | `src-tauri/src/main.rs` 的 `EngineSupervisor` 只有启动、健康检查、kill；无重启逻辑 | ❌ 不一致 | 崩溃后需用户重启应用 |

### 2.2 `core-algorithms.md`

| 文档描述 | 代码实际 | 一致性 | 说明 |
|---|---|:---:|:---|
| 传感器尺寸标准化表与 `sensor_size_from_pixels` | `core/sensor.py` 实现一致，表格内容一致 | ✅ 一致 | — |
| `ThinLensCalculator` 方法集 | `core/thin_lens.py` 已实现 focal/fov/wd/magnification/afov/solve/depth_of_field | ✅ 一致 | — |
| 四级流水线伪代码 | 实际代码结构相似，但 Stage 1 未使用 `query_lenses` 的参数过滤 | ⚠️ 部分 | 见 2.1 |
| 算法性能预估表（小型库 <10ms，大型库 <500ms） | 未做系统性基准测试；现有测试库 91 镜头 × 48 探测器组合量很小 | ⚠️ 待验证 | 建议补充性能回归测试 |
| 传感器-像面覆盖匹配公式 | `visualization/coverage.py` 与文档公式一致 | ✅ 一致 | — |
| 奈奎斯特采样匹配 | `scoring.py:_score_nyquist_match` 与文档逻辑一致 | ✅ 一致 | — |
| 光谱波段匹配、显微镜 C-Mount 适配器匹配 | 仅作为知识文档存在；代码中没有独立函数实现这些完整计算 | ⚠️ 部分 | 部分逻辑分散在领域 `calculate_derived` 中 |

### 2.3 `database-design.md`

| 文档描述 | 代码实际 | 一致性 | 说明 |
|---|---|:---:|:---|
| `manufacturers` 表结构 | 与 `models.py` 基本一致 | ✅ 一致 | 实际缺少 `logo_url`、`name_en`/`name_cn` 字段存在，`is_verified` 存在 |
| `lens_catalog` 表结构 | 与 `models.py` 基本一致 | ⚠️ 基本 | 文档列名 `min_working_distance_mm` / `max_working_distance_mm`，代码使用相同；部分文档列如 `filter_thread_mm` 代码中不存在 |
| `detector_catalog` 表结构 | 与 `models.py` 基本一致 | ⚠️ 基本 | 文档列 `quantum_efficiency_530nm`、`pixel_pitch_um`、`snr_max_db` 等代码中不存在 |
| `adapter_catalog` 表 | **不存在** | ❌ 未实现 | ERD 中画出但无模型、无迁移 |
| `spectral_responses` 表 | **不存在** | ❌ 未实现 | — |
| `compatibility_cache` 表 | 表存在但无运行时写入/读取 | ⚠️ 未使用 | — |
| `formula_registry` 表 | **不存在** | ❌ 未实现 | 文档中 L0/L1/L2/L3 分级公式系统未落地 |
| `lens_catalog_history` 表 | **不存在** | ❌ 未实现 | 数据版本管理未落地 |
| `user_projects` / `project_setups` 表 | 已实现 | ✅ 一致 | 代码中还额外有 `match_result_snapshot` 字段 |
| 数据质量评分模型 `calculate_data_quality_score` | 未实现；模型中有 `data_quality_score` 字段但默认 0 | ⚠️ 部分 | 字段占位，无计算逻辑 |
| 索引清单 | 代码中索引与文档大体对应，但 `lens_catalog` 的复合索引不是 `(category, mount_type, focal_length_mm, image_circle_mm, ...)`，而是多个单列/双列索引 | ⚠️ 部分 | 需复核是否满足 Stage 1 范围查询 |

### 2.4 `tech-stack.md`

| 文档描述 | 代码实际 | 一致性 | 说明 |
|---|---|:---:|:---|
| Python 依赖清单含 `diskcache>=5.6` | `diskcache` 已从 `pyproject.toml` 移除 | ✅ 已修复 | 缓存层尚未落地 |
| 含 `python-constraint`、`asteval` | 已从 `pyproject.toml` 移除 | ✅ 已修复 | 未在代码中使用 |
| 含 `matplotlib` | 已从 `pyproject.toml` 移除 | ✅ 已修复 | PDF 导出使用 `reportlab` |
| 前端依赖清单含 `@tanstack/react-query`、`recharts`、`fabric` | 实际 `package.json` 中均存在 | ✅ 一致 | 实际还多了 `lucide-react` |
| 项目目录结构含 `engine/lensfit/core/dof.py`、`units.py` | 不存在；`depth_of_field` 在 `thin_lens.py`，单位换算未单独成模块 | ❌ 不一致 | — |
| 含 `engine/lensfit/matching/constraints.py`、`solver.py` | 不存在；约束在 `domains/base.py`，排序在 `matching/scoring.py` | ❌ 不一致 | — |
| 含 `engine/lensfit/visualization/report.py` | 不存在；报告生成在 `export/pdf_exporter.py` | ❌ 不一致 | — |
| 含 `database/schema.sql` | 不存在；schema 由 Alembic 迁移管理 | ❌ 不一致 | — |
| 描述 `.github/workflows/release.yml` | 仓库只有 `ci.yml` | ❌ 不一致 | 发布流水线未建立 |
| 描述 sidecar 启动参数 `--port` 和 `--mode desktop` | 实际一致 | ✅ 一致 | — |

---

## 3. 关键风险

1. **性能误导**：文档声称 Stage 1 使用数据库索引将组合从 10M 降到 <100K，但实际代码全量加载后 Python 过滤。当目录扩展到文档规划的几千镜头 × 几千探测器时，首次匹配可能显著慢于文档预估。
2. **功能范围误导**：新读者可能认为 `adapter_catalog`、`formula_registry`、异步 PDF 导出、sidecar 自动重启已经存在，从而对 MVP 完整性产生错误预期。
3. **依赖膨胀**：`python-constraint`、`asteval`、`matplotlib` 三个依赖未使用，却会增加打包体积和许可/安全风险。
4. **单文件 god object**：`server.py` 仍承担路由、生命周期、认证、项目管理、导出、可视化等多重职责，与文档中“应用层独立模块”的目标差距较大。

---

## 4. 建议行动

### 4.1 文档修正（已完成）

- `software-architecture.md`：已标注未实现模块、修正 Stage 1 描述、修正 DomainModule 接口、更新数据层/API/端点/Sidecar 描述。
- `core-algorithms.md`：已补充 Stage 1 实现状态、性能预估待验证、光谱/显微镜适配器未实现的说明。
- `database-design.md`：已标注未实现表、未启用缓存、数据质量评分占位。
- `tech-stack.md`：已更新依赖清单、目录结构、CI/CD 说明。

- 在 `software-architecture.md` 中：
  - 把未实现的模块（ProjectMgr、ConfigMgr、AuditLogger、Cache Layer、SyncManager 等）标注为 **“规划中 / 未实现”**。
  - 修正 Stage 1 描述：说明当前实现是全量加载 + Python 过滤，`CatalogQuery` 的参数化查询已准备好但尚未接入。
  - 移除或标注 `get_visual_data_generators` 接口，说明可视化由 `visualization/` 包统一处理。
  - 修正 API 端点清单，移除 `/api/v1/match/async/{task_id}/result` 和 `/api/v1/export/pdf/async` 等不存在端点，或标注为“目标接口”。
  - 修正 Sidecar Supervisor 描述，说明当前无自动重启。
- 在 `database-design.md` 中：
  - 把 `adapter_catalog`、`spectral_responses`、`formula_registry`、`lens_catalog_history` 标注为 **“未实现”**。
  - 说明 `compatibility_cache` 表已创建但未启用。
  - 修正索引描述，列出实际迁移中的索引。
- 在 `tech-stack.md` 中：
  - 更新依赖清单，移除 `diskcache`。
  - 把 `python-constraint`、`asteval`、`matplotlib` 标注为 **“已引入但未使用，待清理或启用”**。
  - 修正目录结构图，移除不存在文件；补充 `lensfit/api/routers/`、`lensfit/export/`、`lensfit/knowledge/` 等实际目录。
  - 说明 `release.yml` 尚未建立。

### 4.2 代码补齐（按优先级）

- **高**：~~将 `CatalogQuery.query_lenses/query_detectors` 接入 `index_pre_filter`~~（已实现）。
- **中**：~~清理未使用依赖~~（`python-constraint`、`asteval`、`matplotlib` 已从 `pyproject.toml` 移除）。
- **中**：~~拆分 `server.py` 为 `routers/matching.py`、`routers/projects.py`、`routers/visualization.py`、`routers/export.py` 等~~（已完成）。
- **低**：决定是否启用 `compatibility_cache`；若暂不启用，可在文档中说明并考虑从 schema 中移除该表，避免维护空表。

### 4.3 持续一致性机制

- 在 `docs/development/decisions/` 下补充 ADR，记录“Stage 1 先全量加载再过滤”的临时决策及未来迁移计划。
- 每次较大代码重构后，同步更新 `architecture/` 下对应文档，避免再次出现文档领先实现的情况。

---

## 5. 附录：检查用到的关键代码位置

- 匹配引擎：`engine/lensfit/matching/engine.py`
- 评分与 TOPSIS：`engine/lensfit/matching/scoring.py`
- 领域接口：`engine/lensfit/domains/base.py`
- 数据模型：`engine/lensfit/db/models.py`
- 目录查询：`engine/lensfit/db/catalog.py`
- API 路由：`engine/lensfit/api/server.py`、`engine/lensfit/api/routers/`
- 可视化：`engine/lensfit/visualization/coverage.py`
- Sidecar 管理：`apps/desktop/src-tauri/src/main.rs`
- 依赖清单：`engine/pyproject.toml`、`apps/desktop/package.json`
