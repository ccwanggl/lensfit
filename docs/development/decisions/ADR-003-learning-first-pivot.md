# ADR-003：学习优先定位转换（Learning-First Pivot）

**状态**：接受（2026-08-26 全仓深度评审后追认，阶段 0–4 已按执行计划落地）  
**日期**：2026-08-24  
**作者**：OptiBench 架构团队  
**范围**：将产品定位从“镜头-传感器选型工作台（工程师主线）+ Self-Study Lab（学习副线）”反转为“学习辅助为第一要务，选型匹配作为学习实践场景”。执行计划见 `docs/development/plans/active/2026-08-learning-first-repositioning-plan.md`。

## 1. 背景

原定位（`docs/development/product/roadmap.md` 旧版、README）是面向机器视觉/光学工程师的选型工作台，学习中心（Self-Study Lab）是内嵌副线，光学面包板是“副线的高级交互形态”（ADR-002）。

经评审确认的新定位：

1. **第一要务是学习辅助**：目标用户为光学学习者（学生、自学者、转行工程师）。
2. **镜头适配等选型能力是学习实践场景**：学习者掌握理论后，在真实器件数据上做应用练习，而不是产品的主要卖点。

这导致原有优先级假设全部反转：匹配流水线不再是核心域模型，学习路径、教程内容、学习者状态从缺失项变为 Must。

## 2. 决策

**采用“学习层叠加”架构，而非重写：**

- **学习路径图（Curriculum Graph）成为新的核心域模型**：声明式 DAG，节点为概念 / 实验 / 面包板 preset / 实践项目，边为先修关系。
- **选型引擎降级为实践域（Practice Domain）**：匹配流水线、器件 catalog、项目管理全部保留不删，通过统一的 `PracticeActivity` 接口被学习路径引用。
- **新增三个子系统**：内容管道（加载 `modules/` markdown）、学习路径层、学习者状态（本地 SQLite，不做账号系统）。
- **应用壳导航反转**：学习中心升为默认首页与主壳；四个领域工作台收编为学习中心内的实践场入口。
- **ADR-002 的依赖方向继续有效**：`SceneGraph -> Solver Adapter -> 第三方引擎` 不变；面包板从副线高级形态升格为主线核心交互形态，但既有 checkpoint 门禁不变。

## 3. 主要后果

### 正面

- 学习层与选型引擎解耦：选型代码几乎零改动，转换风险集中在新增子系统。
- `DomainModule` 可插拔设计天然适配“实践域”定位，`PracticeActivity` 接口成本低。
- 面包板投资（阶段 0-6 已完成的 SceneGraph/workbench）在新定位下价值放大而非浪费。

### 负面 / 代价

- 新增内容管道、路径图、学习者状态三个子系统，引入新的 API 面与数据库表。
- `modules/` 目前只有大纲无正文，内容补写工作量大（内容工作，非架构工作）。
- 旧 roadmap 的 MoSCoW 排序、商业化章节作废，需重写。

### 替代方案（已否决）

- **A. 推倒重写为纯学习应用**：丢弃选型引擎与 catalog。否决理由：选型是学习定位下最有价值的实践场，且重写违反 KISS。
- **B. 保持双主线并列**：不反转优先级，只做增量学习功能。否决理由：无法解决“无教程、无路径、无进度”的结构性缺口，学习体验永远是从属的。

## 4. 架构边界

- 学习路径图只能通过 `PracticeActivity` 接口引用选型能力，禁止学习层直接 import 匹配流水线内部模块。
- 学习者状态保持本地单用户（SQLite），schema 预留 `learner_id` 字段但不做登录/账号端点。
- `modules/` 内容合同（frontmatter schema）是稳定合同，engine 与前端都依赖它，变更需走版本化。
- 面包板、ray-optics 探针的边界不变：仍按 ADR-002 与面包板 active plan 的 checkpoint 门禁推进。

## 5. 与既有文档的关系

- 本 ADR 取代旧 `product/roadmap.md` 的定位假设；roadmap 已按本决策重写（2026-08-24 版）。
- ADR-002 不废弃：其技术决策（混合架构、域模型隔离）在学习定位下继续有效，仅执行优先级提升。
- 选型相关架构文档（`architecture/software-architecture.md`、`core-algorithms.md`）描述的是实践域内部实现，保持有效。

## 6. 参考

- `docs/development/plans/active/2026-08-learning-first-repositioning-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/architecture/optics-lab/self-study-lab-architecture.md`
- `laser-optics-expansion-report.md`、`non-imaging-optics-expansion-report.md`（缺口证据，非执行依据）
