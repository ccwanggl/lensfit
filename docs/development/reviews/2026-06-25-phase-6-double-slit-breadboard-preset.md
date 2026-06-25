# 光学面包板阶段 6 实施评审报告

> 评审日期：2026-06-25
> 评审范围：在 SceneGraph v1 / Workbench API 基础上新增 `double-slit-breadboard` preset
> 评审方式：代码走查、前后端测试、构建验证、与验收条件对照

## 1. 结论

**阶段 6 验收通过。**

在保持 `SceneGraph v1` 和 `WorkbenchSolver` 不变的前提下，通过新增 `double-slit` 设备规格、双缝参数映射函数、前端 `double-slit-breadboard` preset，以及适配的面包板示意图，实现了第二个锁定布局场景。新增测试验证了条纹间距与缝间距、屏距的物理关系，前端生产构建通过。

## 2. 实现概览

新增文件：无（全部为既有文件扩展）。

修改文件：

```text
engine/lensfit/lab/workbench/scene.py
engine/lensfit/lab/workbench/equipment.py
engine/lensfit/lab/workbench/native_interpreter.py
engine/lensfit/lab/workbench/solver.py
engine/tests/test_workbench_scene.py
engine/tests/test_api_workbench.py
apps/desktop/src/lab/workbenchTypes.ts
apps/desktop/src/lab/LearningHub.tsx
docs/development/plans/active/2026-06-optical-breadboard-development-plan.md
docs/development/reviews/2026-06-25-phase-6-double-slit-breadboard-preset.md
```

## 3. 逐项检查

### 3.1 退出条件

| 验收要求 | 实现 | 状态 |
|---|---|---|
| `double-slit-breadboard` preset 可在 LearningHub 运行 | `BREADBOARD_PRESETS` 新增 preset；`WorkbenchSolver` 按 aperture spec_id 分发到 `double-slit` 实验 | ✅ |
| 调大双缝间距条纹间距变小 | `test_workbench_double_slit_separation_decreases_fringe_spacing` | ✅ |
| 调大屏距条纹间距变大 | `test_workbench_double_slit_distance_increases_fringe_spacing`（近似 2 倍） | ✅ |
| 新增测试通过 | 后端 `158 passed` | ✅ |
| 前端构建通过 | `npm run build` 通过 | ✅ |

### 3.2 功能行为

| 能力 | 实现位置 | 状态 |
|---|---|---|
| 双缝设备规格 | `equipment.py` 新增 `double-slit`，默认 `slit_width_um=20`、`slit_separation_um=100` | ✅ |
| SceneGraph 解析双缝 | `scene.py` 扩展 `spec_id` Literal | ✅ |
| 求解器按 aperture 分发 | `solver.py`：`single-slit` → `single-slit-diffraction`；`double-slit` → `double-slit` | ✅ |
| 双缝参数映射 | `native_interpreter.py`：`fraunhofer_double_slit_params` | ✅ |
| 远场条件警告 | 双缝仍按缝宽计算 `L >> a^2 / λ` 给出夫琅禾费警告 | ✅ |
| 前端 preset 参数 | `wavelength_nm`、`slit_width_um`、`slit_separation_um`、`screen_x_mm` | ✅ |
| 前端校验 | `validatePresetParams` 校验 `screen_x_mm > 100`、缝间距 > 缝宽 | ✅ |
| 面包板示意图适配双缝 | `BreadboardPresetHeader` 根据 presetId 绘制单缝/双缝并切换标签 | ✅ |

### 3.3 构建与测试

| 检查项 | 命令 | 结果 |
|---|---|---|
| 后端全量回归 | `cd engine && python -m pytest -q` | **158 passed, 4 warnings** |
| 前端生产构建 | `cd apps/desktop && npm run build` | **通过** |

### 3.4 架构边界

- `SceneGraph v1` 仅扩展了 `spec_id` 枚举，未引入 ray-optics 类型名。
- `WorkbenchSolver` 保持单一入口；分发逻辑集中在 solver 层，未泄露到 SceneGraph。
- 本地草稿仍使用 `sceneDrafts`，未引入数据库 migration。
- 双缝 preset 复用了单缝 preset 的波长 preset 按钮、屏幕位置滑块和面包板示意图机制。

## 4. 发现与建议

### 4.1 已确认的设计选择

1. **Aperture-driven solver dispatch**

   `fraunhofer_intensity` observable 不区分单缝/双缝，由 aperture 组件的 `spec_id` 决定调用哪个后端实验。这样新增第三个 aperture 类型时，只需扩展 `equipment.py`、参数映射和 solver 分发即可。

2. **复用 preset 编辑框架**

   双缝 preset 没有引入新的 UI 机制，而是复用阶段 5 建立的 `sceneDrafts`、`validatePresetParams`、`BreadboardPresetHeader`。新增参数（缝宽、缝间距）直接走现有的 `ParameterControl`。

3. **示意图自适应**

   `BreadboardPresetHeader` 根据 `presetId` 绘制单缝或双缝，并切换标签文字，避免双缝 preset 显示“单缝”造成误解。

### 4.2 建议改进（非阶段 6 阻塞项）

1. **远场警告可更严格**

   当前双缝的夫琅禾费警告基于缝宽 `a`。由于双缝干涉条纹的远场条件还与缝间距 `d` 有关（`L >> d^2 / λ`），未来可考虑对 `d` 也做远场检查，或至少在教育提示中说明。

2. **前端参数非法边界**

   `validatePresetParams` 在缝宽/缝间距非有限时未返回错误。由于 `ParameterControl` 和 `initialParams` 已保证数值存在，当前风险低；但未来若支持清空输入，可补充 `Number.isFinite` 校验。

3. **通用 aperture 示意图**

   `BreadboardPresetHeader` 目前只处理单缝/双缝两种情况。若未来增加光栅、圆孔等 aperture，需要把示意图渲染改为基于 `apertureSpecId` 而不是硬编码 `presetId`。

## 5. 阶段 6 退出条件对照

| 退出条件 | 状态 |
|---|---|
| `double-slit-breadboard` preset 可在 LearningHub 运行 | ✅ |
| 调大双缝间距条纹间距变小 | ✅ |
| 调大屏距条纹间距变大 | ✅ |
| 新增测试通过 | ✅ |
| 前端构建通过 | ✅ |
| 不引入数据库 migration | ✅ |
| 不引入通用拖拽画布 | ✅ |

## 6. 后续建议

阶段 6 完成后，光学面包板已具备单缝、双缝两个 preset，满足“至少两个 preset 证明场景式交互价值”的最低门槛。建议：

1. 提交阶段 6 改动（已得用户确认后执行 `git commit`）。
2. 若继续扩展，优先评估：
   - 将 `BreadboardPresetHeader` 重构为按 `apertureSpecId` 渲染，支持更多 aperture 类型。
   - 接入 ray-optics adapter 实现几何光线与波动强度的分层渲染。
   - 引入用户测试，验证双缝面包板对干涉/衍射概念理解的帮助。

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `engine/lensfit/lab/workbench/equipment.py`
- `engine/lensfit/lab/workbench/native_interpreter.py`
- `engine/lensfit/lab/workbench/solver.py`
- `engine/tests/test_api_workbench.py`
- `apps/desktop/src/lab/workbenchTypes.ts`
- `apps/desktop/src/lab/LearningHub.tsx`
