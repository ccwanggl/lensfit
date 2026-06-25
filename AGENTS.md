# AGENTS.md

## 通用约定

- 始终使用简体中文回复。
- 先读后写，理解现有代码、文档和计划后再修改。
- 如果用户没有明确要求，不要主动创建分支、提交或推送。
- 涉及删除、批量移动、数据库结构变更、生产 API、全局依赖安装、`git commit`、`git push`、`git reset --hard` 等高风险操作前，必须先获得明确确认。

## 文档执行优先级

后续 agent 执行开发任务时，必须按以下顺序查阅文档：

1. `docs/development/plans/active/*.md`：唯一的执行计划来源。
2. `docs/development/decisions/ADR-*.md`：架构决策和不可违反边界。
3. `docs/development/specifications/**/*.md`：API、Schema、数据合同和验收标准。
4. `docs/development/architecture/**/*.md`：模块职责、依赖方向和目标架构。
5. `docs/development/product/*.md`：产品定位、优先级和范围判断。
6. `docs/development/reviews/*.md`：风险证据来源，不可直接当作执行计划。
7. `docs/development/research/*.md`：调研参考，不可直接决定实现。

如果 review、research 或 ADR 中的建议尚未进入 `plans/active/`，agent 不应直接实施；应先创建或更新 active plan。

## 文档语言

- `docs/development/` 下新增或重写的项目文档默认使用简体中文。
- 代码标识符、API 路径、类名、文件路径、外部项目名保持英文。
- 术语首次出现时可以中英并列，例如“场景图（SceneGraph）”。

## 光学面包板执行规则

光学面包板相关开发必须以以下文档为执行入口：

```text
docs/development/plans/active/2026-06-optical-breadboard-development-plan.md
```

当前阶段不得直接实现以下能力，除非 active plan 明确进入对应 checkpoint：

- 完整拖拽画布。
- SceneGraph 持久化。
- `ray-optics` 用户路径。
- 3D / VR / CAD。
- 设备数据库或厂商设备 catalog。
- long-lived Node sidecar。
- 通用任意光路求解。

第一阶段优先级：

1. 修复发布链与现有 Lab 基线。
2. 建立 `SceneGraph v1` 无状态合同。
3. 实现 `single-slit-diffraction` 的 native preset workbench。
4. 再做 `ray-optics` 只读探针，不接入用户路径。

## 工程原则

- KISS：优先最小可验证切片，避免一次性做通用平台。
- YAGNI：没有进入 active plan checkpoint 的能力不实现。
- DRY：复用现有 Lab、API、测试和前端运行壳，不重复建设实验系统。
- SOLID：保持 LensFit `SceneGraph` 与第三方引擎 adapter 解耦，不让 `ray-optics` JSON 泄漏到产品域模型。
