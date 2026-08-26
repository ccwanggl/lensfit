# 前端巨型文件重构计划（api.ts / LearningHub.tsx）

> 制定日期：2026-08-26
> 状态：草案——仅立项，未进入执行；每阶段开工前须单独确认
> 依据：`docs/development/reviews/2026-08-25-deep-codebase-review.md`（M1：前端巨型组件与四域重复编排）、2026-08-26 全仓深度评审（`LearningHub.tsx` 896 行、`utils/api.ts` 814 行持续膨胀）
> 边界：本计划只做结构拆分与模块化，不改任何业务行为、不改四领域工作台页面、不触碰 `engine/optibench/matching`。

## 0. 总览

| 阶段 | 内容 | 核心验收 |
|---|---|---|
| 阶段 A | `utils/api.ts` 按后端域拆分 | 调用方零改动；vitest / tsc / build 全绿 |
| 阶段 B | `lab/LearningHub.tsx` 子视图拆分 | 行为等价；单文件 ≤400 行 |

明确不做（YAGNI）：不改 API 协议与错误处理语义、不引入新状态管理库、不动 `pages/` 四域工作台组件、不动 `matching/engine.py`（遗留豁免）。

## 1. 阶段 A：utils/api.ts 领域化拆分

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

## 2. 阶段 B：LearningHub 子视图拆分

### 目标

将 896 行的 LearningHub 按既有 UI 区域拆为职责单一的子组件与自定义 hooks，渲染行为与进度上报完全等价。

### 设计要点

- TutorialView / PathView / QuizPanel 已是独立组件，本阶段抽取的是 LearningHub 内部剩余块：实验选择器、运行结果容器、面包板 preset 分发逻辑。
- 新代码放 `apps/desktop/src/lab/hub/`：展示组件 + 对应 hooks（如 `useExperimentRun`）。
- 保持既有 lazy 加载边界不变；`useReportProgress` 上报点位一一保留。

### 进入条件

- 阶段 A 已完成并合入 master。

### 退出条件

- `LearningHub.tsx` ≤400 行；新增组件/hooks 有针对性测试或被现有 lab 测试覆盖。
- vitest / tsc / build 全绿；PathView/LearningHub 现有测试不改断言即通过。

### 回滚条件

- 拆分破坏懒加载边界或丢失进度上报 → 回退该切片，不影响阶段 A 成果。

## 3. 验证命令

```bash
cd apps/desktop && npm run test && npx tsc --noEmit && npm run build
```

## 4. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 模块间循环 import | 中 | 类型收敛 `types.ts`；tsc 通过为准，可选 `madge --circular` 复核 |
| 聚合出口掩盖死代码 | 低 | 阶段 A 合入后单独审计清理，不在本计划内顺手做 |
| 拆分引入行为漂移 | 中 | 纯移动不改逻辑；以现有测试全绿为门槛 |

## 5. 执行约束

- 每阶段开工前在本文件记录 checkpoint 勾选并征得确认；一次只开一个阶段。
- 实施期间发现 bug 一律记录、不顺手修，另行走缺陷处理。
