# 学习者状态规格（Learning Records v1）

> 版本：v1
> 日期：2026-08-24
> 依据：`docs/development/plans/active/2026-08-learning-first-repositioning-plan.md` 阶段 2、`docs/development/decisions/ADR-003-learning-first-pivot.md`
> 实现：`engine/optibench/db/models.py`（`LearningRecord`）、`engine/optibench/db/migrations/versions/004_add_learning_records.py`、`engine/optibench/api/routers/learning.py`、`engine/optibench/api/routers/curriculum.py`、`apps/desktop/src/lab/reportProgress.ts`

## 1. 定位

学习者状态记录"谁对哪个学习项做过什么"。阶段 2 落地最小闭环：SQLite 持久化 + GET/PUT API + curriculum graph 状态合并 + 前端三处上报（沙盘完成、教程浏览）。不做账号系统（ADR-003）：单学习者 `learner_id="default"`，字段仅为未来多学习者预留。

## 2. 数据模型

表：`learning_records`（Alembic migration `004`，down_revision `0ac6c641b5d7`）。

| 列 | 类型 | 说明 |
|---|---|---|
| `id` | Integer PK | 自增主键 |
| `learner_id` | String | 学习者 id，默认 `"default"` |
| `item_kind` | String | 学习项类型，对齐 curriculum 节点 kind：`concept` / `experiment` / `preset` / `practice` |
| `item_id` | String | 学习项 id（概念 id / 实验 id / preset id / 实践域 id） |
| `status` | String | `viewed` / `completed` / `scored` |
| `score` | Float，可空 | 仅 `scored` 状态允许带分；其余状态带分返回 422 |
| `updated_at` | DateTime，可空 | 最近一次更新时间（服务端写入） |

约束：

- `UniqueConstraint("learner_id", "item_kind", "item_id")`：同一学习者对同一学习项只有一条记录，重复上报为 upsert（更新 `status`/`score`/`updated_at`）。
- `Index("ix_learning_learner_kind")` 于 `(learner_id, item_kind)`：支撑按类型过滤查询。

## 3. API

### `GET /api/v1/learning/progress`

查询参数：`learner_id`（默认 `"default"`）、`item_kind`（可选过滤）。

响应：`{ "items": [ { "learner_id", "item_kind", "item_id", "status", "score", "updated_at" } ] }`，按 `updated_at` 倒序。

### `PUT /api/v1/learning/progress`

请求体：

```json
{ "item_kind": "experiment", "item_id": "thin-lens", "status": "completed", "score": null }
```

- `learner_id` 可选，默认 `"default"`。
- upsert 语义：已存在同 (learner, kind, id) 记录则更新，否则插入。
- 校验：`status` 非 `scored` 时携带非空 `score` 返回 422。

响应：写入后的记录（同 GET 的单项结构）。

## 4. curriculum graph 状态合并

`GET /api/v1/curriculum/graph` 注入数据库会话，合并 default learner 的记录到节点 `status`：

- 记录 `status` 为 `completed` 或 `scored` → 节点 `completed`；
- 记录 `status` 为 `viewed` → 节点 `viewed`；
- 无记录 → `not_started`；
- 同一节点同时存在多条历史状态时 `completed` 优先于 `viewed`（upsert 模型下同项仅一条记录，优先级规则是防御性的）。

合并只发生在 API 响应层，不回写图定义；`curriculum.yaml` 保持无状态。

## 5. 前端上报

统一走 `useReportProgress()`（`apps/desktop/src/lab/reportProgress.ts`）：

- 按 `(kind, id, status)` 在组件生命周期内去重，失败清除去重标记允许下次重试。
- 上报成功后 `invalidateQueries(["curriculum-graph"])`，路径视图自动刷新合并状态。

接入点：

| 场景 | 上报内容 | 触发时机 |
|---|---|---|
| 沙盘实验运行成功（`LearningHub.tsx`） | `(experiment\|preset, activeExperimentId, "completed")` | run 查询返回结果且无错误 |
| 教程打开（`TutorialView.tsx` `ConceptDetail`） | `(concept, conceptId, "viewed")` | 概念详情加载成功 |
| 路径视图（`PathView.tsx`） | 不上报，只读 graph `status` 渲染完成集合与锁定 | — |

## 6. localStorage 迁移决策

**决策：明确丢弃，不迁移。**

旧实现 `apps/desktop/src/hooks/useLearningProgress.ts` 用 localStorage 存四领域工作台内部的章节/测验勾选状态，其键命名空间（领域工作台 UI 状态）与学习路径 item 命名空间（concept/experiment/preset/practice id）不重叠，无数据可迁、也无必要迁。

- 旧 hook 保留不动，继续服务四领域工作台内部 UI；阶段 4（实践域归口）再统一处理。
- 学习路径相关进度一律走本规格的 API，不新增任何 localStorage 进度键。

## 7. 验收标准

- migration 可 upgrade → downgrade → 再 upgrade（`engine/tests/test_learning_records.py`）。
- PUT/GET、upsert、kind 过滤、scored 带分、非 scored 带分 422、graph 合并（`engine/tests/test_api_learning.py`）。
- PathView 以 graph `status` 渲染完成集合与解锁（`apps/desktop/src/lab/PathView.test.tsx`）。
- 上报去重、失效刷新、失败重试（`apps/desktop/src/lab/reportProgress.test.tsx`）。
