# 学习路径图规格（Curriculum Graph v1）

> 版本：v1
> 日期：2026-08-24
> 依据：`docs/development/plans/active/2026-08-learning-first-repositioning-plan.md` 阶段 1、`docs/development/decisions/ADR-003-learning-first-pivot.md` 第 4 节
> 实现：`modules/curriculum.yaml`、`engine/optibench/curriculum/`、`engine/optibench/practice/`、`engine/optibench/api/routers/curriculum.py`、`apps/desktop/src/lab/PathView.tsx`

## 1. 定位

学习路径图用一份声明式 YAML 把概念、实验、面包板 preset、实践域串成有向无环图（DAG）。engine 启动时加载、校验并构建图，前端学习路径视图按 module 层级展示。单文件，无数据库表；学习者状态存于独立 SQLite 表 `learning_records`，规格见 `learning-records.md`。

## 2. curriculum.yaml Schema

文件位置：`modules/curriculum.yaml`。顶层为映射，必含 `nodes` 列表。每个节点：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 节点 id，文件内唯一 |
| `kind` | enum | 是 | `concept` / `experiment` / `preset` / `practice` / `assessment` |
| `ref` | string | 是 | 节点引用的目标 id，解析规则见第 3 节 |
| `title` | string | 是 | 展示标题 |
| `prerequisites` | string[] | 否（默认 `[]`） | 先修节点 id 列表，必须引用本文件内已定义的节点 id |
| `module` | string | 否（默认 `""`） | 分层展示层级：`10-foundations` / `20-geometric-optics` / `30-wave-optics` / `40-spectroscopy` / `50-optical-design` / `practice`（实践场层） |
| `source` | string | 否（默认 `""`，仅 concept 节点有意义） | `"vault"` → 知识库理论节点（ADR-004）：`ref` 为知识库 slug，前端经 `knowledgeLinks.json` 解析为 `obsidian://` 深链，引擎跳过内容合同索引校验；空值 → 内容合同概念，ref 必须命中内容索引 |

边不由 `edges` 字段声明，而是从各节点 `prerequisites` 派生：对每个先修关系生成一条 `先修节点 → 依赖节点` 的有向边。

约定：节点 `id` 与被引用的目标 `ref` 保持一致（如实验节点的 `id` 即实验 id），保证先修声明可读。

## 3. ref 解析规则

图构建时按 `kind` 校验 `ref` 必须存在于对应注册表，否则报悬空引用错误：

| kind | 解析目标 |
|---|---|
| `concept` | 内容索引（内容合同 v1 的概念 id，`engine/optibench/content`） |
| `experiment` | lab 实验 registry（`engine/optibench/lab/registry.py`） |
| `preset` | practice registry 中 `kind="preset"` 的面包板 preset（`optibench/practice/breadboard.py`） |
| `practice` | practice registry 中 `kind="domain"` 的实践域（`optibench/practice/matching.py`） |
| `assessment` | quiz 索引中的测验 id（`modules/<module>/assessment/quiz.yaml`，`optibench/content/quiz.py`；阶段 3 引入） |

实践域与面包板 preset 通过 `PracticeActivity` 接口（`engine/optibench/practice/base.py`）注册，字段：`id`、`title`、`kind`、`entry`（前端定位信息，engine 视为不透明数据）、`available()`。学习层只依赖该接口，禁止 import matching/domains 内部模块（ADR-003 边界）。

## 4. 校验规则与错误处理

加载（loader）与建图（graph）两阶段校验，违规抛 `CurriculumError`（信息含文件名/节点 id）：

**加载期（schema）：**
1. 文件不存在、非法 YAML、顶层缺 `nodes` 列表：报错。
2. 节点缺必需字段（`id`/`kind`/`ref`/`title`）或字段类型错误：报错并指出 `nodes[i]` 位置。
3. `kind` 不在枚举内：报错并列出合法取值。
4. 节点 `id` 重复：报错。
5. `prerequisites` 引用本文件未定义的节点 id：报悬空先修错误。

**建图期（语义）：**
6. 节点 `ref` 无法按第 3 节解析：报悬空引用错误（含 kind 与 ref）。
7. 先修关系构成环：报环错误并列出环上节点（Kahn 算法检测）。

加载/建图失败时 API 不可用（启动即暴露），不做静默降级——路径定义是内容合同的一部分，错误必须显式修复。

## 5. API

`GET /api/v1/curriculum/graph`：

```json
{
  "nodes": [
    {
      "id": "double-slit",
      "kind": "experiment",
      "ref": "double-slit",
      "title": "双缝干涉实验",
      "module": "30-wave-optics",
      "prerequisites": ["single-slit-diffraction", "polarization-malus"],
      "status": "not_started"
    }
  ],
  "edges": [{ "from_id": "single-slit-diffraction", "to_id": "double-slit" }]
}
```

`status` 为学习者状态合并字段：阶段 2 起由 `learning_records`（见 `learning-records.md`）合并真实进度——default learner 存在 `completed` 或 `scored` 记录时为 `completed`，存在 `viewed` 记录时为 `viewed`（`completed` 优先），否则为 `not_started`。`edges[].from_id` 为先修节点，`to_id` 为依赖节点。

## 6. 前端路径视图

- 挂载：学习中心"学习路径"视图（`apps/desktop/src/lab/PathView.tsx`）。
- 展示：按 `module` 分层（10 → 50，practice 层居末），层内按 YAML 声明顺序线性排列；节点显示 kind 徽章与标题。
- 锁定：`computeLocks(nodes, completed)`——节点的全部直接先修都在完成集合中才解锁；锁定节点显示缺失先修标题。完成集合来自 graph 节点 `status === "completed"`（learning_records 合并结果）；`completed` 节点自身即使先修缺失也不显示锁定（状态以服务端合并为准），行尾显示绿色完成标记。
- 跳转（ADR-004 修订）：experiment/preset → 沙盘加载对应实验；concept → 若 `knowledgeLinks.json` 命中该 ref 则 `obsidian://` 跳转知识库笔记，未命中（内容合同教程，如 `cmos-fundamentals`）则回退教程视图；practice → 对应领域工作台 Tab（经 `appStore`）；assessment → 路径视图内嵌打开测验面板（`QuizPanel`）。

## 7. 先修关系的物理基线

实验节点的先修以实验代码中 `prerequisites` 声明为准（测试 `test_experiment_nodes_mirror_registry_prerequisites` 强制同步）。阶段 1 修正了两处物理不合理声明：

- `polarization-malus`：原声明依赖 `thin-lens`，马吕斯定律与薄透镜无物理依赖，修正为无先修。
- `snell-refraction`：原声明依赖 `thin-lens`，折射定律比薄透镜更基础，顺序颠倒，修正为无先修。

## 8. linked_concepts 挂账状态

内容合同 v1 第 7 节确立的旧 vault 路径映射方案在本阶段部分落地：概念 id 命名空间已生效，curriculum 图通过 concept 节点把实验与概念关联（如 `cmos-spectral-response ← cmos-fundamentals`）。但实验元数据 `linked_concepts` 中的旧 vault 路径（`10-concepts/*`、`50-learning/*`）**未**批量改写：目标概念文档（`modules/<module>/learning/`）大多尚不存在，改写会产生大量悬空引用。该挂账随"教程正文补写"（持续任务）逐批完成：每补齐一篇概念文档，即可把相关实验的旧路径替换为概念 id。
