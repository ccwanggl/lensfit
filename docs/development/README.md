# 开发文档导航

## 产品

- [竞品分析](product/competitor-analysis.md)
- [功能与路线图](product/roadmap.md)

## 架构

- [软件架构](architecture/software-architecture.md)
- [核心算法实现](architecture/core-algorithms.md)
- [数据库设计](architecture/database-design.md)
- [技术栈](architecture/tech-stack.md)
- [光学实验室架构](architecture/optics-lab/README.md)

## 架构决策

- [架构决策记录](decisions/README.md)

## 规格说明

- [规格说明索引](specifications/README.md)
- [光学实验室规格](specifications/lab/README.md)

## 执行计划

- [进行中的计划](plans/active/README.md)
- [已归档计划](plans/archive/README.md)

## 开发指南

- [跨平台开发环境](guides/cross-platform-setup.md)

## 审查记录

- [2026-06-25 光学面包板阶段 0 评审报告](reviews/2026-06-25-phase-0-optical-breadboard-baseline.md)
- [2026-06-15 仓库审查报告](reviews/2026-06-15-repository-review.md)
- [2026-06-15 架构文档与代码一致性检查](reviews/2026-06-15-architecture-code-consistency.md)

## 维护约定

- `architecture/` 只描述已经落地或明确标为目标状态的设计。
- `decisions/` 使用 `ADR-NNNN-title.md` 命名，并记录状态、背景、决策和后果。
- `specifications/` 存放 API、Schema、实验合同和验收标准。
- `plans/active/` 中的计划完成后移入 `plans/archive/`。
- `reviews/` 按日期命名，保留复核批注，不覆盖原始发现。
- `releases/` 记录构建环境、迁移版本、测试结果和发布产物。
