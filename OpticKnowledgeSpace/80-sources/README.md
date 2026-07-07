---
id: map.sources
title: 来源
type: map
status: maintained
---

# 来源

记录标准、论文、书籍、厂商资料和外部文章。来源笔记用于追踪出处，不替代领域知识笔记。

## 当前状态

来源层仍是知识库中最薄的一层。现有概念、公式和学习章节已经能支撑学习，但若要作为工程决策依据，需要逐步补齐来源。

## 核心入口

- [[000-Textbook Index|教材索引]]：优秀教材对比、适用阶段和主题入口。
- [[001-Textbook Reference Matrix|教材页码索引矩阵]]：知识点到教材章节/页码的映射。

## 已建立来源笔记

- [[002-hecht-optics-5e|Eugene Hecht, *Optics*, 5th ed.]] — 入门到进阶通用光学
- [[003-saleh-teich-fundamentals-photonics-3e|Saleh & Teich, *Fundamentals of Photonics*, 3rd ed.]] — 工程光子学
- [[004-goodman-introduction-fourier-optics-4e|Goodman, *Introduction to Fourier Optics*, 4th ed.]] — 傅里叶光学与像质
- [[005-smith-modern-optical-engineering-4e|Smith, *Modern Optical Engineering*, 4th ed.]] — 光学系统工程
- [[006-wyszecki-stiles-color-science-2e|Wyszecki & Stiles, *Color Science*, 2nd ed.]] — 色度学与颜色测量
- [[007-gonzalez-woods-digital-image-processing-4e|Gonzalez & Woods, *Digital Image Processing*, 4th ed.]] — 采样、边缘检测与数字图像处理
- [[008-driggers-infrared-electro-optical-systems-3e|Driggers et al., *Introduction to Infrared and Electro-Optical Systems*, 3rd ed.]] — 红外与电光系统

## 优先补强清单

| 优先级 | 主题 | 应补来源 | 影响 |
|---|---|---|---|
| P1 | 基础几何光学公式 | 光学教材、镜头厂商应用手册 | 焦距、视场、放大倍率、像圈计算 |
| P1 | 分辨率与采样 | 傅里叶光学教材、数字图像处理教材、传感器厂商文档 | 奈奎斯特、像素精度、过采样、混叠 |
| P1 | 光谱公式 | 光谱仪教材、光栅厂商资料 | 光栅方程、光谱分辨率、棱镜色散 |
| P1 | 色彩科学 | 色彩科学教材、CIE 标准、色彩管理资料 | 色度图、色温、Delta E |
| P2 | 红外成像 | 红外/电光系统教材、红外材料/探测器厂商资料 | 黑体辐射、NETD、波段选择 |
| P2 | 工业照明 | 机器视觉光源厂商手册 | 环光、同轴、背光、远心照明 |
| P3 | 计算成像 | 综述论文、教材 | 第14章计算光学内容 |

## 来源笔记格式

每条来源建议使用 `templates/Source.md`，至少包含：

- 标题、作者/机构、年份
- 来源类型：教材、标准、论文、厂商资料、网页
- 覆盖主题：概念、公式、设备、领域
- 关键结论摘要
- 引用到的知识笔记链接
- 访问或确认日期

## 维护规则

- 公式页没有来源时，状态保持 `draft`。
- 来源已确认、算例已校验后，公式页可提升为 `reviewed`。
- 厂商规格必须记录产品型号和访问日期。
- 标准和论文优先于二手博客；博客可作为学习材料，但不作为最终依据。
