# 光学面包板阶段 5 实施评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 5：有限编辑与扩展评审  
> 评审方式：代码走查、前后端测试、构建验证、与 active plan 退出条件对照

## 1. 结论

**阶段 5 验收通过。**

采用了参数驱动的有限编辑方案：在现有参数面板基础上，为 `single-slit-breadboard` preset 增加了波长 preset 按钮、屏幕位置滑块、面包板示意图、本地草稿持久化、非法状态提示和一键重置。未引入通用拖拽画布、数据库 migration 或 Undo/Redo。

## 2. 实现概览

新增文件：无（全部为既有文件扩展）。

修改文件：

```text
apps/desktop/src/stores/labStore.ts
apps/desktop/src/lab/workbenchTypes.ts
apps/desktop/src/lab/LearningHub.tsx
engine/tests/test_workbench_scene.py
docs/development/plans/active/2026-06-optical-breadboard-development-plan.md
docs/development/reviews/2026-06-25-phase-5-implementation-review.md
docs/development/README.md
```

## 3. 逐项检查

### 3.1 退出条件

| active plan 要求 | 实现 | 状态 |
|---|---|---|
| 刷新后草稿可恢复 | `labStore.sceneDrafts` 通过 Zustand `persist` 写入 `localStorage` | ✅ |
| 重置能回到教学默认布局 | “重置默认布局”调用 `resetSceneDraft` 并恢复参数默认值 | ✅ |
| 非法移动有明确提示 | `validatePresetParams` 校验 `screen_x_mm > 100`，非法时禁用运行并显示红色提示 | ✅ |
| 序列化 SceneGraph 不包含第三方类型 | 新增 `test_serialized_scenegraph_has_no_ray_optics_types` | ✅ |
| 不引入数据库 migration | 草稿仅存 `localStorage`，无 Alembic 改动 | ✅ |

### 3.2 功能行为

| 能力 | 实现位置 | 状态 |
|---|---|---|
| 只允许移动屏幕 | `screen_x_mm` 参数滑块 + 面包板 SVG 示意图 | ✅ |
| 只允许切换激光波长 preset | `BreadboardPresetHeader` 红/绿/蓝按钮 | ✅ |
| 只允许编辑白名单参数 | 仍使用 preset 元数据中的 `parameters` 列表 | ✅ |
| 一键重置默认布局 | `ParameterPanel` 底部按钮，preset 显示“重置默认布局” | ✅ |
| `labStore.sceneDrafts[presetId]` 本地草稿 | `labStore` 新增字段与持久化 | ✅ |

### 3.3 构建与测试

| 检查项 | 命令 | 结果 |
|---|---|---|
| 后端指定测试 | `pytest tests/test_workbench_scene.py tests/test_api_workbench.py tests/test_ray_optics_contract.py -q` | **31 passed, 1 warning** |
| 后端全量回归 | `pytest -q` | **151 passed, 4 warnings** |
| 前端生产构建 | `npm run build` | **通过** |

### 3.4 架构边界

- `SceneGraph v1` 未修改，未引入 ray-optics 类型名。
- `WorkbenchSolver` / native interpreter 未改动；`buildScene` 仍通过组件坐标推导 `screen_distance_m`。
- 本地草稿仅用于 breadboard preset，普通实验保持原有 `paramDrafts`。
- 未引入数据库 schema 变化。

## 4. 发现与建议

### 4.1 已确认的设计选择

1. **参数驱动优于可视化拖动**

   阶段 5 没有引入通用拖拽画布。屏幕位置通过滑块控制，并辅以 SVG 示意图实时反馈。这降低了实现复杂度，同时保留了空间感知。

2. **`screen_distance_m` → `screen_x_mm`**

   将屏距参数改为屏幕绝对位置，使学习者更直观地理解“移动屏幕”。后端仍然从 `SceneGraph` 组件坐标推导实际距离，实验结果不变。

3. **`sceneDrafts` 与 `paramDrafts` 分离**

   preset 使用 `sceneDrafts`，普通实验使用 `paramDrafts`。这种隔离让 future 阶段可以独立演进面包板草稿格式，而不影响现有实验。

### 4.2 建议改进（非阶段 5 阻塞项）

1. **用户价值验证**

   active plan 的进入条件之一是“用户测试证明 preset 比普通滑块实验更有理解价值”。本阶段尚未进行真实用户测试，建议在后续迭代中补充 1-2 位目标用户试用记录。

2. **示意图可交互性**

   当前 SVG 仅作视觉反馈。若后续用户反馈需要更强的空间操控，可让示意图上的屏幕图标可拖动，并反向写回 `screen_x_mm`。

3. **非法状态校验扩展**

   当前仅校验 `screen_x_mm > 100`。未来若增加更多可移动组件，应扩展 `validatePresetParams` 为通用校验表。

4. **草稿版本迁移**

   若未来 `SceneGraph v2` 改变参数结构，需要考虑 `sceneDrafts` 的版本迁移或丢弃策略。

## 5. 阶段 5 退出条件对照

| 退出条件 | 状态 |
|---|---|
| 刷新后草稿可恢复 | ✅ |
| 重置能回到教学默认布局 | ✅ |
| 非法移动有明确提示 | ✅ |
| 序列化 SceneGraph 不包含第三方类型 | ✅ |
| 不引入数据库 migration | ✅ |
| 不引入通用拖拽画布 | ✅ |
| 不引入 Undo/Redo / 保存 / 分享 | ✅ |

## 6. 后续建议

阶段 5 完成后，光学面包板 MVP 的五个 checkpoint 已全部通过。建议：

1. 提交阶段 5 改动（已取得用户确认后再执行 `git commit`）。
2. 若后续要继续扩展，优先评估：
   - 接入 ray-optics adapter 实现几何光线与波动强度的分层渲染。
   - 增加更多 breadboard preset（如双缝、薄透镜成像）。
   - 引入用户测试，验证面包板对教学理解的价值。

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/reviews/2026-06-25-phase-5-readiness-review.md`
- `apps/desktop/src/stores/labStore.ts`
- `apps/desktop/src/lab/workbenchTypes.ts`
- `apps/desktop/src/lab/LearningHub.tsx`
- `engine/tests/test_workbench_scene.py`
