# 学习优先定位转换计划

> 制定日期：2026-08-24
> 依据：`docs/development/decisions/ADR-003-learning-first-pivot.md`、`docs/development/product/roadmap.md`（2026-08-24 版）
> 地位：本计划是当前**第一优先级执行计划**。面包板计划（`2026-06-optical-breadboard-next-steps.md`）的阶段 6.5/7 继续有效，与本计划并行，门禁不变。

## 0. 总览

| 阶段 | 内容 | 对应 roadmap |
|---|---|---|
| 阶段 0 | 内容合同 + 内容管道（engine 内容 API + 前端教程渲染） | LM1 |
| 阶段 1 | 学习路径图（声明式 DAG + API + 前端路径视图） | LM2 |
| 阶段 2 | 学习者状态（SQLite 表 + API + 前端进度接入） | LM3 |
| 阶段 3 | 评测泛化（通用测验组件 + assessment 落地） | LM7 |
| 阶段 4 | 应用壳导航反转（学习中心主壳 + 选型收编实践场） | LM4 |
| 持续 | 教程正文补写（内容工作，阶段 0 后按路径优先级分批） | LM6 |

明确不做（YAGNI）：掌握度模型/自适应推荐、账号系统、云同步、通用画布、学习内容社区化、对匹配引擎的任何重构。

## 1. 阶段 0：内容合同 + 内容管道

### 目标

让 `modules/` 的 markdown 教程从孤儿文档变为软件内可读内容：定义内容合同，engine 提供内容 API，前端在学习中心渲染教程。

### 设计要点

- **内容合同 v1**：modules 下每篇教程 markdown 的 frontmatter 必含 `id`（概念 id，全局唯一）、`title`、`module`（如 `20-geometric-optics`）、`difficulty`（foundation/intermediate/advanced）、`prerequisites`（概念 id 列表）、`linked_experiments`（实验 id 列表，可空）、`status`（draft/published）。正文为 markdown。
- **内容索引**：engine 启动时扫描 `modules/**/*.md`，构建只读索引（id → 元数据 + 正文路径）。无数据库表，纯文件扫描，KISS。
- **API**：`GET /api/v1/content/concepts`（索引列表）、`GET /api/v1/content/concepts/{id}`（含正文）。
- **前端**：学习中心新增“教程”视图，按 module 分组列出概念，点击渲染 markdown 正文，侧栏显示关联实验入口。
- **路径根**：modules 目录路径通过配置注入，sidecar 打包时随包携带（参考阶段 0 面包板对实验收集的处理方式）。

### 进入条件

- ADR-003 状态为接受。

### 退出条件

- 内容合同文档落在 `docs/development/specifications/lab/content-contract.md`。
- 上述两个 API 返回 modules 现有内容；`linked_concepts` 旧 vault 路径债务在本次映射中清理（`experiment-catalog.md:7` 挂账项）。
- 前端教程视图能打开并渲染至少一篇现有 markdown（可用 `modules/20-geometric-optics/learning/CMOS-fundamentals.md` 验证）。
- 新增 pytest 覆盖索引构建与 API；非法 frontmatter 有明确报错。

### 涉及文件（预计）

- `engine/optibench/content/`（新包）：`contract.py`（schema 校验）、`index.py`（扫描索引）、`loader.py`。
- `engine/optibench/api/routers/content.py`（新）。
- `apps/desktop/src/lab/TutorialView.tsx`（新）+ LearningHub 挂载。
- `docs/development/specifications/lab/content-contract.md`（新）。

### 回滚条件

- 内容合同需要数据库表才能表达（说明设计过重，退回简化）。

## 2. 阶段 1：学习路径图

### 目标

用声明式 DAG 把概念、实验、面包板 preset、实践项目串成可引导的学习路径，前端提供路径视图。

### 设计要点

- **路径定义文件**：`modules/curriculum.yaml`（单文件，KISS），节点 `{id, kind: concept|experiment|preset|practice, ref, title}`，边来自各节点 `prerequisites`。实验/preset 节点直接引用 registry 已有 id；concept 节点引用阶段 0 的概念 id；practice 节点引用四个实践域。
- **PracticeActivity 接口**：`engine/optibench/practice/base.py` 定义统一接口（`id`、`title`、`entry`（前端定位信息）、`available()`），matching 四域与面包板 preset 各自注册实现。学习层只依赖此接口。
- **API**：`GET /api/v1/curriculum/graph`（节点+边+状态合并后返回）。
- **前端路径视图**：按 module 层级（10→50）分层的线性列表 + 先修锁定提示。不做图形化 DAG 编辑器、不做掌握度模型（YAGNI）。
- 实验 `prerequisites` 中物理不合理的声明（如 `polarization-malus` 依赖 `thin-lens`）在本阶段修正。

### 进入条件

- 阶段 0 退出条件全部满足。

### 退出条件

