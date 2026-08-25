# 知识链接未解析清单

> 生成日期：2026-08-25
> 背景：ADR-004 债务清偿。实验元数据中的旧 vault 路径已批量替换为裸 slug；以下条目在 OpticKnowledgeSpace 中找不到对应笔记，按约定**保留原值、不做猜测**。

## 未解析条目（8 个唯一值，9 处出现）

| 旧值 | 所在文件 | 说明 |
|---|---|---|
| `10-concepts/diffraction-grating` | `engine/optibench/lab/experiments/grating.py` | 库中有 `grating-coupler`（光栅耦合器），非同一概念；缺「衍射光栅」笔记 |
| `10-concepts/同轴照明` | `engine/optibench/lab/experiments/illumination_geometry.py` | 知识库无同轴照明概念笔记 |
| `20-formulas/depth-of-field` | `engine/optibench/lab/experiments/depth_of_field.py` | `20-公式/` 无景深公式笔记 |
| `20-formulas/hyperfocal-distance` | `engine/optibench/lab/experiments/depth_of_field.py` | 无超焦距公式笔记 |
| `20-formulas/longitudinal-chromatic-aberration` | `engine/optibench/lab/experiments/chromatic_aberration.py` | 无纵向色差公式笔记 |
| `20-formulas/malus-law` | `engine/optibench/lab/experiments/polarization_malus.py` | 无马吕斯定律公式笔记 |
| `20-formulas/single-slit-minima` | `engine/optibench/lab/experiments/single_slit_diffraction.py`、`apps/desktop/src/lab/workbenchTypes.ts`（×2） | 无单缝极小公式笔记 |
| `20-formulas/snell-law` | `engine/optibench/lab/experiments/snell_refraction.py` | 无斯涅尔定律公式笔记 |

## 处理方式

对应笔记在知识库补齐后：在 `20-公式/`（或 `10-概念/`）新建笔记并按规范填写 frontmatter `id`（如 `formula.snell-law`），重跑 `scripts/generate_knowledge_links.py`，再把上述字面量替换为裸 slug 即可恢复链接。

## 另行事项

- `aberration_spot.py` 引用的 `50-learning/06-aberrations`、`50-learning/11-optical-design-basics` 为课程章节引用（第三类前缀），不在本次 slug 化范围，维持原值；待章节级链接机制明确后统一处理。
