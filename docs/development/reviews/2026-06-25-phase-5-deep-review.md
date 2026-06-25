# 光学面包板阶段 5 深度审查报告

> 审查日期：2026-06-25  
> 审查对象：阶段 5 实现（有限编辑与扩展评审）  
> 审查方式：代码重读、边界条件推演、布局问题复现与修复、前后端测试、生产构建

## 1. 审查结论

**阶段 5 实现基本正确，已发现并修复一处布局缺陷。**

审查后，所有退出条件仍满足，测试与构建均通过。剩余问题均为低风险改进项，不影响当前 MVP。

## 2. 已修复问题

### 2.1 参数面板与面包板示意图的垂直布局冲突

**问题描述**

`BreadboardPresetHeader` 被插入到参数面板容器内，但容器未设置为 `flex-col`，且 `ParameterPanel` 使用 `h-full`。这导致：

- 头部组件占用高度后，参数面板仍尝试占据父容器 100% 高度。
- 在较小视口下，参数控件和“重置”按钮可能被截断或溢出容器。

**修复内容**

- 左侧参数容器和移动端左侧面板容器均改为 `flex flex-col`。
- `ParameterPanel` 改为 `flex min-h-0 flex-1 flex-col`，让头部自动占据所需高度，参数面板填充剩余空间。

**验证**

- `npm run build` 通过。
- 未引入新的 TypeScript 错误。

## 3. 代码正确性检查

### 3.1 状态管理

| 检查项 | 结果 | 说明 |
|---|---|---|
| `sceneDrafts` 仅用于 preset | ✅ | `LearningHub` 通过 `isPreset` 选择 `sceneDrafts` 或 `paramDrafts` |
| 草稿持久化 | ✅ | `labStore` 的 `partialize` 包含 `sceneDrafts` |
| 重置清除草稿 | ✅ | `handleReset` 对 preset 调用 `resetSceneDraft(activeExperimentId)` |
| 参数变化同步到草稿 | ✅ | `handleParamChange` 对 preset 调用 `setSceneDraft` |
| 草稿恢复后运行正确 | ✅ | `initialParams` 从 `drafts` 计算，并通过 effect 回流到 `liveParams` |

### 3.2 校验逻辑

| 检查项 | 结果 | 说明 |
|---|---|---|
| 初始状态校验 | ✅ | `useEffect` 在 `initialParams` 变化时调用 `validatePresetParams` |
| 参数变化校验 | ✅ | `handleParamChange` 的 debounce 回调中校验 |
| 非法状态禁用运行 | ✅ | `useQuery` 的 `enabled` 要求 `sceneError === null` |
| 错误提示明确 | ✅ | 左侧面板显示“屏幕必须位于单缝之后” |
| 校验函数范围 | ⚠️ | 当前仅覆盖 `single-slit-breadboard`；未来新增 preset 需扩展 |

### 3.3 参数语义

| 检查项 | 结果 | 说明 |
|---|---|---|
| `screen_x_mm` 范围 | ✅ | min 200 mm, max 3000 mm, step 10 mm |
| 默认布局 | ✅ | 默认 1100 mm，对应单缝后 1000 mm |
| 后端距离推导 | ✅ | `native_interpreter.screen_distance_m()` 仍从组件坐标推导 |
| 波长 presets | ✅ | 红 650 nm / 绿 550 nm / 蓝 450 nm |

### 3.4 架构隔离

| 检查项 | 结果 | 说明 |
|---|---|---|
| `SceneGraph` 未修改 | ✅ | 仍保持 v1 语义 |
| 无 ray-optics 类型泄漏 | ✅ | 新增测试覆盖序列化 JSON 扫描 |
| 无数据库 migration | ✅ | 草稿仅保存到 `localStorage` |
| native workbench 未受影响 | ✅ | 普通实验路径仍使用 `paramDrafts` |

## 4. 边界条件推演

