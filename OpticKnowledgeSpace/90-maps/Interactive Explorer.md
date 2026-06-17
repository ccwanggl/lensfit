---
id: map.interactive-explorer
title: 交互式探索器
type: map
status: reviewed
aliases:
  - Interactive Explorer
  - 知识图谱浏览器
---

# 交互式探索器

除了静态图解，本库还提供两种交互式探索方式，适合喜欢“拖拽 + 点击查看”的视觉学习者。

---

## 1. 浏览器版知识图谱

`attachments/visuals/knowledge-explorer.html` 是一个自包含的 HTML 文件，使用 D3.js 绘制整个知识库的关系网络。

### 使用方法

1. 用浏览器直接打开 `OpticKnowledgeSpace/attachments/visuals/knowledge-explorer.html`。
2. 在左侧搜索框输入笔记标题，快速定位节点。
3. 点击任意节点：
   - 查看该笔记的标题、所属文件夹、状态
   - 查看入链（哪些笔记引用它）和出链（它引用了哪些笔记）
   - 高亮其邻居节点和连接
4. 拖拽节点、滚轮缩放、右下角按钮重置视图或隐藏标签。

> 注意：该 HTML 使用 CDN 加载 D3.js，首次打开需要联网。如果需要在离线环境使用，可下载 `d3.v7.min.js` 放到同一目录并修改 `<script src>`。

---

## 2. Obsidian Canvas 学习路径

`90-maps/Learning Path.canvas` 是一个 Obsidian 原生画布文件，把 16 章学习路径以卡片时间线形式呈现。

### 使用方法

1. 在 Obsidian 中打开 `90-maps/Learning Path.canvas`。
2. 拖动、缩放画布，按阶段浏览章节卡片。
3. 点击任意章节卡片即可跳转到对应学习笔记。
4. 你可以继续添加自己的笔记卡片、高亮卡片或连线。

---

## 什么时候用哪种工具？

| 场景 | 推荐工具 |
|---|---|
| 想纵览全局关系、找孤立笔记 | 浏览器版知识图谱 |
| 想按章节顺序规划学习 | Obsidian Canvas 学习路径 |
| 只想快速查看某张图解 | [[90-maps/Visual Index\|可视化索引]] |
| 想系统阅读完整教程 | [[90-maps/Learning Path\|从零到深入学习路径]] |

---

## 如何更新这些交互资产

运行仓库根目录下的脚本即可重新生成：

```bash
python scripts/generate_interactive_assets.py
```

它会同时更新：

- `OpticKnowledgeSpace/attachments/visuals/knowledge-explorer.html`
- `OpticKnowledgeSpace/90-maps/Learning Path.canvas`
