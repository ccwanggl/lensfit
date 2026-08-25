# 应用壳导航规格（App Shell v1）

> 版本：v1
> 日期：2026-08-24
> 依据：`docs/development/plans/active/2026-08-learning-first-repositioning-plan.md` 阶段 4、`docs/development/product/roadmap.md`（2026-08-24 版）
> 实现：`apps/desktop/src/App.tsx`、`apps/desktop/src/stores/appStore.ts`、`apps/desktop/src/stores/labStore.ts`、`apps/desktop/src/components/SettingsPanel.tsx`

## 1. 定位

学习中心是默认首页与应用主壳；四个领域工作台收编为"实践场"入口；项目/器件库/游乐场为工具区。四领域工作台组件零改动，仅入口归位。

## 2. 导航分组

顶部导航分三组（`NAV_GROUPS`，组间分隔线 + 组标题，窄屏隐藏组标题）：

| 组 | 内容 | 说明 |
|---|---|---|
| 学习 | 学习中心 | 默认 Tab（`appStore.activeTab` 初值 `"learning"`）；内部子视图"学习路径 / 实验沙盘 / 教程"，默认子视图为学习路径（`labStore.learningView` 初值 `"path"`） |
| 实践场 | 工业视觉 / 摄影 / 显微镜 / 红外成像 | 原选型工作台，Tab id 不变；学习路径 practice 节点经 `appStore.setActiveTab` 跳转至此 |
| 工具 | 项目 / 器件库 / 游乐场 | 设置经右上角图标抽屉进入，不占 Tab |

## 3. "学习模式"开关决策

**决策：保留，重命名为"实践场学习辅助"，默认关闭不变。**

评审结论：该开关并非冗余——它有实际功能差异，控制四领域工作台内的学习辅助行为：

- `useParamHint`：仅在开启时返回参数提示；
- `KnowledgePanel`：开启时高亮学习链接并自动展开相关公式章节。

这些行为作用于实践场工作台，与学习中心（始终学习导向）互不重叠，因此开关保留但文案收窄：设置面板与头部徽章/横幅统一改称"实践场学习辅助"，明确其作用域为实践场四个工作台，避免与"学习优先"的产品定位产生语义冲突。默认值维持关闭（不改变四领域工作台既有默认渲染，回归无损）。

## 4. 验收标准

- 启动默认进入学习中心的学习路径视图（`appStore`/`labStore` 默认值，`src/stores/*.test.ts`）。
- 实践场四个工作台功能回归无损（组件零改动，Tab id 不变）。
- 路径视图 practice 节点跳转领域 Tab 行为不变（`PathView.test.tsx`）。
- `npm run build` 与前端全量测试通过。
