---
id: map.obsidian-setup
title: Obsidian 配置说明
type: map
status: reviewed
aliases:
  - Obsidian Setup
  - 配置说明
---

# Obsidian 配置说明

本知识库默认使用一套与 `E:\EEDevSpace\EEKnowledgeSpace` 一致的 Obsidian 配置，存放在 `OpticKnowledgeSpace/.obsidian/` 下。

> 注意：`.obsidian/` 目录已加入 `.gitignore`，因此配置不会随仓库提交，仅在本地生效。下面的说明用于记录复刻内容，方便你在新设备上手动恢复。

---

## 已同步的配置文件

| 文件 | 作用 |
|---|---|
| `app.json` | 应用行为：关闭删除确认、关闭 Readable line length、启用 `wide-reading-view` CSS 片段 |
| `appearance.json` | 外观：启用 `wide-reading-view` CSS 片段 |
| `core-plugins.json` | 核心插件开关 |
| `community-plugins.json` | 社区插件清单 |
| `types.json` | 属性类型定义（主要为 Tasks 插件字段） |
| `snippets/wide-reading-view.css` | 宽阅读视图 CSS，提升编辑/预览区宽度 |

未同步（个人/可再生成）的文件：

- `workspace.json`：工作区布局
- `plugins/*/data.json`：插件个人设置与 API key
- 所有插件代码目录（`plugins/`）

---

## 社区插件清单

打开 Obsidian → 设置 → 社区插件，安装以下插件即可完全复刻：

- `copilot`
- `obsidian-excalidraw-plugin`
- `obsidian-dataview`
- `advanced-tables-obsidian`
- `templater-obsidian`
- `obsidian-spaced-repetition`
- `obsidian-meta-bind-plugin`
- `buttons`
- `obsidian-charts`
- `obsidian-tasks-plugin`
- `obsidian-kanban`
- `obsidian-style-settings`

---

## 推荐启用方式

1. 用 Obsidian 打开 `OpticKnowledgeSpace/` 文件夹。
2. 进入「设置 → 外观」，开启 CSS 片段 `wide-reading-view`。
3. 进入「设置 → 社区插件」，关闭安全模式并安装上述插件。
4. 进入「设置 → 核心插件」，按需要启用/关闭功能（参考 `core-plugins.json`）。
5. 如需使用 Copilot，请自行在插件设置中填入 API key；**切勿把 key 提交到 Git**。

---

## 与本库配合的用法

- **Excalidraw**：把 [[90-maps/004-Visual Index|可视化索引]] 中的 SVG 拖入白板，自己画变体。
- **Dataview**：在 [[90-maps/003-Visual Learning Toolkit|视觉学习工具箱]] 中生成按 `status`、`type`、`domain` 过滤的学习进度表。
- **Canvas**：打开 [[90-maps/005-Interactive Explorer|交互式探索器]] 提到的 `Learning Path.canvas` 拖拽章节卡片。
- **Tasks / Kanban**：把「待补充概念」「待复习公式」做成任务或看板。
