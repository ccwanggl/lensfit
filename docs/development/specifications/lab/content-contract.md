# 内容合同 v1（Content Contract）

> 版本：v1
> 日期：2026-08-24
> 依据：`docs/development/plans/active/2026-08-learning-first-repositioning-plan.md` 阶段 0、`docs/development/decisions/ADR-003-learning-first-pivot.md` 第 4 节
> 地位：稳定合同。engine 内容管道与前端教程视图都依赖本合同；任何变更必须走版本化（见第 6 节）。

## 1. 范围与定位

`modules/` 目录下的 markdown 文档分为两类：

- **概念教程（concept）**：本合同的约束对象，位于 `modules/<module>/learning/*.md`。
- **非教程文档**：模块根 `README.md`、`projects/`、`assessment/` 下的文档。本合同不为其建索引（见第 4 节），其 frontmatter 不受本合同约束。例外：`assessment/quiz.yaml` 是阶段 3 引入的测验定义文件，由独立的 quiz loader 扫描，格式见 `assessment-quizzes.md`。

概念教程由 frontmatter（YAML）+ markdown 正文组成。engine 启动时扫描构建只读索引，前端通过内容 API 读取并渲染。无数据库表。

## 2. Frontmatter Schema

每篇概念教程必须在文件头部包含 YAML frontmatter（`---` 分隔），字段如下：

| 字段 | 类型 | 必需 | 说明 |
|---|---|---|---|
| `id` | string | 是 | 概念 id，全局唯一。小写字母/数字/连字符，如 `cmos-fundamentals` |
| `title` | string | 是 | 概念标题，用于列表展示 |
| `module` | string | 是 | 所属模块目录名，如 `20-geometric-optics`；必须与文件所在模块目录一致 |
| `difficulty` | enum | 是 | `foundation` / `intermediate` / `advanced` |
| `prerequisites` | string[] | 是 | 先修概念 id 列表，可为空列表 `[]` |
| `linked_experiments` | string[] | 是 | 关联实验 id 列表（lab registry 中的实验 id），可为空列表 `[]` |
| `status` | enum | 是 | `draft` / `published` |

正文为 frontmatter 之后的 markdown 全文。

允许出现合同之外的附加字段（如 `type`、`source`、`author`），校验器保留但不解释这些字段，供后续合同版本使用。

### 示例

```markdown
---
id: cmos-fundamentals
title: CMOS Image Sensor 基础
module: 20-geometric-optics
difficulty: intermediate
prerequisites: []
linked_experiments:
  - sensor-coverage
status: draft
---

## 前言

正文……
```

## 3. 校验规则

engine 在构建索引时对每个候选文件执行校验，违规即产生明确报错（包含文件路径与字段名）：

1. frontmatter 缺失、未闭合或不是合法 YAML：报错。
2. 缺少必需字段：报错并列出缺失字段名。
3. `difficulty` / `status` 取值不在枚举内：报错并列出合法取值。
4. `id`、`title`、`module` 不是非空字符串：报错。
5. `prerequisites` / `linked_experiments` 不是字符串列表：报错。
6. `module` 与文件实际所在模块目录名不一致：报错。
7. `id` 全局重复（两个文件声明同一 `id`）：报错，指出冲突的两个文件。

注意：`prerequisites` 与 `linked_experiments` 引用的目标是否存在，在阶段 0 **不做**悬空引用检查（概念内容尚未补齐，强制检查会阻塞管道落地）；悬空引用检测随阶段 1 的 curriculum 图构建引入。

## 4. 索引规则

- 扫描范围：`modules/**/*.md`。
- 候选文件：路径形如 `modules/<module>/learning/<name>.md` 的文件。即只有位于模块 `learning/` 子目录下的 markdown 才会被当作概念教程校验并收录。
- 其余文件（模块根 `README.md`、`projects/`、`assessment/` 下的文档）一律跳过，不参与校验、不建索引。这保证 `projects/README.md`、`assessment/README.md` 这类带有自身 frontmatter 的非教程文档不会误触发合同校验。
- 索引内容：`id → (元数据, 正文文件路径)`，只读，进程内缓存，无数据库表。
- 非法文件的处理：默认从索引中剔除并记录错误（错误通过 API 暴露，便于内容作者排查）；严格模式（`strict=True`，用于测试与 CI）遇到第一个非法文件即抛出 `ContractError`。

## 5. 内容 API

- `GET /api/v1/content/concepts`：返回索引列表。每项含全部元数据（不含正文）；响应同时携带索引构建期收集的错误列表 `errors`。
- `GET /api/v1/content/concepts/{id}`：返回单个概念的元数据 + markdown 正文（`body`）。未收录的 `id` 返回 404。

## 6. 版本化策略

- 本合同为 v1。新增字段、改变字段语义、收紧校验均构成新版本（v2），须：
  1. 更新本文档并标注版本号与变更说明；
  2. 同步更新 `engine/optibench/content/contract.py` 的校验器；
  3. 保证旧版本合法内容在新版本下仍然合法（只增不删，新字段必须有默认值或允许缺省）。
- engine 与前端都只依赖本合同定义字段；附加字段不得被任何一端依赖。

## 7. 旧 vault 路径映射（linked_concepts 债务）

> **2026-08-25 修订**：本节清偿机制由 [ADR-004](../../decisions/ADR-004-vault-software-knowledge-interlink.md) 接管。以下为现行机制；原"逐篇正文补齐后重映射到合同 id"的方案已被取代（历史方案见文末附注）。

**现行机制（ADR-004）**：实验元数据中的 `linked_concepts` / `linked_formulas` 统一使用**裸 slug**（知识库 frontmatter `id` 去命名空间前缀，如 `concept.diffraction-limit` → `diffraction-limit`），概念与公式各自成表，同名 slug 合法并存。前端经生成的映射表解析：

- 映射表：`apps/desktop/src/lab/knowledgeLinks.json`（`{concepts: {slug: {path,title}}, formulas: {...}}`）
- 生成器：`scripts/generate_knowledge_links.py`（只读扫描知识库 `10-概念/`、`20-公式/` 的 frontmatter）
- 渲染：`apps/desktop/src/lab/KnowledgeSidebar.tsx` 按 slug 查表构造 `obsidian://open?vault=OpticKnowledgeSpace&file=<path>` 链接
- 未在知识库中找到对应笔记的字面量保留原值并登记于 `scripts/knowledge_links_unresolved.md`（2026-08-25 快照：8 个唯一值，含 `20-formulas/snell-law`、`20-formulas/single-slit-minima` 等）

**历史方案（已被取代）**：原 §7 规定 `10-concepts/<slug>` 待对应概念教程补齐后重映射为本合同 id、公式暂由 `linked_formulas` 原样保留且不属于本合同范围——该方案的"逐批清偿依赖正文补写"与"公式除外"两点均不再成立，详见 ADR-004 §2/§5。
