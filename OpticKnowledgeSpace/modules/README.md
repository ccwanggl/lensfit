---
id: lensfit.modules
title: LensFit 微专业入口
type: map
domains: [general]
status: draft
aliases: [微专业入口, 模块导航, 学习起点]
---

# LensFit 光学基础与成像系统入门

> **微专业名称**：光学基础与成像系统入门
> 
> **版本**：v4.0（模块环形重构）
> **完成标准**：完成全部五个模块；提交至少一个综合项目报告；完成每模块自测；最终能独立阅读一篇基础成像/光谱/设计论文并复述其系统结构、关键指标与限制条件。

---

## 五模块环形结构

```mermaid
flowchart LR
    A[[modules/10-foundations/README\|模块甲｜桥接]] --> B[[modules/20-geometric-optics/README\|模块乙｜几何光学]]
    B --> C[[modules/30-wave-optics/README\|模块丙｜波动光学]]
    B --> D[[modules/40-spectroscopy/README\|模块丁｜光谱学]]
    C --> E[[modules/50-optical-design/README\|模块戊｜光学设计]]
    D --> E
    E --> F[[modules/90-projects/README\|综合项目]]
```

---

## 模块速览

| 模块 | 核心能力 | 预计时长 | 先修 | 状态 |
|------|---------|---------|------|------|
| **[[modules/10-foundations/README\|模块甲｜桥接]]** | 建立"会用级"数学与物理直觉，掌握基本术语 | 15–25h | 无 | 🟡 可用 |
| **[[modules/20-geometric-optics/README\|模块乙｜几何光学]]** | 能用光线模型解释成像，掌握典型系统结构 | 30–45h | 模块甲 | 🟡 可用 |
| **[[modules/30-wave-optics/README\|模块丙｜波动光学]]** | 理解干涉、衍射、相干、PSF/OTF/MTF、傅里叶 | 35–55h | 模块乙 | 🟡 可用 |
| **[[modules/40-spectroscopy/README\|模块丁｜光谱学]]** | 掌握光谱原理、仪器结构和分辨率限制 | 25–40h | 模块乙 | 🟡 可用 |
| **[[modules/50-optical-design/README\|模块戊｜光学设计]]** | 建立"规格—结构—分析—优化—容差"闭环 | 40–60h | 模块丙+丁 | 🟡 可用 |
| **[[modules/90-projects/README\|综合项目]]** | 用真实项目串联三个以上模块知识 | 20–40h | 模块乙+丙/丁 | 🔴 待建 |

---

## 三种学习节奏

| 节奏 | 周投入 | 总时长 | 适合人群 |
|------|--------|--------|---------|
| **速成** | 12–18h/周 | 3个月 | 数理基础好、快速建立整体视野 |
| **常规（推荐）** | 6–10h/周 | **6个月** | **在职工程师，性价比最高** |
| **慢速** | 3–5h/周 | 12个月 | 教材+MOOC+实验全做扎实 |

**快速选择**：
- 完全没光学基础 → **模块甲 → 模块乙 → 模块戊（综合项目）**
- 有基础，想补系统 → **模块乙 → 模块丙 → 模块戊**
- 工作需要光谱 → **模块甲 → 模块乙 → 模块丁 → 模块戊**
- 已有基础，查概念 → **直接用下方概念/公式/设备索引**

---

## 三本账体系

每个模块维护三本个人知识账：

1. **📘 概念账**：专记术语、单位、近似条件和适用边界
   - 每模块至少积累 10-25 个核心概念
   - 用 `[[10-concepts/xxx|概念名]]` 链接到原子笔记

2. **📗 计算账**：记录所有常用公式与典型题型
   - 每模块至少掌握 5-15 个核心公式
   - 用 `[[20-formulas/xxx|公式名]]` 链接到公式笔记

3. **📙 项目账**：持续沉淀仿真脚本、实验照片、误差分析与阶段总结
   - 每模块至少完成 2-4 个实践项目
   - 用 `.compute/scripts/` 或 `cmos_sensor_lab/` 交互式验证

---

## 快速索引

### 概念索引
- [[10-concepts/README|全部概念目录]]
- [[modules/10-foundations/concepts|模块甲概念]]
- [[modules/20-geometric-optics/concepts|模块乙概念]]
- [[modules/30-wave-optics/concepts|模块丙概念]]
- [[modules/40-spectroscopy/concepts|模块丁概念]]
- [[modules/50-optical-design/concepts|模块戊概念]]

### 公式索引
- [[20-formulas/README|全部公式目录]]
- [[modules/10-foundations/formulas|模块甲公式]]
- [[modules/20-geometric-optics/formulas|模块乙公式]]
- [[modules/30-wave-optics/formulas|模块丙公式]]
- [[modules/40-spectroscopy/formulas|模块丁公式]]
- [[modules/50-optical-design/formulas|模块戊公式]]

### 设备索引
- [[40-devices/README|全部设备目录]]

### 领域索引
- [[30-domains/README|全部领域目录]]

---

## 软件与工具栈

**基础层**：Jupyter + Python + NumPy/Matplotlib，用于作图、单位换算、简单几何和频域计算。

**光学层**：
- **RayOptics** — 几何与近轴分析（与模块乙/戊对接）
- **POPPY** — Fraunhofer/Fresnel 衍射与 PSF 仿真（与模块丙对接）
- **CMOS Sensor Lab** — 交互式传感器参数实验（与模块乙对接）
  - 运行：`streamlit run .compute/cmos_sensor_lab/app.py`

---

## 与旧版学习路线的关系

本微专业是旧版「学习路线.md」的**超集和重构**：
- 旧版：16 章线性阅读，约 40-60 小时，快速入门导向
- 新版：五模块环形，约 145-225 小时，微专业深度导向
- **旧版内容全部保留**，通过模块 README 重新索引，不破坏任何链接
- 旧版 `学习路线.md` 仍可作为「快速浏览版」使用

---

> **开始你的光学微专业之旅**：[[modules/10-foundations/README|从模块甲｜桥接开始 →]]
