# 光学面包板阶段 3 评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 3：前端单缝面包板 Preset  
> 评审方式：代码走查、TypeScript 构建、后端回归测试、与 active plan UI 原则对照

## 1. 结论

**阶段 3 验收通过。**

`single-slit-breadboard` preset 已集成到现有 `LearningHub`，不启用独立 `BreadboardPage`。左侧参数控件、中间锁定布局 + 强度曲线、右侧知识栏均符合 active plan 的 UI 原则。前端生产构建通过，后端测试无回归。

## 2. 实现概览

新增文件：

```text
apps/desktop/src/lab/workbenchTypes.ts
apps/desktop/src/lab/BreadboardPresetRunner.tsx
```

修改文件：

```text
apps/desktop/src/utils/api.ts
apps/desktop/src/lab/ExperimentCatalog.tsx
apps/desktop/src/lab/LearningHub.tsx
```

## 3. 逐项检查

### 3.1 UI 原则

| active plan 要求 | 实现 | 状态 |
|---|---|---|
| 左侧继续使用参数控件 | `LearningHub` 对 preset 仍渲染 `ParameterPanel` | ✅ |
| 中间显示锁定布局：激光、单缝、屏幕、强度曲线 | `BreadboardPresetRunner` 显示布局说明 + 后端 SVG | ✅ |
| 右侧继续使用知识侧栏 | `KnowledgeSidebar` 接收 preset 元数据 | ✅ |
| 第一版不做拖拽，不做自由放置 | 仅通过参数滑块控制场景 | ✅ |
| 几何布局层和波动强度层必须明确标注 | `BreadboardPresetRunner` 中明确说明“几何层为示意图；下方曲线为波动光学计算” | ✅ |

### 3.2 功能行为

| 退出条件 | 验证方式 | 状态 |
|---|---|---|
| 用户能打开 `single-slit-breadboard` preset | 目录中新增 preset 卡片，点击后 active id 切换 | ✅ |
| 调大缝宽，中央亮纹变窄 | 由后端 `/workbench/run` 计算保证（阶段 2 已测试） | ✅ |
| 调大屏距，条纹间距变大 | 由后端 `/workbench/run` 计算保证（阶段 2 已测试） | ✅ |
| 参数变化有 loading/error 状态 | `isFetching` 控制透明度，`runError` 显示错误信息 | ✅ |
| 错误信息不暴露 ray-optics 或内部 adapter 字段 | 当前为 native 路径，错误来自 `SceneGraph` 校验或实验运行 | ✅ |
| 移动端不出现主要内容遮挡 | `LearningHub` 响应式布局未改动，preset 沿用相同网格 | ✅ |

### 3.3 构建与测试

| 检查项 | 命令 | 结果 |
|---|---|---|
| 前端生产构建 | `npm run build` | **通过** |
| 后端全量回归 | `pytest -q` | **137 passed, 4 warnings** |

### 3.4 架构边界

- `LearningHub` 通过 `isBreadboardPreset(activeExperimentId)` 区分 preset 与普通实验。
- preset 元数据（`BREADBOARD_PRESETS`）在内存中定义，不访问后端 `/lab/experiments`。
- preset 参数变化仍复用 `ParameterControl` 和 `labStore` 的 `paramDrafts`。
- `/lab/workbench/run` 返回的 `LabRunResult` 与普通实验 API 完全一致，前端无需额外适配。

## 4. 发现与建议

### 4.1 已确认的设计选择

1. **preset 与普通实验共享 `LabExperiment` 类型**

   `BreadboardPreset` 扩展了 `LabExperiment`，因此 `ExperimentCatalog`、`ParameterPanel`、`KnowledgeSidebar` 都能直接消费，无需为 preset 单独写渲染逻辑。

2. **场景构造器位于前端**

   `buildScene(params)` 在前端根据参数生成 `SceneGraph v1`。这使得 UI 能实时响应参数变化，同时保持后端 `/workbench/run` 无状态。

3. **未修改 `ParameterControl.tsx` 和 `labStore.ts`**

   active plan 列出了这两个文件为“修改”，但实际实现中它们的通用性足够，无需改动。这是一个正面的信号，说明现有组件已经具备良好的复用性。

### 4.2 建议改进（非阶段 3 阻塞项）

1. **添加前端单元/集成测试**

   当前阶段 3 没有新增前端测试。建议后续为 `workbenchTypes.ts` 的 `buildScene` 和 `BreadboardPresetRunner` 增加轻量测试（例如使用 Vitest），确保场景构造正确。

2. **统一错误信息本地化**

   后端返回的英文 `ValueError` 会直接展示在 `LearningHub` 的错误区域。未来可以增加一层错误文案映射。

3. **场景可视化增强**

   当前“锁定布局”是文字说明 + 后端 SVG。后续可以考虑在前端绘制一个独立的几何示意图（激光、单缝、屏幕位置），与强度曲线并列，进一步强化分层概念。

## 5. 阶段 3 退出条件对照

| 退出条件 | 状态 |
|---|---|
| 用户能打开 `single-slit-breadboard` preset | ✅ |
| 调大缝宽，中央亮纹变窄 | ✅ |
| 调大屏距，条纹间距变大 | ✅ |
| 参数变化有 loading/error 状态 | ✅ |
| 错误信息不暴露 ray-optics 或内部 adapter 字段 | ✅ |
| 移动端不出现主要内容遮挡 | ✅ |
| 不形成 `LearningHub` 与旧 `LabPage` 双入口 | ✅ |
| 几何阴影和衍射强度已分层标注 | ✅ |

## 6. 进入阶段 4 的前提

阶段 3 已满足进入阶段 4 的全部条件。建议在阶段 4 开始前：

1. 提交阶段 3 改动（已取得用户确认后再执行 `git commit`）。
2. 阶段 4 目标是在测试或后台验证 `ray-optics` Node runner 的最低可行集，不接入用户路径，不影响 native workbench。

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `apps/desktop/src/lab/workbenchTypes.ts`
- `apps/desktop/src/lab/BreadboardPresetRunner.tsx`
- `apps/desktop/src/lab/LearningHub.tsx`
- `apps/desktop/src/lab/ExperimentCatalog.tsx`
- `apps/desktop/src/utils/api.ts`
