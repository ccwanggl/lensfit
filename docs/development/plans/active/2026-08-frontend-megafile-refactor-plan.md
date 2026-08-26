# 前端巨型文件重构计划（api.ts / LearningHub.tsx / 四域页面）

> 制定日期：2026-08-26（同日 v2 修订：纳入 2026-08-25 评审 M1 的另一半范围「DomainPageShell」，并补充与面包板 checkpoint 的协调条款）
> 状态：切片 A、B 已完成（2026-08-26）；切片 C 待确认后开工
> 依据：`docs/development/reviews/2026-08-25-deep-codebase-review.md`（M1：前端巨型组件与四域重复编排）、2026-08-26 全仓深度评审（`LearningHub.tsx` 896 行、`utils/api.ts` 814 行持续膨胀）
> 边界：全部切片只做结构拆分与模块化，不改任何业务行为与 API 协议语义；四域页面仅做结构抽取，不做视觉改版；不触碰 `engine/optibench/matching`。

## 0. 总览

| 切片 | 内容 | 目标文件（当前行数） | 核心验收 |
|---|---|---|---|
| A | `utils/api.ts` 按后端域拆分 | utils/api.ts（814） | 调用方零改动；vitest / tsc / build 全绿 |
| B | `lab/LearningHub.tsx` 子视图拆分 | lab/LearningHub.tsx（896） | 行为等价；单文件 ≤400 行 |
| C | 四域页面 DomainPageShell 抽取 | IndustrialPage(694)/MicroscopePage(736)/PhotographyPage(666)/InfraredPage(672) 及配套 *LearningHub(502/387/381/416) | 编排层去重；行为零变化 |

明确不做（YAGNI）：不改匹配算法与评分逻辑、不引入新状态管理库、不改路由结构、不动 `matching/engine.py`（遗留豁免）、不做四域页面的视觉改版。

## 1. 切片 A：utils/api.ts 领域化拆分

> **状态：✅ 已完成（2026-08-26）**——拆出 `src/api/` 12 个域模块（client/types/domains/matching/visualization/catalog/projects/export/knowledge/lab/content/curriculum/learning），`utils/api.ts` 转为 23 行聚合出口；vitest 59 通过、tsc 通过、build 成功，最大单文件 catalog.ts 168 行。

### 目标

将 814 行聚合模块拆为按后端路由域组织的薄模块；`utils/api.ts` 保留为聚合出口，存量调用方 import 路径零改动。

### 设计要点

- 新建 `apps/desktop/src/api/`：`client.ts`（fetch 封装 / baseUrl / API key 注入）、`matching.ts`、`catalog.ts`、`projects.ts`、`export.ts`、`visualization.ts`、`content.ts`、`curriculum.ts`、`learning.ts`、`types.ts`（跨域共享类型）。
- 各域函数与随行类型整体平移，纯移动不改逻辑。
- `utils/api.ts` 改为 `export * from "../api/*"` 聚合出口并标注 deprecated，引导新代码直用子模块。
- 循环依赖以防为主：类型一律收敛到 `types.ts`，实现模块不得反向 import `utils/api.ts`。

### 进入条件

- 无其他正在进行的触及 `utils/api.ts` 的改动。

### 退出条件

- `npm run test`、`npx tsc --noEmit`、`npm run build` 全绿。
- 除 `client.ts` 外单文件 ≤300 行。
- 存量 `from ".../utils/api"` 引用数量不减不增（允许原样保留）。

### 回滚条件

- 出现无法快速定位的行为差异 → 废弃子模块拆分，保留聚合出口回退点。

## 2. 切片 B：LearningHub 子视图拆分

> **状态：✅ 已完成（2026-08-26）**——LearningHub 896→374 行；拆出 `src/lab/hub/` 七模块：ViewSwitcher / DisplayCard / CatalogColumn / panels（Parameter·Media·Data·Hints）/ states（Badge·Loading·Error·Empty）/ TabButton / BreadboardPresetHeader（经 LearningHub 再导出保持测试导入兼容）。全部字节级平移，数据查询与 `useReportProgress` 上报点保留在 LearningHub 原位，现有测试零改动全绿（vitest 59 / tsc / build）。

### 目标

