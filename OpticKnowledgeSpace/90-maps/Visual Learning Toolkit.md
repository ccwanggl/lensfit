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
| **Graph Analysis** | 增强图谱分析 | 在 Obsidian 图谱中查看中心概念、孤岛笔记、连接强度 |
| **Tag Wrangler** | 管理标签 | 给每个概念打上 `#visual` `#formula` `#device` 等标签，便于过滤 |
| **Spaced Repetition** | 闪卡复习 | 把公式、定义做成卡片，按遗忘曲线复习 |
| **Breadcrumbs** | 层级导航 | 在笔记顶部显示「上级 → 同级 → 下级」路径，强化结构感 |

### 安装建议

1. 打开 Obsidian → 设置 → 社区插件 → 关闭安全模式。
2. 浏览社区插件，安装上表中的插件。
3. 在 `.obsidian/plugins/` 下安装后，**不要提交这些插件目录**（已在 `.gitignore` 中排除）。

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
