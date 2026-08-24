# 光学面包板后续工作计划

> 制定日期：2026-06-25  
> 前提：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 0-5 已全部完成。

> **状态注记（2026-08 更新）**：阶段 6（双缝衍射 breadboard preset）已完成，主计划阶段 0-6 全部勾完，双缝测试已通过（评审报告：`docs/development/reviews/2026-06-25-phase-6-double-slit-breadboard-preset.md`）。本文第 2 节“推荐路线：阶段 6”与第 5 节推荐顺序中的阶段 6 不再适用；当前待办是阶段 6.5（工程债务清理 + 前端测试，见第 4 节路线 C 的工程债务部分），之后按第 5 节进入阶段 7 用户试用。

## 1. 背景

原 active plan 在阶段 5 后注明“需要重新评审”。本文件在阶段 5 验收通过后，给出下一阶段的可选路线与推荐方案。

## 2. 推荐路线：阶段 6 — 第二个 breadboard preset

### 目标

在不动用通用自由画布、不引入数据库 migration 的前提下，验证“场景式 preset 比普通参数滑块更有教学价值”。

### 候选 preset

| 候选 | 复用后端实验 | 新增 spec_id | 复杂度 |
|---|---|---|---|
| **双缝衍射面包板**（推荐） | `engine/optibench/lab/experiments/double_slit.py` | `double-slit` | 低 |
| 薄透镜成像面包板 | `engine/optibench/lab/experiments/thin_lens.py` | `thin-lens` | 中（涉及物距/像距/焦距联动） |
| 光栅衍射面包板 | `engine/optibench/lab/experiments/grating.py` | `diffraction-grating` | 中 |

### 推荐：双缝衍射面包板

原因：

- 后端已有 `double_slit.py` 实验，可直接复用。
- 光学布局与单缝相同（激光 → 双缝 → 屏幕），只需把 `single-slit` 替换为 `double-slit`。
- 新增参数（双缝间距、缝宽、波长、屏距）都是单缝已有的教学维度，学习者容易迁移。

### 进入条件

- 阶段 5 验收通过。
- 决定采用哪个后端实验作为第二个 preset。

### 退出条件

- 新增 `double-slit-breadboard` preset 可在 `LearningHub` 中打开。
- 调大双缝间距，条纹间距变小。
- 调大屏距，条纹间距变大。
- 波长 preset 与重置按钮对第二个 preset 同样生效。
- `SceneGraph v1` 新增 `double-slit` spec_id，但不引入 ray-optics 类型名。
- 不引入数据库 migration。
- 新增测试覆盖双缝 preset 的 `buildScene` 与后端结果一致性。

### 涉及文件

- `engine/optibench/lab/workbench/scene.py`：扩展 `Component.spec_id` Literal。
- `engine/optibench/lab/workbench/equipment.py`：新增 `double-slit` 设备规格。
- `engine/optibench/lab/workbench/native_interpreter.py`：新增双缝参数映射。
- `engine/optibench/lab/workbench/solver.py`：根据 aperture spec_id 分发单缝/双缝。
- `apps/desktop/src/lab/workbenchTypes.ts`：新增 `double-slit-breadboard` preset。
- `apps/desktop/src/lab/LearningHub.tsx`：无改动或仅小幅调整（若新增通用化校验）。
- `engine/tests/test_workbench_scene.py` / `tests/test_api_workbench.py`：新增双缝场景测试。

### 验证命令

```powershell
cd "E:/OpticHackerSpace/optibench/engine"
python -m pytest tests/test_workbench_scene.py tests/test_api_workbench.py -q

cd "E:/OpticHackerSpace/optibench/apps/desktop"
npm run build
```

### 回滚条件

- 需要修改 `SceneGraph` 核心结构才能支持双缝。
- 双缝实验物理结果与现有 `double_slit.py` 不一致。
- 第二个 preset 让前端状态管理明显复杂化。

## 3. 备选路线 B：ray-optics 几何层 adapter

### 目标

让 `WorkbenchSolver` 能为几何光学场景生成光线追迹图，与 native 波动强度分层渲染。

### 进入条件

- 至少有一个 breadboard preset 稳定运行。
- ray-optics runner 合同测试在目标平台通过。
- 许可证 / NOTICE 策略明确。

### 退出条件

- `SceneGraph` 新增 `geometry_rays` observable（或 adapter 内部类型）。
- `WorkbenchSolver` 对几何 observable 调用 ray-optics adapter，对波动 observable 调用 native solver。
- 失败不影响现有 Lab 路径。
- 输出包含几何光线图 + 波动强度图，并明确标注分层。

### 风险

- 需要把 Node runtime 和 vendored ray-optics 打包进桌面发行版。
- `node-canvas` 可能成为 image 输出的平台依赖。
- 几何追迹与波动强度在物理上可能不一致，需要 UI 明确标注。

## 4. 备选路线 C：用户测试 + 工程债务清理

### 目标

在投入更多功能前，先用真实用户验证现有单缝 preset 的教学价值，并补齐工程债务。

### 任务清单

1. **用户测试**
   - 准备 2-3 个任务：观察单缝衍射、改变缝宽、改变屏距。
   - 记录用户是否理解“锁定布局 + 参数”与“波动强度曲线”的关系。
   - 根据反馈决定是否做第二个 preset 或 ray-optics。

2. **工程债务**
   - 前端：为 `BreadboardPresetHeader`、`sceneDrafts`、`validatePresetParams` 增加测试（Vitest / React Testing Library）。
   - 前端：抽取 SVG 示意图常量。
   - 后端：把真实 sidecar 冒烟测试纳入 pytest/CI，避免一次性脚本。
   - 文档：把 ADR-002、research doc、active plan 中的重叠内容进一步拆分。

## 5. 推荐顺序

1. **阶段 6：双缝衍射 breadboard preset**（短期，1-2 天）。
2. **阶段 6.5：工程债务清理 + 前端测试**（与阶段 6 并行或紧随其后）。
3. **阶段 7：用户试用阶段 5-6 的两个 preset**，收集反馈。
4. **阶段 8：根据反馈决定是否实现 ray-optics 几何层 adapter 或通用画布**。

## 6. 决策点

下一步需要决定：

- 是否按推荐路线进入阶段 6（双缝衍射 preset）？
- 是否先走路线 C（用户测试 + 工程债务）？
- 是否跳过第二个 preset，直接进入路线 B（ray-optics adapter）？

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/reviews/2026-06-25-phase-5-implementation-review.md`
- `docs/development/reviews/2026-06-25-phase-5-deep-review.md`
