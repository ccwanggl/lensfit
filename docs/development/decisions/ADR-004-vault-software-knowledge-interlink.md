# ADR-004：知识库—软件知识互联（Vault-Software Knowledge Interlink）

**状态**：接受
**日期**：2026-08-25
**作者**：OptiBench 架构团队
**范围**：界定 OptiBench 与 OpticKnowledgeSpace（Obsidian 知识库）的协同模型——软件不承载正文，深度学习内容回到知识库阅读；两侧通过"双链导航"互联，仅做知识级链接，不做数据同步。同时修订 `content-contract.md` §7 的旧路径债务清偿机制。

## 1. 背景

Self-Study Lab 原始设计即以 obsidian:// 深链把实验与知识库概念笔记关联（`KnowledgeSidebar.tsx`），但接口建立在**文件路径硬编码**之上。v4.0 知识库重组（目录英译中、编号前缀）使全部深链静默失效；随后仓库内 vault 副本删除，外部独立知识库继续演化。

ADR-003 学习优先转型后，`modules/` 内容合同 v1 与课程图落地，但 `modules/*/learning/` 正文近乎空置，"教程正文补写"成为最大成本项。经评审确认：**在桌面应用内重建一套阅读体验是错误分工**——软件的独特价值是可运行实验与实践场，深度理论阅读应发生在具备反链、图谱与原生渲染的知识库环境中。

## 2. 决策

1. **软件不承载正文。** 深度学习内容的唯一阅读场所是 Obsidian 知识库；软件是实践场（实验/沙盘/选型/进度），不是内容阅读器。
2. **双链导航，非双向更新。** 软件概念芯片 → `obsidian://` 跳转知识库笔记；知识库笔记「关联实验」章节 → 实验 id 指回软件。两个方向都是知识导航：无正文复制、无自动同步、无冲突解决。
3. **slug 为跨仓库主键。** 知识库 frontmatter `id` 去命名空间前缀后的部分（`concept.X` / `formula.Y` → `X` / `Y`）与实验元数据、课程图共用同一命名空间。概念与公式各自成表（同名 slug 如 `nyquist-frequency` 合法并存）。
4. **解析层为生成物。** `apps/desktop/src/lab/knowledgeLinks.json`（slug → {path, title}）由 `scripts/generate_knowledge_links.py` 扫描知识库 frontmatter 自动产出——元数据级同步；知识库重组目录后重跑脚本即修复全部链接。
5. **`modules/*/learning` 角色调整。** frontmatter 层（id/prerequisites/linked_experiments/status）保留为课程图数据源；正文降格为可选的一句话摘要或指针。ADR-003 中"教程正文补写工作量大"的成本项就此消解。
6. **产品假设：用户环境必有 Obsidian 与 OpticKnowledgeSpace vault。** 不做缺失探测、不做降级 UI。
7. **公式纳入解析层。** `linked_formulas` 与 `linked_concepts` 同机制处理（修订原 §7 "公式暂不处理"表述）。

## 3. 主要后果

### 正面

- 零内容副本 → 零漂移、零同步校验成本。
- 阅读体验直接获得 Obsidian 全部能力（LaTeX、SVG 嵌入、反链、图谱）。
- 债务清偿不再被"正文是否写完"阻塞：旧路径一次性替换为裸 slug 即完成。
- 删除整个"格式适配层"（双链转换、附件拷贝、数学定界符）的计划复杂度。

### 负面 / 代价

- 运行时依赖用户本机存在同名 vault；未安装 Obsidian 的终端用户无法使用知识点跳转（已接受的产品假设）。
- `knowledgeLinks.json` 是新增的必须再生成的产物，需随知识库重组维护。
- ADR-003 阶段 0 建设的 TutorialView 教程渲染能力利用率下降（保留服务 frontmatter 层与未来摘要正文）。

### 替代方案（已否决）

- **A. 导出管道**：把知识库正文转换为合同教程写入 `modules/`。漂移与格式适配成本高，违背"内容只写在权威页"的知识库约定。
- **B. 引擎运行时直读知识库**：重新引入 v4.0 刚移除的耦合，Obsidian 语法不可移植，违反稳定合同原则。
- **C. 双向自动同步**：冲突解决复杂度是上一轮耦合腐烂的直接死因。
- **D. 任一侧目录改名对齐**：破坏知识库双链与编号体系；slug 主键已消除必要性。

## 4. 架构边界

- 引擎运行时不得读取知识库路径；`obsidian://` URL 的构造仅存在于前端表现层。
- 对知识库的一切读取保持只读；向知识库回流信息只能走人工流程（如投放快照到收件箱）。
- 实验元数据的 `linked_concepts` / `linked_formulas` 只允许裸 slug 或 §7 报告中挂账的未解析字面量，禁止再引入新路径形态。

## 5. 与既有文档的关系

- 修订 `docs/development/specifications/lab/content-contract.md` §7（债务清偿机制改由本决策接管）。
- 修订 `docs/development/specifications/lab/experiment-catalog.md` 头部注记。
- 不废弃 ADR-003：课程图、PracticeActivity、学习者状态等决策全部有效；仅"教程正文"供给方式变更。
- 未解析条目清单见 `scripts/knowledge_links_unresolved.md`。

## 6. 参考

- `docs/development/decisions/ADR-003-learning-first-pivot.md`
- `docs/development/specifications/lab/content-contract.md`
- `docs/development/specifications/lab/experiment-catalog.md`
- `docs/development/architecture/optics-lab/self-study-lab-architecture.md`（状态注记）
- `scripts/generate_knowledge_links.py`、`scripts/knowledge_links_unresolved.md`