- `curriculum.yaml` 覆盖现有 19 个实验、2 个面包板 preset、4 个实践域，先修关系经物理合理性检查。
- 前端路径视图：未完成先修的节点显示锁定原因；点击实验节点跳转沙盘并加载对应实验。
- pytest 覆盖图构建（含环检测、悬空引用检测）；前端 Vitest 覆盖锁定逻辑。

### 涉及文件（预计）

- `modules/curriculum.yaml`（新）。
- `engine/optibench/curriculum/`（新包）：`graph.py`、`loader.py`。
- `engine/optibench/practice/`（新包）：`base.py`、`matching.py`、`breadboard.py`。
- `engine/optibench/api/routers/curriculum.py`（新）。
- `apps/desktop/src/lab/PathView.tsx`（新）。

### 回滚条件

- 路径表达需要超出单 YAML 文件的复杂度（如多路径分支、掌握度模型）。

## 3. 阶段 2：学习者状态

### 目标

本地持久化学习进度：概念已读、实验完成、测验成绩，前端路径视图显示完成度。

### 设计要点

- **SQLite 新表**（Alembic migration）：`learning_records`（`id`, `learner_id`（默认 `default`，预留）, `item_kind`, `item_id`, `status`（viewed/completed/scored）, `score`, `updated_at`）。单表，KISS。
- **API**：`GET/PUT /api/v1/learning/progress`（按 item 查询/上报）。
- **前端**：替换现有 localStorage 碎片（`useLearningProgress.ts` 迁移到 API）；路径视图节点显示完成标记。
- 不做账号、不做多端同步（LW2）。

### 进入条件

- 阶段 1 退出条件全部满足。

### 退出条件

- migration 可升降级；进度上报/查询 API 有 pytest 覆盖。
- 路径视图与沙盘实验完成后写进度，刷新后保留。
- 旧 localStorage 数据有一次性迁移或明确丢弃（二选一，记录决策）。

### 回滚条件

- 需要引入多表关联或 ORM 关系才能表达进度（说明模型过重）。

## 4. 阶段 3：评测泛化

### 目标

把 `LearningQuiz` 从四领域章节专用泛化为通用测验组件，落地 `modules/*/assessment/README.md` 中已写好的评估标准。

### 设计要点

- 测验题定义并入内容合同 v1（题目 markdown 或 YAML，随 modules 扫描）。
- 成绩写入阶段 2 的 `learning_records`。
- 先从 1-2 个 module 的题目落地验证，不追求全覆盖。

### 进入条件

- 阶段 2 退出条件全部满足。

### 退出条件

- 通用测验组件在路径视图和教程视图均可挂载；至少 1 个 module 有完整测验；成绩入库。

## 5. 阶段 4：应用壳导航反转

### 目标

学习中心成为默认首页与应用主壳，四个领域工作台收编为实践场入口。

### 设计要点

- `App.tsx`：Tab 重排——学习中心（默认）拆为“学习路径 / 实验沙盘 / 教程”子视图；四领域工作台收进“实践场”分组；项目/器件库/游乐场/设置保留为工具区。
- 四领域工作台组件零改动，仅入口归位。
- 设置面板“学习模式”开关评审去留（默认学习定位下可能冗余）。

### 进入条件

- 阶段 1 退出条件满足（路径视图存在，主壳才有内容可展示）。阶段 2/3 不阻塞本阶段。

### 退出条件

- 启动默认进入学习路径视图；实践场四个工作台功能回归无损；`npm run build` 与前端测试通过。

## 6. 持续任务：教程正文补写

阶段 0 内容管道就绪后启动，按学习路径顺序分批补写 modules 正文（内容工作，不走 checkpoint）。优先顺序：

1. 10-foundations 核心概念（已有实验可联动的优先）。
2. 20-geometric-optics（配合缺口实验：反射/平面镜、色散棱镜——新实验按 LS2 另行立项）。
3. 30-wave-optics（菲涅尔衍射、干涉仪）。
4. 40-spectroscopy、50-optical-design。

每篇正文须满足内容合同 v1 并链接至少一个已有实验。

## 7. 验证命令（各阶段通用）

```powershell
cd "E:/OpticHackerSpace/optibench/engine"
python -m pytest tests/ -q

cd "E:/OpticHackerSpace/optibench/apps/desktop"
npm run build
npm run test
```

## 8. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 内容合同设计过度 | 高 | 合同 v1 只允许上述必需字段；新增字段走合同版本化 |
| 学习层耦合匹配引擎 | 高 | `PracticeActivity` 接口 + import 方向测试 |
| 各阶段间前端状态管理膨胀 | 中 | 每阶段退出条件含前端测试；状态集中在既有 zustand store 扩展 |
| 与面包板阶段 6.5/7 冲突 | 低 | 面包板边界不动；面包板 preset 以 PracticeActivity 注册进路径图 |
