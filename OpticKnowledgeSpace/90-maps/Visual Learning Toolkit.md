---
id: map.visual-learning-toolkit
title: 视觉学习工具箱
type: map
status: reviewed
aliases:
  - Visual Learning Toolkit
  - 学习方法
---

# 视觉学习工具箱

本库默认按「原子笔记 + 学习章节」组织，但如果你更偏向视觉学习，可以搭配下面的方法、图解和 Obsidian 插件，把线性阅读变成空间探索。

---

## 推荐学习流程

```
看大图 → 读概念 → 看图解 → 动手画 → 做沙盒练习 → 回看图谱
```

1. **看大图**：先打开 [[90-maps/Learning Path|学习路径]]，了解 16 章的先后顺序与分组。
2. **读概念**：进入具体概念页（如 [[10-concepts/focal-length|焦距]]），先浏览图解，再读文字。
3. **看图解**：每个关键概念都配有 SVG 图解，见 [[90-maps/Visual Index|可视化索引]]。
4. **动手画/拖拽**：拿一张纸或 Obsidian Canvas，把薄透镜、像圈、景深等图自己画一遍；也可以打开 [[90-maps/Interactive Explorer|交互式探索器]] 拖拽章节卡片。
5. **做沙盒练习**：每章末尾的「LensFit 沙盒 🧪」提供可计算的实例。
6. **回看图谱**：学完一章后，回到 [[90-maps/Knowledge Map|知识地图]] 或 [[90-maps/Knowledge Architecture|知识库架构]]，确认新知识与旧知识的连接。

---

## 推荐 Obsidian 插件

这些插件能增强视觉学习体验，均可在 Obsidian 的「社区插件」中搜索安装。

| 插件 | 作用 | 为什么适合视觉学习者 |
|---|---|---|
| **Excalidraw** | 手绘风格白板 | 把 SVG 图解复制到白板上，自己标注、推导、画变体 |
| **Canvas** | Obsidian 原生画布 | 将章节、概念、公式、设备卡片拖拽成自己的知识地图 |
| **Dataview** | 查询笔记元数据 | 按 `status`、`domain`、`type` 动态生成学习进度看板 |
| **Templater** | 笔记模板增强 | 一键创建带标准 frontmatter 的概念/公式/设备笔记 |
| **Tasks** | 任务管理 | 把学习计划、待补充 stub、复习任务可视化 |
| **Kanban** | 看板 | 把学习阶段排成看板，直观跟踪进度 |
| **Advanced Tables** | 表格增强 | 整理参数对比、教材索引等表格 |
| **Meta Bind** | 交互式 frontmatter | 用按钮/输入框快速修改笔记元数据 |
| **Buttons** | 按钮组件 | 在笔记中插入「生成闪卡」「打开 Canvas」等快捷按钮 |
| **Charts** | 数据图表 | 把 frontmatter 数据渲染成柱状图/折线图 |
| **Spaced Repetition** | 闪卡复习 | 把公式、定义做成卡片，按遗忘曲线复习 |
| **Style Settings** | 主题微调 | 调整字体、行宽、颜色，优化阅读体验 |
| **Copilot** | AI 辅助（可选） | 需要自行配置 API key，可用于概念解释和润色 |

### 安装建议

1. 打开 Obsidian → 设置 → 社区插件 → 关闭安全模式。
2. 浏览社区插件，安装上表中的插件。
3. 在 `.obsidian/plugins/` 下安装后，**不要提交这些插件目录**（已在 `.gitignore` 中排除），尤其不要把 `copilot/data.json` 中的 API key 提交到仓库。

### 已复刻的 Obsidian 配置

本库 `.obsidian/` 已同步以下配置（来自另一个 EE 知识库）：

- `app.json`：关闭删除确认、关闭 Readable line length，启用 `wide-reading-view` 片段。
- `appearance.json`：启用 `wide-reading-view` CSS 片段。
- `core-plugins.json`：开启/关闭的核心插件集合。
- `community-plugins.json`：社区插件清单。
- `snippets/wide-reading-view.css`：宽阅读视图样式，让编辑/预览区域更宽。

> 如需完全一致的插件行为，还需在 Obsidian 中手动安装社区插件；配置文件中只包含插件清单和开关，不包含插件代码或个人 API key。

---

## 推荐的 Canvas 用法

Obsidian Canvas 是最适合视觉学习者的原生工具：

- **创建章节概览**：把 16 章学习笔记作为卡片，按阶段摆成时间线。
- **概念推导墙**：把薄透镜公式、视角公式、像圈覆盖等卡片用箭头连起来。
- **选型决策树**：复制 `attachments/visuals/domain-selection-map.svg` 到 Canvas，把每个分支链接到对应领域笔记。
- **错题/误区收集**：把常见误区写成卡片，贴在对应概念旁边。

> 提示：`.canvas` 文件属于个人工作区，已加入 `.gitignore`，你可以自由创建而不会影响仓库。

---

## 图解使用清单

- 每学完一章，检查是否看过 [[90-maps/Visual Index|可视化索引]] 中对应的图解。
- 对复杂的图，建议右键「在新标签页打开图片」，放大查看坐标轴和标注。
- 把常用图（如镜头选型清单、传感器雷达图）打印出来，放在手边备查。

---

## 延伸阅读

- [[90-maps/Learning Path|从零到深入学习路径]]
- [[90-maps/Visual Index|可视化索引]]
- [[90-maps/Knowledge Architecture|知识库架构]]
- [[50-learning/09-exercises|第9章：综合练习]]