| 场景 | 预期行为 | 实际代码行为 |
|---|---|---|
| 用户将 `screen_x_mm` 设为 100（与单缝重合） | 显示错误，不运行 | `validatePresetParams` 返回错误，`useQuery` 禁用 |
| 用户将 `screen_x_mm` 设为 50（单缝之前） | 显示错误，不运行 | 同上 |
| 用户输入非数字 | 参数控件返回 NaN，校验可能放行 | `ParameterControl` 对 float 使用 `parseFloat`，非数字返回 `NaN`；`Number(NaN) <= 100` 为 false，因此校验放行，但后端 422 |
| 用户直接点击波长 preset | 波长更新并触发重新计算 | `onChange("wavelength_nm", value)` 走现有参数变更流程 |
| 刷新页面 | 恢复上次 draft | `sceneDrafts` 通过 Zustand persist 写入 `localStorage` |
| 重置布局 | 恢复默认值并清除 draft | `resetSceneDraft` + `setLiveParams(defaults)` |
| 从 preset 切换到普通实验 | 普通实验使用 `paramDrafts` | `isPreset` 变化，`drafts` 重新计算 |

**发现**：非数字输入场景下，`ParameterControl` 的 number input 会显示空值，但 `parseFloat(""|"abc")` 返回 `NaN`，`validatePresetParams` 把 `NaN` 视为有效（因为 `NaN <= 100` 为 false），随后 `buildScene` 会生成 `NaN` 坐标，导致后端 `screen_distance_m()` 报错并返回 422。

**处理结果**：已在 `validatePresetParams` 中增加 `Number.isFinite(screen_x_mm)` 检查，拒绝 `NaN` 或 `Infinity` 进入 `SceneGraph`。修复后重新运行构建与测试，均通过。

## 5. 测试覆盖

| 测试文件 | 新增/相关测试 | 结果 |
|---|---|---|
| `engine/tests/test_workbench_scene.py` | `test_serialized_scenegraph_has_no_ray_optics_types` | ✅ 通过 |
| `engine/tests/test_workbench_scene.py` | `test_unknown_spec_id_fails`（SingleRay 被拒） | ✅ 通过 |
| `engine/tests/test_api_workbench.py` | workbench run / slit width / distance / warning | ✅ 通过 |
| `engine/tests/test_ray_optics_contract.py` | ray-optics 合同测试 | ✅ 通过 |

**不足**：前端尚未为 `BreadboardPresetHeader`、`sceneDrafts`、`validatePresetParams` 增加单元/集成测试。建议后续引入 Vitest 或 React Testing Library 覆盖：

- 点击波长 preset 按钮更新 `wavelength_nm`。
- 非法 `screen_x_mm` 禁用运行并显示错误。
- 重置按钮清除 `sceneDrafts`。

## 6. 性能与可维护性

| 检查项 | 结果 | 说明 |
|---|---|---|
| 无多余重渲染风险 | ⚠️ | `BreadboardPresetHeader` 每次 `params` 变化都会重新渲染 SVG；数据量小，可接受 |
| 依赖数组完整 | ✅ | `useMemo`、`useEffect` 依赖包含所需状态 |
| 类型安全 | ✅ | TypeScript 构建通过 |
| 魔法数字 | ⚠️ | SVG 示意图中的 `100`、`200`、`3000`、`220` 等数字未命名常量；建议抽取为 `SLIT_X_MM`、`SCREEN_X_MIN`、`SCREEN_X_MAX` 等 |

## 7. 建议改进（非阻塞）

1. **增强 `validatePresetParams` 的健壮性（已处理）**

   已增加 `Number.isFinite` 检查，防止 `NaN` 或 `Infinity` 进入 `SceneGraph`。

2. **抽取 SVG 示意图常量**

   将示意图中的位置、范围常量提到 `workbenchTypes.ts` 或单独常量文件，便于后续 preset 复用。

3. **增加前端测试**

   为 `BreadboardPresetHeader` 和 `LearningHub` 的 preset 分支增加轻量测试。

4. **用户价值验证**

   阶段 5 进入条件原本要求“用户测试证明 preset 比普通滑块实验更有理解价值”。当前尚未进行真实用户测试，建议在后续迭代中补充。

## 8. 最终验证

| 检查项 | 命令 | 结果 |
|---|---|---|
| 后端指定测试 | `pytest tests/test_workbench_scene.py tests/test_api_workbench.py tests/test_ray_optics_contract.py -q` | **31 passed, 1 warning** |
| 后端全量回归 | `pytest -q` | **151 passed, 4 warnings** |
| 前端生产构建 | `npm run build` | **通过** |

## 9. 参考

- `docs/development/reviews/2026-06-25-phase-5-implementation-review.md`
- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `apps/desktop/src/lab/LearningHub.tsx`
- `apps/desktop/src/lab/workbenchTypes.ts`
- `apps/desktop/src/stores/labStore.ts`
- `engine/tests/test_workbench_scene.py`