将 896 行的 LearningHub 按既有 UI 区域拆为职责单一的子组件与自定义 hooks，渲染行为与进度上报完全等价。

### 设计要点

- TutorialView / PathView / QuizPanel 已是独立组件，本切片抽取的是 LearningHub 内部剩余块：实验选择器、运行结果容器、面包板 preset 分发逻辑。
- 新代码放 `apps/desktop/src/lab/hub/`：展示组件 + 对应 hooks（如 `useExperimentRun`）。
- 保持既有 lazy 加载边界不变；`useReportProgress` 上报点位一一保留。

### 进入条件

- 切片 A 已完成并合入 master。

### 退出条件

- `LearningHub.tsx` ≤400 行；新增组件/hooks 有针对性测试或被现有 lab 测试覆盖。
- vitest / tsc / build 全绿；PathView/LearningHub 现有测试不改断言即通过。

### 回滚条件

- 拆分破坏懒加载边界或丢失进度上报 → 回退该切片，不影响切片 A 成果。

## 3. 切片 C：四域页面 DomainPageShell 抽取

### 目标

消解四域页面编排层的结构性重复（2026-08-25 评审 M1 的另一半）：工业视觉 / 显微镜 / 摄影 / 红外四个页面共享同一套「页头—表单—运行—结果」编排骨架，仅领域参数不同。

### 设计要点

- 新增 `apps/desktop/src/components/domain/`：
  - `DomainPageShell`：页头、Tab/分组、结果区布局、状态装配的共享壳；
  - 配置驱动表单渲染器：各域参数以声明式配置描述，复用既有 `DomainForm` / `useMatching` 能力，不重写匹配交互。
- **表征测试先行**：四页目前无任何组件测试——动手前先为每页补最小冒烟测试（可渲染、提交路径触发、关键区块出现），作为重构安全网；此为本切片的第一个 checkpoint。
- 行为零变化：请求参数、评分展示、`reportProgress` 上报点位保持不变；配套 `*LearningHub` 的 localStorage 进度逻辑不在本切片范围内迁移（决策见 `specifications/lab/learning-records.md` §6）。
- 分域逐个迁移（industrial → photography → microscope → infrared），每域一笔可独立回退的提交。

### 进入条件

- 切片 A 已完成并合入 master（页面大量依赖 api 层，先稳定底层）。切片 B 与 C 无相互依赖，可分别独立执行。

### 退出条件

- 每个域页面文件的编排代码 ≤400 行（数据配置外置不计入）。
- `DomainPageShell` 与配置渲染器有独立测试；四页冒烟测试全绿。
- vitest / tsc / build 全绿；人工走查四域各一条完整匹配路径无行为差异。

### 回滚条件

- 任一域出现无法快速定位的视觉或行为回归 → 单独回退该域迁移提交，shell 保留待查。

## 4. 与面包板 checkpoint 的协调

- 2026-06 面包板计划的后续 checkpoint（阶段 6.5/7）若需改动 `lab/LearningHub.tsx` 或 `utils/api.ts`：与本计划切片 A/B **不并行**——先到先得，后开工的一方基于对方完成后的 master 进行。
- 依据：`2026-06-optical-breadboard-next-steps.md` 已预期未来对 LearningHub「无改动或仅小幅调整」，冲突概率低，无需预先排期，只需遵守不并行约定。

## 5. 验证命令

```bash
cd apps/desktop && npm run test && npx tsc --noEmit && npm run build
```

## 6. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 模块间循环 import | 中 | 类型收敛 `types.ts`；tsc 通过为准，可选 `madge --circular` 复核 |
| 聚合出口掩盖死代码 | 低 | 切片 A 合入后单独审计清理，不在本计划内顺手做 |
| 拆分引入行为漂移 | 中 | 纯移动不改逻辑；以现有测试全绿为门槛 |
| 切片 C 缺少页面级测试安全网 | 高 | 表征测试先行作为独立 checkpoint，未建网不开工 |
| 与面包板 checkpoint 撞车 | 低 | §4 不并行约定 |

## 7. 执行约束

- 每切片开工前在本文件勾选对应 checkpoint 并征得确认；一次只开一个切片，切片 C 内部分域串行。
- 实施期间发现 bug 一律记录、不顺手修，另行走缺陷处理。
