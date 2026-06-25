# 光学面包板阶段 5 就绪评审

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 5：有限编辑与扩展评审  
> 评审方式：对照阶段 0-4 交付物与阶段 5 进入/退出条件进行桌面评审

## 1. 结论

**阶段 5 尚未实现，但进入条件已基本具备。**

阶段 0-4 已全部完成并通过验收。当前最大的未满足进入条件是“用户测试证明 preset 比普通滑块实验更有理解价值”，这需要产品/UX 决策，无法仅通过代码实现自动验证。

## 2. 阶段 5 目标回顾

> 在前四个 checkpoint 全部通过后，评估是否开放少量场景编辑能力。

可考虑能力：

- 只允许移动屏幕。
- 只允许切换激光波长 preset。
- 只允许编辑白名单参数。
- 一键重置默认布局。
- `labStore.sceneDrafts[presetId]` 本地草稿，不入数据库。

## 3. 进入条件检查

| 进入条件 | 状态 | 说明 |
|---|---|---|
| Checkpoint 0-4 全部通过 | ✅ | 阶段 0-4 已提交并通过评审 |
| 用户测试证明 preset 比普通滑块实验更有理解价值 | ⚠️ 未验证 | 需要实际用户反馈或 A/B 观察；代码层面已具备 preset 能力 |

## 4. 退出条件预评估

| 退出条件 | 当前是否可达成 | 备注 |
|---|---|---|
| 刷新后草稿可恢复 | 可实现 | 使用 `localStorage` 或 `labStore.sceneDrafts` 本地保存 |
| 重置能回到教学默认布局 | 可实现 | preset 元数据已包含默认参数，可一键重置 |
| 非法移动有明确提示 | 可实现 | `SceneGraph` 校验器可复用，前端可展示错误 |
| 序列化 SceneGraph 不包含第三方类型 | 可达成 | 阶段 1/4 已确保；需新增测试防止回归 |
| 不引入数据库 migration | 可达成 | 本地草稿即可，无需持久化到后端数据库 |

## 5. 当前架构是否支撑阶段 5

| 能力 | 当前状态 | 需要改动 |
|---|---|---|
| `SceneGraph` 参数驱动 | ✅ 已支持 | 无 |
| 参数滑块与 live params | ✅ 已支持 | 无 |
| 本地草稿存储 | ❌ 未实现 | 扩展 `labStore` 的 `sceneDrafts` |
| 一键重置 | ❌ 未实现 | 在 `BreadboardPresetRunner` 或 `LearningHub` 增加重置按钮 |
| 非法移动提示 | ❌ 未实现 | 增加对组件坐标/旋转的实时校验与错误展示 |
| 只允许移动屏幕 | ❌ 未实现 | 增加受限交互控件，不开放通用拖拽画布 |

## 6. 推荐的最小可行范围

如果决定进入阶段 5，建议优先实现以下**最小编辑能力**：

1. **屏幕位置滑块**：在现有参数面板中增加 `screen_x_mm` 滑块，范围限制在合理区间（如 200 mm ~ 3000 mm）。
2. **波长 preset 切换**：在参数面板中提供几个固定波长按钮（红/绿/蓝）。
3. **重置按钮**：在 `BreadboardPresetRunner` 标题栏增加“重置为默认布局”。
4. **本地草稿**：`labStore.sceneDrafts[presetId]` 保存当前参数，刷新后恢复；不进入数据库。
5. **非法状态提示**：当 `screen_x_mm <= slit_x_mm` 时，前端直接禁用运行并提示“屏幕必须在单缝之后”。

**明确不做**：通用自由画布、任意组件连接、Undo/Redo、保存/分享、数据库 migration。

## 7. 风险

| 风险 | 影响 | 缓解 |
|---|---|---|
| 增加编辑后，参数与可视化不同步 | 中 | 保持参数驱动模式；所有编辑通过 `labStore` 的 `paramDrafts` / `sceneDrafts` 统一回流 |
| 用户构造不可求解拓扑 | 低 | 只允许移动单个组件和切换白名单参数，限制编辑范围 |
| 草稿与后端 API 不一致 | 低 | 草稿只保存参数，运行前仍通过 `buildScene(params)` 生成 `SceneGraph` |
| 需要 Undo/Redo 才能解释交互 | 低 | 范围限定为一键重置 + 参数滑块，无需历史栈 |

## 8. 建议

1. **先完成用户价值验证**：在实现阶段 5 代码前，建议让至少 1-2 位目标用户试用阶段 3 的 preset，确认“锁定布局 + 参数滑块”是否足够直观。
2. **若验证通过，按最小可行范围实现**：优先做屏幕位置滑块、波长 preset、重置按钮、本地草稿。
3. **每新增一个编辑能力，都补充一个回归测试**：确保 `SceneGraph` 序列化后仍不含 ray-optics 类型名，且不触发数据库 migration。

## 9. 进入阶段 5 的决策点

阶段 5 不是自动进入的 checkpoint，而是一个**产品决策**。建议在以下两种路径中选择：

- **路径 A：跳过阶段 5，进入阶段 6+（如果有）或结束面包板 MVP**：如果当前 preset 已满足教学目标。
- **路径 B：实现最小有限编辑**：如果用户反馈表明需要更强的空间感知（如移动屏幕改变光路）。

## 10. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/reviews/2026-06-25-phase-4-ray-optics-readonly-probe.md`
- `apps/desktop/src/lab/workbenchTypes.ts`
- `apps/desktop/src/lab/LearningHub.tsx`
- `apps/desktop/src/stores/labStore.ts`
