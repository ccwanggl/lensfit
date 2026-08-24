# OptiBench 研发文档

本目录记录 OptiBench 的产品规划、现行架构、工程决策、开发指南、审查结果和发布过程。通用光学知识与学习资料位于仓库顶层的 `modules/` 目录（按 10-foundations ~ 50-optical-design 五个模块组织）。

## 文档边界

- `docs/development/` 描述 OptiBench 当前如何设计、开发、测试和发布。
- `modules/` 保存不依赖当前代码实现的光学知识、公式、教程和领域资料。
- 当前实现与目标设计必须分开记录，旧计划应归档，不能继续作为现状说明。

## 研发文档导航

### 产品

- [竞品分析](development/product/competitor-analysis.md)
- [功能与路线图](development/product/roadmap.md)

### 架构

- [软件架构](development/architecture/software-architecture.md)
- [核心算法实现](development/architecture/core-algorithms.md)
- [数据库设计](development/architecture/database-design.md)
- [技术栈](development/architecture/tech-stack.md)

### 指南

- [跨平台开发环境](development/guides/cross-platform-setup.md)

### 审查

- [2026-06-15 仓库审查报告](development/reviews/2026-06-15-repository-review.md)

### 过程目录

- `development/decisions/`：架构决策记录，采用 ADR 编号。
- `development/specifications/`：已确认的功能和技术规格。
- `development/plans/active/`：正在执行的开发计划。
- `development/plans/archive/`：完成或停止的计划。
- `development/releases/`：版本发布说明和验证记录。

## 文档状态

研发文档应在开头标明适用版本、状态或日期。会随实现变化的文档需要在相关代码变更中同步更新。
