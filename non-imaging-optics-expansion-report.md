# OptiBench 光学知识库非成像光学扩展规划报告

> **任务**：非成像光学核心知识骨架研究  
> **版本**：v1.0  
> **日期**：2026  
> **研究员**：扩展规划子代理

---

## 执行摘要

现有 OptiBench 知识库（约 157 个核心知识文件）高度聚焦于成像光学体系：约 **62%** 的文件为纯成像光学内容（镜头、传感器、MTF、像差、景深等），**34%** 为通用基础物理概念（折射、干涉、衍射、色散等），仅约 **3%** 触及非成像光学的边缘（成像系统中的照明几何）。非成像光学的四大核心支柱——**照明光学、太阳能聚光、显示光学、光通信耦合**——以及**激光光学、光纤光学、集成光子学、辐射度学、光电探测、光调制**等光电子领域，在知识库中几乎完全空白。

本报告提出在保留现有五模块（桥接→几何→波动→光谱→设计）成像体系的基础上，新建三个模块：**模块己｜非成像光学与辐射度学**、**模块庚｜激光光学与光纤通信**、**模块辛｜光电子学与光电探测**，并建议将现有 **34%** 的通用基础内容重新标注为跨模块共享资源，以支撑从"成像入门"到"完整光学体系"的跃迁。预计新增核心概念笔记 **80+**、公式笔记 **40+**、设备笔记 **30+**，形成可扩展为 Obsidian 双链网络的知识骨架。

---

## 任务 1：现有成像光学偏向性深度分析

### 1.1 文件分类统计

对 `OpticKnowledgeSpace` 下核心知识文件（`10-concepts/`、`20-formulas/`、`30-domains/`、`40-devices/`、`50-learning/`）进行逐文件分类，结果如下：

| 分类 | 定义 | 文件数量 | 占比 | 典型示例 |
|------|------|---------|------|----------|
| **【纯成像光学】** | 直接服务于图像形成、图像质量评价或成像系统选型的概念/公式/设备/教程 | **97** | **61.8%** | 焦距、MTF、像差、景深、传感器、像圈、镜头选型 |
| **【通用基础】** | 在成像、非成像、光电子、光谱等多领域共享的基础物理概念，但在知识库中常以成像语境书写 | **53** | **33.8%** | 折射率、干涉、衍射、偏振、光栅方程、黑体辐射、傅里叶光学 |
| **【已覆盖非成像】** | 本质上属于非成像光学范畴，已在知识库中以边缘形式出现 | **5** | **3.2%** | 照明几何、照明方式、同轴/低角度/远心照明 |
| **【未覆盖】** | 知识库中完全缺失的非成像光学领域（非文件分类） | — | — | 照明设计（LED光提取/配光）、CPC聚光、导光板、激光器、光纤、光电探测器等 |

#### 详细分类表（10-concepts/ 93 个文件）

| 文件 | 分类 | 备注 |
|------|------|------|
| `000-refractive-index` | 通用基础 | 所有光学分支的基础 |
| `001-近轴近似` | 通用基础 | 几何光学基础，不限于成像 |
| `002-工作距离` | 纯成像光学 | 工程参数，仅用于成像系统布局 |
| `003-focal-length` / `004-焦距` | 纯成像光学 | 透镜基本属性，但知识库中仅服务于成像 |
| `005-f-number` | 纯成像光学 | 摄影/成像镜头专用参数 |
| `006-数值孔径` | **通用基础** | 显微镜、光纤、聚光、光通信均使用 |
| `007-depth-of-field` | 纯成像光学 | 景深是成像系统的核心指标 |
| `008-放大倍率` | 纯成像光学 | 一阶成像工程 |
| `009-image-circle` / `010-像圈` | 纯成像光学 | 镜头覆盖能力 |
| `011-视场` / `012-视角` | 纯成像光学 | 成像系统视场参数 |
| `013-透视畸变` | 纯成像光学 | 图像几何变形 |
| `014-视差` | 纯成像光学 | 立体视觉/双目成像 |
| `015-法兰距` | 纯成像光学 | 镜头接口标准 |
| `016-abbe-number` | 通用基础 | 材料色散属性，非成像设计也用 |
| `017-dispersion` / `018-色散` | 通用基础 | 物理基础现象 |
| `019-chromatic-aberration` / `020-色差` | 纯成像光学 | 成像像差 |
| `021-interference` / `022-干涉` | 通用基础 | 波动光学基础 |
| `023-diffraction-grating` / `024-衍射光栅` | 通用基础 | 分光基础 |
| `025-diffraction-limit` / `026-衍射极限` | 通用基础 | 物理极限，激光聚焦、光刻等也用 |
| `027-airy-disk` / `028-艾里斑` | 通用基础 | 衍射基础现象 |
| `029-瑞利判据` | 通用基础 | 分辨极限，显微镜/光谱/激光通用 |
| `030-psf` / `031-点扩散函数` | 纯成像光学 | 成像系统脉冲响应 |
| `032-otf` / `033-光学传递函数` | 纯成像光学 | 成像频域响应 |
| `034-mtf` / `035-调制传递函数` | 纯成像光学 | 成像质量评价 |
| `036-pixel` / `037-像素精度` | 纯成像光学 | 传感器采样 |
| `038-nyquist-frequency` / `039-奈奎斯特频率` | 通用基础 | 采样定理，信号处理通用 |
| `040-aliasing` / `041-混叠` | 通用基础 | 采样伪影，信号处理通用 |
| `042-过采样` | 通用基础 | 采样策略通用 |
| `043-边缘检测` | 纯成像光学 | 计算机视觉/图像处理 |
| `044-illumination-geometry` | **已覆盖非成像** | 照明设计是非成像光学子领域 |
| `045-照明方式` | **已覆盖非成像** | 同上 |
| `046-同轴照明` | **已覆盖非成像** | 成像照明，但属照明光学 |
| `047-低角度照明` | **已覆盖非成像** | 同上 |
| `048-远心照明` | **已覆盖非成像** | 同上 |
| `049-分光镜` | 通用基础 | 干涉仪、光通信、光谱仪通用 |
| `050-polarization` / `051-偏振` | 通用基础 | 光的偏振是通用属性 |
| `052-漫射` / `053-镜面反射` | 通用基础 | 表面反射属性 |
| `054-半影` | 通用基础 | 阴影光学 |
| `055-均匀性` | 纯成像光学 | 像面照度均匀性 |
| `056-平场` | 纯成像光学 | 像场平整度 |
| `057-渐晕` | 纯成像光学 | 像面边缘变暗 |
| `058-全局快门` / `059-卷帘快门` | 纯成像光学 | 传感器快门 |
| `060-动态范围` | 纯成像光学 | 传感器成像动态范围 |
| `061-读出噪声` | 纯成像光学 | 传感器噪声 |
| `062-NETD` | 纯成像光学 | 红外成像探测器指标 |
| `063-微测辐射热计` | 纯成像光学 | 红外成像探测器 |
| `064-发射率` | 通用基础 | 辐射度学基础 |
| `065-果冻效应` | 纯成像光学 | 卷帘快门成像伪影 |
| `066-spectral-power-distribution` | 通用基础 | 光谱学基础 |
| `067-color-temperature` / `068-色温` | 通用基础 | 光源属性 |
| `069-chromaticity-diagram` | 通用基础 | 色度学基础 |
| `070-fluorescence` | 通用基础 | 光谱现象 |
| `071-raman-scattering` | 通用基础 | 光谱现象 |
| `072-multispectral-imaging` | 纯成像光学 | 成像光谱 |
| `073-hyperspectral-imaging` | 纯成像光学 | 成像光谱 |
| `074-spectral-resolution` | 通用基础 | 光谱仪器通用指标 |
| `075-snapshot-spectral-imaging` | 纯成像光学 | 成像技术 |
| `076-multispectral-filter-array` | 纯成像光学 | 片上成像 |
| `077-fabry-perot-microcavity` | 通用基础 | 光谱/激光/通信通用 |
| `078-metasurface` | 通用基础 | 超表面，多领域应用 |
| `079-spectral-reconstruction` | 纯成像光学 | 计算成像 |
| `080-双远心` | 纯成像光学 | 远心成像系统 |
| `4f-system` | 纯成像光学 | 空间滤波成像系统 |
| `coherence` | 通用基础 | 波动光学基础 |
| `cutoff-frequency` | 纯成像光学 | 成像系统截止频率 |
| `czerny-turner` | 通用基础 | 光谱仪结构 |
| `fourier-transform-pair` | 通用基础 | 数学/物理基础 |
| `merit-function` | 纯成像光学 | 光学设计评价函数 |
| `slit` | 通用基础 | 光谱仪/衍射通用 |
| `spatial-filtering` | 纯成像光学 | 空间滤波（在知识库中用于成像处理） |
| `spectral-bandwidth` | 通用基础 | 光谱学通用 |
| `strehl-ratio` | 纯成像光学 | 点像质量评价 |
| `wavefront-error` | 纯成像光学 | 波前像差（成像系统） |
| `zernike-polynomials` | 纯成像光学 | 波前拟合（成像系统） |

#### 其他目录统计

| 目录 | 纯成像光学 | 通用基础 | 已覆盖非成像 | 总计 |
|------|-----------|---------|-------------|------|
| `20-formulas/` | 7 | 15 | 0 | 22 |
| `30-domains/` | 6 | 0 | 0 | 6 |
| `40-devices/` | 14 | 4 | 0 | 18 |
| `50-learning/` | 15 | 3 | 0 | 18 |
| **合计** | **97** | **53** | **5** | **157** |

### 1.2 成像光学独占核心概念及其在非成像领域的通用性

以下概念在知识库中被**纯成像独占标注**，但它们实际上在多个非成像领域也是核心工具，只是未被覆盖：

| 成像独占概念 | 现有知识库语境 | 在非成像领域的应用 | 被忽略的原因 |
|-------------|--------------|-----------------|-------------|
| **MTF / OTF**（调制传递函数 / 光学传递函数） | 仅用于成像系统对比度传递评价 | 照明系统的均匀性传递、显示系统的亮度调制传递、光通信系统的频率响应 | 名称中的"成像"暗示了排他性 |
| **PSF**（点扩散函数） | 成像系统对点源的模糊响应 | 激光束聚焦光斑分析、光纤耦合效率计算、照明系统的光斑分布 | 知识库中仅讨论"像质" |
| **数值孔径 NA** | 仅用于显微镜物镜和镜头 | 光纤的集光/发射角、LED光提取效率、CPC聚光器的接受角、光通信耦合 | 标注在成像语境下，未提及光纤/照明等场景 |
| **F值**（F-number） | 仅用于摄影/工业镜头 | 激光聚焦系统的焦深比、照明系统的光束收敛角 | 被视为摄影专用术语 |
| **像差（球差、彗差、像散等）** | 仅用于成像质量劣化分析 | 激光光学中的光束畸变、太阳能聚光器的光斑均匀性、光纤耦合的像差损耗 | 知识库中仅讨论"图像变形" |
| **景深 / 焦深** | 仅用于成像系统清晰度范围 | 激光加工的焦点容差、光纤耦合的轴向容差、显示系统的最佳观看距离 | 仅与"图像清晰"关联 |
| **衍射极限** | 仅用于解释成像分辨率上限 | 激光聚焦的最小光斑极限、光刻系统的最小线宽、CPC聚光器的理论极限 | 与"艾里斑=分辨率"强绑定 |
| **Zernike 多项式** | 仅用于波前像差拟合 | 大气光学中的波前校正、激光光束质量分析、自适应光学系统 | 仅与"光学设计"关联 |
| **偏振** | 仅用于减少眩光/提高对比度 | 液晶显示、电光调制、磁光记录、光通信中的偏振复用、光纤中的偏振模色散 | 仅与"成像对比度"关联 |
| **色散（材料色散）** | 仅用于解释色差 | 光纤通信中的脉冲展宽、飞秒激光的啁啾、光通信中的色散补偿 | 仅与"色差"关联 |
| **光谱分辨率** | 仅用于光谱成像 | 激光线宽测量、光通信信道间隔、光谱仪通用指标 | 知识库中偏向"成像光谱" |
| **积分球** | 仅作为光谱仪校准设备 | LED总光通量测量、激光功率测量、材料反射/透射率测量、辐射度标准 | 知识库中仅提及"光谱仪" |

### 1.3 可重新标注为"通用基础"的现有内容建议

以下文件建议从当前模块中**重新标注为跨模块通用基础**，或在内容中增加"非成像应用"分支，以扩展适用范围：

| 文件路径 | 当前标注 | 建议新标注 | 新增非成像应用方向 |
|----------|---------|-----------|-------------------|
| `10-concepts/006-数值孔径` | 模块乙（几何光学） | **通用基础 + 模块乙 + 模块庚** | 增加光纤NA、LED光提取NA、CPC接受角 |
| `10-concepts/050-polarization` / `051-偏振` | 模块丙（波动光学） | **通用基础 + 模块丙 + 模块辛** | 增加液晶显示、电光调制、磁光效应、光纤偏振模色散 |
| `10-concepts/016-abbe-number` / `017-色散` | 模块乙（几何光学） | **通用基础 + 模块乙 + 模块庚** | 增加光纤色散、激光啁啾、光通信色散补偿 |
| `10-concepts/025-衍射极限` / `027-艾里斑` | 模块丙（波动光学） | **通用基础 + 模块丙 + 模块庚** | 增加激光聚焦极限、光刻分辨率、CPC理论极限 |
| `10-concepts/038-nyquist-frequency` / `040-混叠` | 模块乙（几何光学） | **通用基础 + 模块乙 + 模块辛** | 增加光通信采样、光电子信号处理、光电探测器采样 |
| `10-concepts/064-发射率` | 模块乙（红外成像） | **通用基础 + 模块己** | 增加辐射度学基础、黑体辐射、温度测量 |
| `10-concepts/049-分光镜` | 模块乙（几何光学） | **通用基础 + 模块乙 + 模块庚** | 增加光纤耦合器、光通信分束、激光干涉仪 |
| `20-formulas/015-planck-blackbody` | 模块丁（光谱学） | **通用基础 + 模块己** | 增加辐射度学基础、红外探测、热辐射源 |
| `20-formulas/012-grating-equation` / `013-grating-resolving-power` | 模块丁（光谱学） | **通用基础 + 模块丁 + 模块庚** | 增加激光波长选择、光通信DWDM、光纤光栅 |
| `40-devices/014-integrating-sphere` | 模块丁（光谱学） | **通用基础 + 模块己** | 增加光通量测量、辐射度标准、LED光效测量 |
| `10-concepts/021-干涉` / `022-干涉` | 模块丙（波动光学） | **通用基础 + 模块丙 + 模块庚** | 增加激光干涉仪、光纤干涉、集成光子学干涉器 |

---

## 任务 2：非成像光学核心知识骨架

### 2.1 照明光学（Illumination Design）

照明光学是非成像光学的最大应用分支，关注光能量的高效传输和目标面上的可控分布，而非成像质量。

#### 核心概念（15 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 光学扩展量 | Étendue / Optical Extent | $G = n^2 A \Omega$，描述光学系统的通光能力，在无损理想系统中守恒 |
| 2 | 光通量 | Luminous Flux | 人眼感知的可见光功率，单位流明（lm） |
| 3 | 辐射通量 | Radiant Flux | 客观物理光功率，单位瓦特（W） |
| 4 | 发光强度 | Luminous Intensity | 单位立体角内的光通量，单位坎德拉（cd） |
| 5 | 亮度 | Luminance / Brightness | 单位面积单位立体角的光通量，单位 cd/m² |
| 6 | 照度 | Illuminance | 单位接收面积上的光通量，单位勒克斯（lx） |
| 7 | 配光曲线 | Intensity Distribution Curve (IDC) | 光源发光强度随角度的分布函数 $I(	heta)$ |
| 8 | LED 光提取效率 | LED Light Extraction Efficiency | LED 芯片内部产生光子逃逸到外部空间的效率 |
| 9 | 光学效率 | Optical Efficiency | 光源发出的光通量到达目标面的比例 |
| 10 | 均匀性 | Uniformity | 目标面内最大/最小照度之比或标准差比 |
| 11 | 朗伯体 | Lambertian Emitter | 辐射亮度不随角度变化的理想漫射表面，$I(	heta) = I_0 \cos	heta$ |
| 12 | 自由曲面 | Freeform Surface | 无旋转对称性的非球面光学表面，用于任意配光控制 |
| 13 | 光线耦合 | Light Coupling | 将光源发出的光高效导入传输或接收系统的非成像过程 |
| 14 | 光能利用率 | Light Utilization Ratio | 有效照明区域内的光通量与总光源光通量之比 |
| 15 | 蒙特卡洛光线追迹 | Monte Carlo Ray Tracing | 用随机光线统计方法模拟非成像光学系统的能量分布 |

#### 核心公式 / 计算模型（8 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 光学扩展量 | $G = n^2 A \int \cos	heta \, d\Omega = n^2 A \pi \sin^2	heta$ | 面积×立体角×折射率平方，守恒量 |
| 2 | 光学效率极限 | $\eta_{max} = G_{target} / G_{source}$ | 受 étendue 守恒限制的最大效率 |
| 3 | 朗伯体辐射定律 | $L = I / (A \cos	heta) = 	ext{const}$ | 亮度与方向无关，$I(	heta) = I_0 \cos	heta$ |
| 4 | 照度距离平方反比 | $E = I / r^2$ | 点光源在距离 $r$ 处的照度（垂直入射） |
| 5 | 照度余弦定律 | $E = I \cos	heta / r^2$ | 倾斜入射时的照度 |
| 6 | 均匀度评价 | $U = E_{min} / E_{max}$ 或 $U = 1 - \sigma / ar{E}$ | 目标面照度均匀性指标 |
| 7 | LED 光提取效率 | $\eta_{ex} = (1 - \cos	heta_c) / 2$（简单模型） | $	heta_c = rcsin(1/n)$ 为全反射临界角 |
| 8 | 自由曲面映射方程 | $\int_0^{	heta} I_{source}(	heta') \sin	heta' \, d	heta' = \int_0^{r} E_{target}(r') \cdot 2\pi r' \, dr'$ | 边缘光线理论，能量守恒映射 |

#### 典型设备 / 组件（8 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | LED 光源 | LED Light Source | 固态照明核心，光谱窄、效率高、方向性强 |
| 2 | 自由曲面透镜 | Freeform Lens | 对 LED 朗伯光场进行任意整形，实现特定配光 |
| 3 | 反射杯 / 反光罩 | Reflector Cup | 收集 LED 后向光并重新定向，提高光利用率 |
| 4 | 导光管 / 光导管 | Light Pipe / Light Guide | 利用全内反射传输光能，用于局部照明和指示 |
| 5 | 积分棒 / 均光棒 | Integrating Rod / Homogenizer | 通过多次反射实现截面均匀化，用于光刻照明 |
| 6 | 微透镜阵列 | Microlens Array (MLA) | 将光源分割成多束子光束再叠加，提高均匀性 |
| 7 | 扩散板 / 漫射板 | Diffuser Plate | 破坏光束方向性，实现面光源均匀化 |
| 8 | 准直透镜 | Collimator Lens | 将发散光转换为平行光，用于投影和光耦合 |

#### 建议知识库骨架（照明光学）

```
10-concepts/
  100-etendue.md                          # 光学扩展量
  101-luminous-flux.md                     # 光通量/辐射通量
  102-luminance.md                         # 亮度
  103-illuminance.md                       # 照度
  104-intensity-distribution-curve.md      # 配光曲线
  105-light-extraction-efficiency.md       # LED光提取效率
  106-uniformity.md                        # 均匀性
  107-lambertian-emitter.md                # 朗伯体
  108-freeform-surface.md                  # 自由曲面
  109-light-coupling.md                    # 光线耦合
  110-optical-efficiency.md                # 光学效率
  111-monte-carlo-ray-tracing.md           # 蒙特卡洛光线追迹

20-formulas/
  100-etendue-conservation.md              # 光学扩展量守恒
  101-lambert-cosine-law.md                # 朗伯余弦定律
  102-inverse-square-law.md                # 照度距离平方反比
  103-uniformity-metrics.md                # 均匀度评价公式
  104-led-extraction-efficiency.md          # LED光提取效率
  105-freeform-mapping-equation.md         # 自由曲面映射方程
  106-optical-efficiency-limit.md          # 光学效率极限
  107-lumen-calculation.md                 # 光通量计算

40-devices/
  100-led-source.md                        # LED光源
  101-freeform-lens.md                     # 自由曲面透镜
  102-reflector-cup.md                     # 反射杯
  103-light-pipe.md                        # 导光管
  104-integrating-rod.md                   # 积分棒
  105-microlens-array.md                   # 微透镜阵列
  106-diffuser-plate.md                    # 扩散板
  107-collimator-lens.md                   # 准直透镜

50-learning/ （新增章节）
  017-illumination-design-nonimaging.md    # 非成像照明设计基础
```

---

### 2.2 太阳能聚光（Solar Concentrator）

太阳能聚光是非成像光学的起源领域之一，目标是将大面积入射太阳光能量集中到小面积接收器上，最大化能量密度而非成像质量。

#### 核心概念（12 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 复合抛物面聚光器 | Compound Parabolic Concentrator (CPC) | 由两段抛物线组成的非成像聚光器，可在接受角内实现理想聚光 |
| 2 | 聚光比 | Concentration Ratio (C) | 入射孔径面积与接收器面积之比 $C = A_{in} / A_{out}$ |
| 3 | 接受角 | Acceptance Angle ($2	heta_c$) | 聚光器能收集光线的最大入射角范围 |
| 4 | 几何聚光比 | Geometric Concentration Ratio | 仅由几何尺寸决定的理论聚光比 |
| 5 | 光学效率 | Optical Efficiency | 实际到达接收器的能量与入射能量之比 |
| 6 | 光通量映射 | Flux Mapping | 描述入射光通量在接收器上空间分布的映射关系 |
| 7 | 边缘光线原理 | Edge Ray Principle | 非成像光学设计的核心原理：边缘入射光线对应边缘出射光线 |
| 8 | 截断 | Truncation | 为减小 CPC 高度而截去顶部不贡献部分 |
| 9 | 菲涅尔透镜 | Fresnel Lens | 将连续曲面压缩为同心棱镜环的聚光元件，用于薄型聚光 |
| 10 | 二次反射聚光器 | Secondary Concentrator | 在初级聚光器后增加的小型 CPC，用于提高聚光比 |
| 11 | 热斑效应 | Hot Spot Effect | 接收器上光通量分布不均匀导致的局部高温 |
| 12 | 太阳跟踪 | Solar Tracking | 主动调整聚光器朝向以对准太阳的运动机构 |

#### 核心公式 / 计算模型（7 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | CPC 二维理想聚光比 | $C = 1 / \sin	heta_c$ | $	heta_c$ 为接受半角，理论上二维极限 |
| 2 | 三维聚光比极限 | $C_{max} = 1 / \sin^2	heta_c$ | 旋转对称三维 CPC 的理论极限 |
| 3 | 光学效率 | $\eta = \Phi_{receiver} / \Phi_{incident}$ | 实际到达接收器的能量比例 |
| 4 | 年均能量增益 | $G = C 	imes \eta 	imes f_{track}$ | 聚光比×光学效率×跟踪因子 |
| 5 | 菲涅尔透镜焦距 | $f = r_i / 	an	heta_i$ | 第 $i$ 环棱镜的焦距设计 |
| 6 | CPC 轮廓曲线 | $r(\phi) = 2f / (1 - \cos\phi)$ | 抛物线极坐标方程，用于构建 CPC |
| 7 | 热平衡方程 | $q'' = \eta \cdot C \cdot G_{solar} - h(T - T_{amb}) - arepsilon\sigma(T^4 - T_{amb}^4)$ | 接收器热流平衡 |

#### 典型设备 / 组件（6 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | CPC 聚光器 | CPC Concentrator | 非成像聚光的核心器件，无跟踪或低跟踪要求 |
| 2 | 菲涅尔聚光透镜 | Fresnel Concentrator | 薄型大面积聚光，常用于光伏聚光系统 |
| 3 | 抛物槽式聚光器 | Parabolic Trough Collector | 一维聚光，用于太阳能热发电 |
| 4 | 塔式定日镜 | Heliostat Field | 大面积平面反射镜阵列，将光聚焦到中央接收塔 |
| 5 | 接收器 / 吸收器 | Solar Receiver / Absorber | 将聚焦光能转换为热能或电能的器件 |
| 6 | 太阳跟踪系统 | Solar Tracking System | 单轴/双轴跟踪机构，保证聚光器对准太阳 |

#### 建议知识库骨架（太阳能聚光）

```
10-concepts/
  120-cpc-concentrator.md                  # 复合抛物面聚光器
  121-concentration-ratio.md               # 聚光比
  122-acceptance-angle.md                  # 接受角
  123-geometric-concentration.md           # 几何聚光比
  124-flux-mapping.md                      # 光通量映射
  125-edge-ray-principle.md                # 边缘光线原理
  126-truncation.md                        # 截断
  127-fresnel-lens.md                      # 菲涅尔透镜
  128-secondary-concentrator.md            # 二次反射聚光器
  129-hot-spot-effect.md                   # 热斑效应
  130-solar-tracking.md                    # 太阳跟踪

20-formulas/
  120-cpc-concentration-ratio.md           # CPC聚光比公式
  121-3d-concentration-limit.md            # 三维聚光极限
  122-optical-efficiency-concentrator.md   # 聚光光学效率
  123-fresnel-lens-design.md               # 菲涅尔透镜设计公式
  124-cpc-profile-equation.md              # CPC轮廓方程
  125-thermal-balance.md                   # 热平衡方程
  126-annual-energy-gain.md               # 年均能量增益

40-devices/
  120-cpc-concentrator.md                  # CPC聚光器
  121-fresnel-concentrator.md              # 菲涅尔聚光透镜
  122-parabolic-trough.md                  # 抛物槽式聚光器
  123-heliostat.md                         # 塔式定日镜
  124-solar-receiver.md                    # 接收器/吸收器
  125-solar-tracker.md                     # 太阳跟踪系统

50-learning/ （新增章节）
  018-solar-concentrator-design.md         # 太阳能聚光器设计基础
```

---

### 2.3 显示光学（Display Optics）

显示光学关注如何将光源转换为均匀、可控、高亮度的面光源，用于 LCD/OLED 等显示器件，属于典型的非成像光学应用。

#### 核心概念（13 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 背光模组 | Backlight Unit (BLU) | 为 LCD 提供均匀面光源的光学组件系统 |
| 2 | 导光板 | Light Guide Plate (LGP) | 利用全内反射将侧入光转换为面出光的平板光学元件 |
| 3 | 微透镜阵列 | Microlens Array (MLA) | 用于背光准直和亮度增强的周期透镜阵列 |
| 4 | 扩散膜 | Diffusion Film / Diffuser | 破坏光束方向性，均匀化亮暗分布 |
| 5 | 增亮膜 | Brightness Enhancement Film (BEF) | 利用棱镜结构回收大角度光，将光能集中在正向视角 |
| 6 | 反射型偏振增亮膜 | Dual Brightness Enhancement Film (DBEF) | 反射一种偏振态、透射另一种，配合偏振循环提高亮度 |
| 7 | 全内反射 | Total Internal Reflection (TIR) | 导光板的核心传输机制，入射角大于临界角时完全反射 |
| 8 | 网点 / 散射点 | Dot Pattern / Extractor Pattern | 导光板表面的微结构，破坏 TIR 使光从正面出射 |
| 9 | 色域 | Color Gamut | 显示系统能重现的颜色范围，常用 NTSC/sRGB/DCI-P3 百分比 |
| 10 | 亮度均匀性 | Luminance Uniformity | 显示面内最大/最小亮度之比 |
| 11 | 视角特性 | Viewing Angle Characteristics | 显示亮度/对比度/色度随观看角度变化的特性 |
| 12 | 局部调光 | Local Dimming | 分区控制背光亮度，提高对比度 |
| 13 | Mini-LED / Micro-LED | Mini-LED / Micro-LED Backlight | 高密度 LED 阵列实现精细局部调光 |

#### 核心公式 / 计算模型（6 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 导光板 TIR 临界角 | $	heta_c = rcsin(n_{air} / n_{LGP})$ | 光在导光板内全内反射的条件 |
| 2 | 网点密度分布 | $ho(x) \propto 1 / P_{rem}(x)$ | 剩余光功率的反比，保证均匀出光 |
| 3 | 增亮膜增益 | $G_{BEF} = 1 / \sin^2	heta_{view}$ | 视角压缩带来的正向亮度增益 |
| 4 | 色域面积比 | $G = A_{display} / A_{sRGB} 	imes 100\%$ | 相对于标准色域的覆盖面积百分比 |
| 5 | 亮度均匀性 | $U = L_{min} / L_{max} 	imes 100\%$ | 显示面内最小与最大亮度比 |
| 6 | 光效 | $\eta = L \cdot A / P_{electrical}$ | 亮度×面积/电功率，单位 cd/m²/W |

#### 典型设备 / 组件（7 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 侧入式背光模组 | Edge-lit BLU | LED 位于导光板侧边，薄型设计 |
| 2 | 直下式背光模组 | Direct-lit BLU | LED 阵列位于扩散板后方，可实现局部调光 |
| 3 | 导光板 | Light Guide Plate | PMMA 或 PC 材质，通过网点实现光提取 |
| 4 | 增亮膜 (BEF) | Brightness Enhancement Film | 3M 棱镜膜，将大角度光回收至正向 |
| 5 | 反射型偏振膜 (DBEF) | Reflective Polarizer | 提高偏振光利用率，通常配合 BEF 使用 |
| 6 | 扩散膜 | Diffuser | 均匀化光斑，隐藏网点和 LED 颗粒 |
| 7 | 反射片 | Reflective Sheet | 位于导光板底部，回收泄漏光 |

#### 建议知识库骨架（显示光学）

```
10-concepts/
  140-backlight-unit.md                    # 背光模组
  141-light-guide-plate.md                 # 导光板
  142-microlens-array-display.md           # 微透镜阵列（显示应用）
  143-diffusion-film.md                    # 扩散膜
  144-brightness-enhancement-film.md       # 增亮膜 BEF
  145-reflective-polarizer.md              # 反射型偏振增亮膜 DBEF
  146-total-internal-reflection.md         # 全内反射（显示语境）
  147-dot-pattern.md                       # 网点/散射点
  148-color-gamut.md                       # 色域
  149-luminance-uniformity.md              # 亮度均匀性
  150-viewing-angle.md                     # 视角特性
  151-local-dimming.md                     # 局部调光
  152-mini-led-backlight.md                # Mini-LED背光

20-formulas/
  140-tir-critical-angle.md                # TIR临界角
  141-dot-density-distribution.md          # 网点密度分布
  142-bef-gain.md                          # 增亮膜增益
  143-color-gamut-ratio.md                 # 色域面积比
  144-luminance-uniformity-formula.md      # 亮度均匀性公式
  145-optical-efficiency-blu.md            # 背光模组光效

40-devices/
  140-edge-lit-blu.md                      # 侧入式背光模组
  141-direct-lit-blu.md                    # 直下式背光模组
  142-light-guide-plate-device.md          # 导光板
  143-bef-film.md                          # 增亮膜
  144-dbef-film.md                         # 反射型偏振膜
  145-diffuser-film.md                     # 扩散膜
  146-reflective-sheet.md                  # 反射片

50-learning/ （新增章节）
  019-display-optics.md                    # 显示光学基础
```

---

### 2.4 光通信耦合光学（Coupling Optics for Optical Communication）

光通信中的耦合光学关注如何将光源高效耦合进光纤，以及光纤之间的对接，是典型的非成像光学问题。

#### 核心概念（10 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 耦合效率 | Coupling Efficiency | $\eta = P_{fiber} / P_{source}$，光源到光纤的功率传输比例 |
| 2 | 模式匹配 | Mode Matching | 使光源场分布与光纤本征模场分布重叠最大化的过程 |
| 3 | 光纤数值孔径 | Fiber Numerical Aperture | $NA = \sqrt{n_{core}^2 - n_{clad}^2}$，描述光纤集光角 |
| 4 | 模场直径 | Mode Field Diameter (MFD) | 单模光纤中光强下降到 $1/e^2$ 时的直径 |
| 5 | 对接损耗 | Butt Coupling Loss | 两光纤端面直接对接时的功率损耗 |
| 6 | 横向失准损耗 | Lateral Misalignment Loss | 光纤轴线横向偏移引起的耦合损耗 |
| 7 | 角度失准损耗 | Angular Misalignment Loss | 光纤轴线倾斜引起的耦合损耗 |
| 8 | 轴向间隙损耗 | Gap Loss | 两光纤端面之间存在间隙时的损耗 |
| 9 | 透镜耦合 | Lens Coupling | 使用透镜将光源成像到光纤端面，提高耦合效率 |
| 10 | 光纤熔接 | Fiber Splicing | 通过加热将两根光纤熔融连接，实现低损耗永久连接 |

#### 核心公式 / 计算模型（6 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 光纤 NA | $NA = \sqrt{n_{core}^2 - n_{clad}^2} pprox n_{core}\sqrt{2\Delta}$ | $\Delta = (n_{core} - n_{clad})/n_{core}$ |
| 2 | 接受角 | $	heta_{max} = rcsin(NA)$ | 光纤能接收的最大入射角 |
| 3 | 高斯光束耦合效率 | $\eta = |\int E_{source} E_{fiber}^* \, dA|^2 / (\int |E_{source}|^2 \, dA \cdot \int |E_{fiber}|^2 \, dA)$ | 模式重叠积分 |
| 4 | 横向失准损耗 | $L_{lat} = -10\log_{10} \exp(-d^2 / w^2)$ | $d$ 为偏移量，$w$ 为模场半径 |
| 5 | 角度失准损耗 | $L_{ang} = -10\log_{10} \exp(-(\pi n w 	heta / \lambda)^2)$ | $	heta$ 为倾斜角 |
| 6 | 菲涅尔反射损耗 | $R = ((n_1 - n_2)/(n_1 + n_2))^2$，$L = -10\log_{10}(1-R)$ | 端面反射损耗 |

#### 典型设备 / 组件（5 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 光纤连接器 | Fiber Connector | FC/SC/LC/MPO 等可插拔光纤连接器件 |
| 2 | 光纤熔接机 | Fusion Splicer | 将两根光纤熔融连接的精密设备 |
| 3 | 光纤耦合透镜 | Fiber Coupling Lens | 将激光器输出准直并聚焦到光纤端面 |
| 4 | 光纤适配器 | Fiber Adapter / Coupler | 连接不同接口类型光纤的转接器件 |
| 5 | 光纤对准平台 | Fiber Alignment Stage | 六维精密调节平台，用于实验室耦合优化 |

#### 建议知识库骨架（耦合光学）

```
10-concepts/
  160-coupling-efficiency.md               # 耦合效率
  161-mode-matching.md                     # 模式匹配
  162-fiber-na.md                          # 光纤数值孔径
  163-mode-field-diameter.md               # 模场直径
  164-butt-coupling-loss.md                # 对接损耗
  165-lateral-misalignment.md             # 横向失准
  166-angular-misalignment.md             # 角度失准
  167-gap-loss.md                          # 轴向间隙损耗
  168-lens-coupling.md                     # 透镜耦合
  169-fiber-splicing.md                    # 光纤熔接

20-formulas/
  160-fiber-na-formula.md                  # 光纤NA公式
  161-acceptance-angle.md                  # 接受角
  162-gaussian-coupling-efficiency.md      # 高斯耦合效率
  163-lateral-loss-formula.md              # 横向失准损耗
  164-angular-loss-formula.md            # 角度失准损耗
  165-fresnel-reflection-loss.md           # 菲涅尔反射损耗

40-devices/
  160-fiber-connector.md                     # 光纤连接器
  161-fusion-splicer.md                    # 光纤熔接机
  162-fiber-coupling-lens.md                 # 光纤耦合透镜
  163-fiber-adapter.md                     # 光纤适配器
  164-alignment-stage.md                     # 光纤对准平台

50-learning/ （新增章节）
  020-optical-communication-coupling.md      # 光通信耦合光学基础
```

---

## 任务 3：激光光学与光子学核心知识骨架

### 3.1 激光器原理（Laser Principles）

#### 核心概念（15 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 受激辐射 | Stimulated Emission | 入射光子诱导激发态原子辐射同相位光子，激光产生机制 |
| 2 | 粒子数反转 | Population Inversion | 高能态粒子数多于低能态，激光增益的必要条件 |
| 3 | 光学谐振腔 | Optical Resonator / Cavity | 由两个反射镜构成的光反馈系统，决定激光模式 |
| 4 | 增益介质 | Gain Medium | 提供受激辐射放大作用的材料（气体/固体/半导体/光纤） |
| 5 | 泵浦 | Pumping | 向增益介质注入能量以建立粒子数反转的过程 |
| 6 | 激光阈值 | Laser Threshold | 增益等于损耗时的临界泵浦功率，超过此值产生激光振荡 |
| 7 | 纵模 / 横模 | Longitudinal Mode / Transverse Mode | 谐振腔中允许的轴向/横向驻波模式，TEM$_{mn}$ |
| 8 | 品质因数 Q | Quality Factor Q | 谐振腔储能与损耗之比，$Q = \omega_0 W / P_{loss}$ |
| 9 | Q 开关 | Q-Switching | 突然降低谐振腔 Q 值以释放巨脉冲的技术 |
| 10 | 锁模 | Mode Locking | 强制多纵模相位同步，产生超短脉冲（ps/fs 级） |
| 11 | 调 Q | Q-Switching (Active/Passive) | 主动（电光/声光）或被动（可饱和吸收体）Q 开关 |
| 12 | 腔倒空 | Cavity Dumping | 在激光腔内存储能量后突然将其全部输出 |
| 13 | 斜率效率 | Slope Efficiency | 输出功率-泵浦功率曲线高于阈值部分的斜率 |
| 14 | 光束质量 | Beam Quality | 描述激光束接近理想高斯光束的程度，用 $M^2$ 表征 |
| 15 | 相干长度 | Coherence Length | $L_c = c / \Delta
u$，光源时间相干性的度量 |

#### 核心公式 / 计算模型（8 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 激光阈值条件 | $g_{th} = lpha + rac{1}{2L}\lnrac{1}{R_1 R_2}$ | 阈值增益 = 内部损耗 + 输出耦合损耗 |
| 2 | 输出耦合率 | $T = 1 - R$（单端输出） | 输出镜透射率 |
| 3 | 斜率效率 | $\eta_s = \eta_{pump} \cdot \eta_{quantum} \cdot \eta_{coupling}$ | 泵浦效率×量子效率×耦合效率 |
| 4 | 谐振腔纵模频率 | $
u_q = q \cdot c / (2nL)$ | $q$ 为整数，相邻纵模间隔 $\Delta
u = c / (2nL)$ |
| 5 | 谐振腔细度 | $\mathcal{F} = \pi\sqrt{R_1 R_2} / (1 - R_1 R_2)$ | 谐振腔频率选择性 |
| 6 | Q 值 | $Q = 2\pi
u_0 W / P_{loss} = 
u_0 / \Delta
u_{FWHM}$ | 储能/损耗或频率/线宽 |
| 7 | 锁模脉冲宽度 | $\Delta t pprox 1 / \Delta
u_{gain}$ | 增益带宽越宽，脉冲越短 |
| 8 | 粒子数反转密度 | $\Delta N = N_2 - (g_2/g_1)N_1 > 0$ | 实现受激辐射放大的条件 |

#### 典型设备 / 组件（8 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 激光二极管 | Laser Diode (LD) | 半导体激光器，电泵浦，体积小、效率高 |
| 2 | 固体激光器 | Solid-State Laser | Nd:YAG、Ti:Sapphire 等，光泵浦或二极管泵浦 |
| 3 | 光纤激光器 | Fiber Laser | 增益介质为掺杂光纤（Er/Yb），高效、光束质量好 |
| 4 | 气体激光器 | Gas Laser | He-Ne、CO₂、Ar⁺ 等，气体放电泵浦 |
| 5 | 电光调制器 | Electro-Optic Modulator (EOM) | 主动 Q 开关和锁模的关键器件 |
| 6 | 声光调制器 | Acousto-Optic Modulator (AOM) | 利用声光效应进行光束调制和 Q 开关 |
| 7 | 可饱和吸收体 | Saturable Absorber | 被动 Q 开关和被动锁模元件（如 SESAM、Cr:YAG） |
| 8 | 激光电源与温控 | Laser Power Supply & TEC | 提供稳定泵浦电流和精确温度控制 |

#### 建议知识库骨架（激光器原理）

```
10-concepts/
  200-stimulated-emission.md               # 受激辐射
  201-population-inversion.md              # 粒子数反转
  202-optical-resonator.md                 # 光学谐振腔
  203-gain-medium.md                       # 增益介质
  204-pumping.md                           # 泵浦
  205-laser-threshold.md                   # 激光阈值
  206-longitudinal-mode.md                 # 纵模
  207-transverse-mode.md                   # 横模
  208-quality-factor.md                    # 品质因数Q
  209-q-switching.md                        # Q开关
  210-mode-locking.md                      # 锁模
  211-cavity-dumping.md                    # 腔倒空
  212-slope-efficiency.md                  # 斜率效率
  213-beam-quality.md                      # 光束质量
  214-coherence-length.md                  # 相干长度

20-formulas/
  200-laser-threshold-condition.md         # 激光阈值条件
  201-output-coupling.md                   # 输出耦合率
  202-slope-efficiency-formula.md          # 斜率效率
  203-longitudinal-mode-frequency.md       # 纵模频率
  204-finesse-formula.md                   # 谐振腔细度
  205-q-value.md                           # Q值
  206-mode-locked-pulse-width.md           # 锁模脉冲宽度
  207-population-inversion-density.md      # 粒子数反转密度

40-devices/
  200-laser-diode.md                       # 激光二极管
  201-solid-state-laser.md                 # 固体激光器
  202-fiber-laser.md                       # 光纤激光器
  203-gas-laser.md                         # 气体激光器
  204-electro-optic-modulator.md           # 电光调制器
  205-acousto-optic-modulator.md           # 声光调制器
  206-saturable-absorber.md                # 可饱和吸收体
  207-laser-power-supply.md                # 激光电源与温控

50-learning/ （新增章节）
  021-laser-principles.md                  # 激光器原理基础
```

---

### 3.2 光束传播（Beam Propagation）

#### 核心概念（12 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 高斯光束 | Gaussian Beam | 激光器输出的基模光束，横向强度呈高斯分布 |
| 2 | 光束腰 / 束腰 | Beam Waist | 高斯光束的最小半径位置，$w_0$ |
| 3 | 瑞利范围 | Rayleigh Range | $z_R = \pi w_0^2 / \lambda$，束腰到光斑扩大 $\sqrt{2}$ 倍的距离 |
| 4 | 光束发散角 | Beam Divergence Angle | 远场半角，$	heta = \lambda / (\pi w_0)$（理想高斯） |
| 5 | 光束质量因子 $M^2$ | Beam Quality Factor $M^2$ | 实际光束与理想高斯光束的发散-束腰乘积比，$M^2 \geq 1$ |
| 6 | 光束参数乘积 | Beam Parameter Product (BPP) | $BPP = w_0 \cdot 	heta = M^2 \lambda / \pi$ |
| 7 | 聚焦光斑 | Focused Spot | 透镜聚焦后的最小光斑半径，$w_f = f \cdot \lambda / (\pi w_{in})$ |
| 8 | 焦深 / 景深 | Depth of Focus (DOF) | 聚焦光斑半径不超过 $\sqrt{2}w_f$ 的轴向范围，$pprox 2z_R$ |
| 9 | Gouy 相位 | Gouy Phase | 高斯光束通过焦点时产生的 $\pi$ 相位跳变 |
| 10 | 高斯焦移 | Gaussian Focus Shift | 实际最佳聚焦位置与几何焦点偏离的现象 |
| 11 | 近场 / 远场 | Near Field / Far Field | 菲涅尔衍射区（$z < z_R$）与夫琅禾费衍射区（$z \gg z_R$） |
| 12 | 光束整形 | Beam Shaping | 将高斯光束转换为平顶、环形或其他强度分布的技术 |

#### 核心公式 / 计算模型（8 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 高斯光束半径 | $w(z) = w_0 \sqrt{1 + (z/z_R)^2}$ | 沿传播轴的光束半径变化 |
| 2 | 瑞利范围 | $z_R = \pi w_0^2 / \lambda$ | 理想高斯光束 |
| 3 | 发散角（理想） | $	heta = \lambda / (\pi w_0)$ | 理想高斯光束远场半角 |
| 4 | 发散角（实际） | $	heta = M^2 \lambda / (\pi w_0)$ | 实际光束，$M^2$ 为质量因子 |
| 5 | 光束质量因子 | $M^2 = \pi w_0 	heta / \lambda$ | ISO 11146 标准定义 |
| 6 | 聚焦光斑半径 | $w_f = (M^2 \lambda f) / (\pi w_{in})$ | $f$ 为透镜焦距，$w_{in}$ 为入射光束半径 |
| 7 | 焦深 | $DOF = 2z_R = 2\pi w_f^2 / (M^2 \lambda)$ | 聚焦区域的轴向范围 |
| 8 | Gouy 相位 | $\psi(z) = rctan(z/z_R)$ | 通过焦点时从 $-\pi/2$ 到 $+\pi/2$ 变化 |

#### 典型设备 / 组件（6 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 光束质量分析仪 | Beam Quality Analyzer | 测量 $M^2$ 因子、束腰、发散角 |
| 2 | 扫描狭缝式光束分析仪 | Scanning Slit Beam Profiler | 用刀口/狭缝扫描测量光束轮廓 |
| 3 | CCD 光束分析仪 | CCD Beam Profiler | 直接成像测量光束横截面强度分布 |
| 4 | 扩束镜 / 缩束镜 | Beam Expander / Reducer | 改变激光束直径和发散角的无焦系统 |
| 5 | 聚焦透镜 | Focusing Lens | 将激光束聚焦到极小光斑，用于加工/耦合 |
| 6 | 空间滤波器 | Spatial Filter | 在焦点处放置小孔滤除高阶模，净化光束 |

#### 建议知识库骨架（光束传播）

```
10-concepts/
  220-gaussian-beam.md                     # 高斯光束
  221-beam-waist.md                        # 束腰
  222-rayleigh-range.md                    # 瑞利范围
  223-beam-divergence.md                   # 光束发散角
  224-m2-factor.md                         # 光束质量因子M²
  225-beam-parameter-product.md            # 光束参数乘积
  226-focused-spot.md                       # 聚焦光斑
  227-depth-of-focus.md                    # 焦深
  228-gouy-phase.md                        # Gouy相位
  229-gaussian-focus-shift.md              # 高斯焦移
  230-near-far-field.md                    # 近场/远场
  231-beam-shaping.md                      # 光束整形

20-formulas/
  220-gaussian-beam-radius.md              # 高斯光束半径
  221-rayleigh-range-formula.md            # 瑞利范围
  222-divergence-ideal.md                  # 理想发散角
  223-divergence-real.md                   # 实际发散角
  224-m2-factor-formula.md                 # M²因子
  225-focused-spot-radius.md               # 聚焦光斑半径
  226-depth-of-focus-formula.md            # 焦深
  227-gouy-phase-formula.md                # Gouy相位

40-devices/
  220-beam-quality-analyzer.md             # 光束质量分析仪
  221-scanning-slit-profiler.md            # 扫描狭缝式分析仪
  222-ccd-beam-profiler.md                 # CCD光束分析仪
  223-beam-expander.md                     # 扩束镜
  224-focusing-lens.md                     # 聚焦透镜
  225-spatial-filter.md                    # 空间滤波器
```

---

### 3.3 光纤光学（Fiber Optics）

#### 核心概念（15 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 单模光纤 | Single-Mode Fiber (SMF) | 仅支持基模（HE₁₁）传输，芯径 8–10 μm，用于长距离通信 |
| 2 | 多模光纤 | Multi-Mode Fiber (MMF) | 支持多个模式传输，芯径 50/62.5 μm，用于短距离 |
| 3 | 数值孔径 | Numerical Aperture (NA) | $NA = \sqrt{n_{core}^2 - n_{clad}^2}$，描述光纤集光能力 |
| 4 | 归一化频率 | Normalized Frequency (V-number) | $V = (2\pi a / \lambda) \cdot NA$，决定模式数量 |
| 5 | 衰减 | Attenuation / Loss | 光功率沿光纤传输的衰减，单位 dB/km |
| 6 | 材料色散 | Material Dispersion | 纤芯材料折射率随波长变化导致的脉冲展宽 |
| 7 | 波导色散 | Waveguide Dispersion | 波导结构引起的群速度随波长变化 |
| 8 | 模间色散 | Intermodal Dispersion | 多模光纤中不同模式传播速度不同导致的脉冲展宽 |
| 9 | 偏振模色散 | Polarization Mode Dispersion (PMD) | 双折射引起的两个正交偏振模传播速度差异 |
| 10 | 非线性效应 | Nonlinear Effects | 高功率下纤芯内光与物质相互作用：SPM、XPM、FWM、SBS、SRS |
| 11 | 自相位调制 | Self-Phase Modulation (SPM) | 光强引起折射率变化，导致自身相位调制 |
| 12 | 四波混频 | Four-Wave Mixing (FWM) | 三个频率相互作用产生第四个频率的非线性过程 |
| 13 | 光纤放大器 | Optical Fiber Amplifier | EDFA（掺铒光纤放大器）等，直接放大光信号无需光电转换 |
| 14 | 拉曼放大器 | Raman Amplifier | 利用受激拉曼散射在传输光纤中分布式放大 |
| 15 | 光纤布拉格光栅 | Fiber Bragg Grating (FBG) | 纤芯内周期性折射率调制，用于滤波、色散补偿、传感 |

#### 核心公式 / 计算模型（8 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 光纤 NA | $NA = \sqrt{n_{core}^2 - n_{clad}^2}$ | 集光能力 |
| 2 | V 数 | $V = (2\pi a / \lambda) \cdot NA$ | $a$ 为芯半径，$V < 2.405$ 为单模 |
| 3 | 衰减 | $lpha = -rac{10}{L}\log_{10}(P_{out}/P_{in})$ | 单位 dB/km |
| 4 | 材料色散 | $D_m = -rac{\lambda}{c}rac{d^2n}{d\lambda^2}$ | 单位 ps/(nm·km) |
| 5 | 总色散 | $D_{total} = D_m + D_w$ | 材料色散 + 波导色散 |
| 6 | 模间色散（阶跃） | $\Delta	au_{inter} pprox rac{n_1\Delta}{c} \cdot L$ | $\Delta = (n_1-n_2)/n_1$ |
| 7 | 非线性折射率 | $n = n_0 + n_2 I$ | $n_2 pprox 2.6 	imes 10^{-20}$ m²/W（石英） |
| 8 | EDFA 增益 | $G = \exp(g_0 L)$ | $g_0$ 为增益系数，典型 20–40 dB |

#### 典型设备 / 组件（8 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 单模光纤 | SMF (G.652/G.655) | 标准通信光纤，低损耗、低色散 |
| 2 | 多模光纤 | MMF (OM3/OM4/OM5) | 数据中心短距离连接，高耦合效率 |
| 3 | 掺铒光纤放大器 | EDFA | 1550 nm 波段光信号直接放大 |
| 4 | 拉曼放大器 | Raman Amplifier | 分布式放大，噪声更低 |
| 5 | 光纤隔离器 | Optical Isolator | 防止反射光返回激光器，保护光源 |
| 6 | 光纤环行器 | Optical Circulator | 单向传输器件，用于 DWDM 和传感 |
| 7 | 光纤耦合器 | Fiber Coupler / Splitter | 将光功率分路或合路 |
| 8 | 光纤布拉格光栅 | FBG | 波长选择反射，用于滤波和传感 |

#### 建议知识库骨架（光纤光学）

```
10-concepts/
  240-single-mode-fiber.md                 # 单模光纤
  241-multi-mode-fiber.md                  # 多模光纤
  242-fiber-na.md                          # 光纤数值孔径
  243-v-number.md                          # 归一化频率
  244-attenuation.md                         # 衰减
  245-material-dispersion.md               # 材料色散
  246-waveguide-dispersion.md              # 波导色散
  247-intermodal-dispersion.md             # 模间色散
  248-polarization-mode-dispersion.md      # 偏振模色散
  249-nonlinear-effects.md                   # 非线性效应
  250-self-phase-modulation.md             # 自相位调制
  251-four-wave-mixing.md                  # 四波混频
  252-fiber-amplifier.md                     # 光纤放大器
  253-raman-amplifier.md                     # 拉曼放大器
  254-fiber-bragg-grating.md               # 光纤布拉格光栅

20-formulas/
  240-fiber-na-formula.md                  # 光纤NA
  241-v-number-formula.md                  # V数
  242-attenuation-formula.md               # 衰减公式
  243-material-dispersion-formula.md       # 材料色散
  244-total-dispersion.md                  # 总色散
  245-intermodal-dispersion-formula.md     # 模间色散
  246-nonlinear-refractive-index.md        # 非线性折射率
  247-edfa-gain.md                         # EDFA增益

40-devices/
  240-smf-device.md                        # 单模光纤
  241-mmf-device.md                        # 多模光纤
  242-edfa.md                              # 掺铒光纤放大器
  243-raman-amplifier-device.md            # 拉曼放大器
  244-optical-isolator.md                  # 光纤隔离器
  245-optical-circulator.md                # 光纤环行器
  246-fiber-coupler.md                     # 光纤耦合器
  247-fbg-device.md                        # 光纤布拉格光栅

50-learning/ （新增章节）
  022-fiber-optics.md                      # 光纤光学基础
```

---

### 3.4 集成光子学（Integrated Photonics）

#### 核心概念（13 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 光波导 | Optical Waveguide | 限制光在特定路径传输的微型结构，基于全内反射 |
| 2 | 倏逝场 | Evanescent Field | 波导芯外指数衰减的光场，用于耦合和传感 |
| 3 | 定向耦合器 | Directional Coupler | 两根靠近波导通过倏逝场交换能量的器件 |
| 4 | 耦合系数 | Coupling Coefficient ($\kappa$) | 描述耦合器间能量交换速率的参数 |
| 5 | Y 分支 / MMI 耦合器 | Y-Branch / MMI Coupler | 基于多模干涉或对称分光的 1×2 或 2×2 光功分器 |
| 6 | 电光调制器 | Electro-Optic Modulator (EOM) | 利用电光效应（Pockels/Kerr）改变折射率实现调制 |
| 7 | 马赫-曾德尔调制器 | Mach-Zehnder Modulator (MZM) | 双臂干涉型电光调制器，广泛用于光通信 |
| 8 | 相位调制器 | Phase Modulator | 仅改变光波相位而不改变振幅的调制器 |
| 9 | 微环谐振器 | Microring Resonator | 环形波导谐振腔，用于滤波、传感、调制 |
| 10 | 自由光谱范围 | Free Spectral Range (FSR) | 相邻谐振峰的频率间隔，$FSR = c / (n_g L)$ |
| 11 | 品质因数 Q | Quality Factor Q | 谐振器储能与损耗比，$Q = \lambda / \Delta\lambda$ |
| 12 | 光子芯片 | Photonic Integrated Circuit (PIC) | 将多种光子器件集成在单芯片上的系统 |
| 13 | 硅光子学 | Silicon Photonics | 利用 CMOS 工艺在硅基上制造光子器件的技术平台 |

#### 核心公式 / 计算模型（7 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 波导模式有效折射率 | $n_{eff} = eta / k_0$ | $eta$ 为传播常数，$k_0 = 2\pi/\lambda$ |
| 2 | 定向耦合器耦合长度 | $L_c = \pi / (2\kappa)$ | 完全功率转移所需长度 |
| 3 | 耦合器输出 | $P_1 = P_0\cos^2(\kappa z)$, $P_2 = P_0\sin^2(\kappa z)$ | 功率交换关系 |
| 4 | MZM 传输函数 | $T = \cos^2(\Delta\phi / 2)$ | $\Delta\phi = \pi V / V_\pi$ |
| 5 | 半波电压 | $V_\pi = \lambda d / (2n^3 r_{33} L)$ | 产生 $\pi$ 相位变化所需电压 |
| 6 | 微环谐振条件 | $m\lambda = n_{eff} \cdot L$ | $m$ 为整数，$L$ 为环周长 |
| 7 | FSR | $FSR = \lambda^2 / (n_g \cdot L)$ | $n_g$ 为群折射率 |

#### 典型设备 / 组件（7 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 硅光波导 | Silicon Waveguide | 硅光子学平台的核心传输元件 |
| 2 | 定向耦合器 | Directional Coupler | 波长选择耦合、功率分路 |
| 3 | MMI 耦合器 | MMI Coupler | 宽带、工艺容差大的多模干涉耦合器 |
| 4 | 马赫-曾德尔调制器 | MZM | 高速电光调制，>100 Gbps 光通信 |
| 5 | 微环谐振器 | Microring Resonator | 窄带滤波、波长选择开关、生物传感 |
| 6 | 光探测器集成芯片 | Photodetector PIC | 集成 Ge-Si 光电探测器 |
| 7 | 可调谐激光器芯片 | Tunable Laser PIC | 集成半导体激光器与微环调谐 |

#### 建议知识库骨架（集成光子学）

```
10-concepts/
  260-optical-waveguide.md                 # 光波导
  261-evanescent-field.md                  # 倏逝场
  262-directional-coupler.md             # 定向耦合器
  263-coupling-coefficient.md              # 耦合系数
  264-mmi-coupler.md                       # MMI耦合器
  265-electro-optic-modulator.md           # 电光调制器
  266-mach-zehnder-modulator.md            # 马赫-曾德尔调制器
  267-phase-modulator.md                   # 相位调制器
  268-microring-resonator.md               # 微环谐振器
  269-free-spectral-range.md               # 自由光谱范围
  270-quality-factor-pic.md                # 品质因数Q（集成光子学）
  271-photonic-integrated-circuit.md       # 光子芯片
  272-silicon-photonics.md                   # 硅光子学

20-formulas/
  260-effective-refractive-index.md        # 有效折射率
  261-coupling-length.md                   # 耦合长度
  262-coupler-output.md                    # 耦合器输出
  263-mzm-transfer-function.md             # MZM传输函数
  264-half-wave-voltage.md                 # 半波电压
  265-microring-resonance.md               # 微环谐振条件
  266-fsr-formula.md                       # FSR公式

40-devices/
  260-silicon-waveguide.md                 # 硅光波导
  261-directional-coupler-device.md        # 定向耦合器
  262-mmi-coupler-device.md                # MMI耦合器
  263-mzm-device.md                        # MZM
  264-microring-resonator-device.md        # 微环谐振器
  265-pd-pic.md                            # 光探测器集成芯片
  266-tunable-laser-pic.md                 # 可调谐激光器芯片

50-learning/ （新增章节）
  023-integrated-photonics.md              # 集成光子学基础
```

---

## 任务 4：光电子与辐射度学核心知识骨架

### 4.1 辐射度学（Radiometry）

辐射度学是客观描述电磁辐射能量传输的学科，不依赖人眼感知，是所有光学工程的基础。

#### 核心概念（12 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 辐射通量 | Radiant Flux ($\Phi_e$) | 单位时间内通过某面积的光辐射功率，单位 W |
| 2 | 辐射强度 | Radiant Intensity ($I_e$) | 单位立体角内的辐射通量，单位 W/sr |
| 3 | 辐射亮度 | Radiance ($L_e$) | 单位面积单位立体角内的辐射通量，单位 W/(m²·sr) |
| 4 | 辐射照度 | Irradiance ($E_e$) | 单位接收面积上的辐射通量，单位 W/m² |
| 5 | 辐射出射度 | Radiant Exitance ($M_e$) | 单位发射面积向半球空间发出的辐射通量，单位 W/m² |
| 6 | 立体角 | Solid Angle ($\Omega$) | 锥面在球心所张的面积与半径平方之比，单位 sr |
| 7 | 朗伯体 | Lambertian Surface | 辐射亮度与观察方向无关的理想漫射表面 |
| 8 | 光学扩展量 | Étendue ($G$) | 面积与立体角（×折射率平方）的乘积，描述系统通光能力 |
| 9 | 辐射度守恒 | Radiance Conservation | 理想无损光学系统中辐射亮度沿光路守恒 |
| 10 | 光谱辐射量 | Spectral Radiometric Quantity | 单位波长间隔内的辐射量（加下标 $/\lambda$） |
| 11 | 双向反射分布函数 | BRDF | 描述表面反射特性的函数，$f_r = dL_r / dE_i$ |
| 12 | 黑体辐射 | Blackbody Radiation | 理想吸收体发射的连续光谱辐射，由普朗克定律描述 |

#### 核心公式 / 计算模型（7 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 立体角 | $d\Omega = \sin	heta \, d	heta \, d\phi$；半球 $\Omega = 2\pi$ | 球面角测量 |
| 2 | 辐射亮度与强度关系 | $L_e = dI_e / (dA \cos	heta)$ | 亮度 = 强度 / (投影面积) |
| 3 | 朗伯体辐射出射度 | $M_e = \pi L_e$ | 朗伯体半球积分 |
| 4 | 照度距离平方反比 | $E_e = I_e / r^2$ | 点源在距离 $r$ 处的照度 |
| 5 | 光学扩展量 | $G = n^2 A \Omega$ | 通光能力度量 |
| 6 | 普朗克黑体辐射定律 | $B(\lambda,T) = rac{2hc^2}{\lambda^5}rac{1}{e^{hc/\lambda kT}-1}$ | 光谱辐射亮度 |
| 7 | 斯特藩-玻尔兹曼定律 | $M = \sigma T^4$ | 总辐射出射度与温度四次方成正比 |

#### 典型设备 / 组件（6 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 辐射计 | Radiometer | 客观测量辐射功率/照度/亮度的仪器 |
| 2 | 光谱辐射计 | Spectroradiometer | 测量光谱分布的辐射度仪器 |
| 3 | 标准黑体炉 | Blackbody Furnace | 产生已知温度下标准黑体辐射的校准源 |
| 4 | 积分球 | Integrating Sphere | 均匀化光源，用于总通量/反射率测量 |
| 5 | 功率计 | Optical Power Meter | 测量激光或光纤输出的绝对功率 |
| 6 | 热释电探测器 | Pyroelectric Detector | 基于温度变化响应的宽带辐射探测器 |

#### 建议知识库骨架（辐射度学）

```
10-concepts/
  300-radiant-flux.md                      # 辐射通量
  301-radiant-intensity.md                 # 辐射强度
  302-radiance.md                          # 辐射亮度
  303-irradiance.md                        # 辐射照度
  304-radiant-exitance.md                  # 辐射出射度
  305-solid-angle.md                       # 立体角
  306-lambertian-surface.md                # 朗伯体
  307-etendue-radiometry.md                # 光学扩展量（辐射度学）
  308-radiance-conservation.md             # 辐射度守恒
  309-spectral-radiometric.md              # 光谱辐射量
  310-brdf.md                              # 双向反射分布函数
  311-blackbody-radiation.md               # 黑体辐射

20-formulas/
  300-solid-angle-formula.md               # 立体角公式
  301-radiance-intensity-relation.md       # 辐射亮度与强度
  302-lambert-exitance.md                  # 朗伯体辐射出射度
  303-inverse-square-radiometry.md         # 距离平方反比
  304-etendue-formula.md                   # 光学扩展量
  305-planck-law.md                        # 普朗克定律
  306-stefan-boltzmann.md                  # 斯特藩-玻尔兹曼定律

40-devices/
  300-radiometer.md                        # 辐射计
  301-spectroradiometer.md                 # 光谱辐射计
  302-blackbody-furnace.md                 # 标准黑体炉
  303-integrating-sphere-radiometry.md     # 积分球（辐射度学应用）
  304-optical-power-meter.md               # 功率计
  305-pyroelectric-detector.md             # 热释电探测器
```

---

### 4.2 光度学（Photometry）

光度学基于人眼视觉感知，是对可见光的辐射度量加上人眼光谱响应的加权。

#### 核心概念（12 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 光通量 | Luminous Flux ($\Phi_v$) | 人眼感知的辐射功率，单位流明（lm） |
| 2 | 发光强度 | Luminous Intensity ($I_v$) | 单位立体角内的光通量，单位坎德拉（cd） |
| 3 | 亮度 | Luminance ($L_v$) | 单位面积单位立体角的光通量，单位 cd/m² |
| 4 | 照度 | Illuminance ($E_v$) | 单位面积接收的光通量，单位勒克斯（lx = lm/m²） |
| 5 | 光出射度 | Luminous Exitance ($M_v$) | 单位面积向半球空间发出的光通量，单位 lm/m² |
| 6 | 光谱光视效率 | Spectral Luminous Efficiency $V(\lambda)$ | 人眼对不同波长光的相对灵敏度，峰值 555 nm |
| 7 | 光视效能 | Luminous Efficacy ($K$) | $K = \Phi_v / \Phi_e$，单位 lm/W，表示电能→光能效率 |
| 8 | 最大光视效能 | Maximum Luminous Efficacy ($K_m$) | 683 lm/W @ 555 nm，人眼最敏感波长 |
| 9 | 流明 | Lumen (lm) | 光通量单位，1 lm = 1 cd·sr |
| 10 | 色温 | Correlated Color Temperature (CCT) | 光源颜色最接近的黑体温度，单位 K |
| 11 | 显色指数 | Color Rendering Index (CRI) | 光源还原物体真实颜色能力的指标，Ra 最高 100 |
| 12 | 光视效率函数 | Photopic / Scotopic Vision | 明视觉（锥细胞，峰值 555 nm）与暗视觉（杆细胞，峰值 507 nm） |

#### 核心公式 / 计算模型（6 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 光通量与辐射通量 | $\Phi_v = K_m \int_{380}^{780} V(\lambda) \Phi_{e,\lambda} d\lambda$ | $V(\lambda)$ 加权积分 |
| 2 | 光视效能 | $K = \Phi_v / \Phi_e$ | 总光通量/总辐射通量 |
| 3 | 亮度与照度（朗伯体） | $L_v = E_v / \pi$（反射面） | 理想漫反射面 |
| 4 | 照度距离定律 | $E_v = I_v / r^2$ | 点光源垂直照度 |
| 5 | 照度余弦定律 | $E_v = I_v \cos	heta / r^2$ | 倾斜入射 |
| 6 | 流明与坎德拉 | $1 	ext{ lm} = 1 	ext{ cd} \cdot 	ext{sr}$ | 基本单位关系 |

#### 典型设备 / 组件（5 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 照度计 | Lux Meter / Illuminance Meter | 测量照度（lx）的便携仪器 |
| 2 | 亮度计 | Luminance Meter | 测量目标面亮度（cd/m²） |
| 3 | 光谱光度计 | Spectrophotometer | 测量光谱反射/透射/吸收率 |
| 4 | 积分球光度计 | Integrating Sphere Photometer | 测量总光通量（lm） |
| 5 | 色度计 | Colorimeter | 测量色度坐标（x, y, z）和色温 |

#### 建议知识库骨架（光度学）

```
10-concepts/
  320-luminous-flux.md                     # 光通量
  321-luminous-intensity.md                # 发光强度
  322-luminance.md                         # 亮度
  323-illuminance.md                       # 照度
  324-luminous-exitance.md                # 光出射度
  325-spectral-luminous-efficiency.md      # 光谱光视效率
  326-luminous-efficacy.md                 # 光视效能
  327-maximum-luminous-efficacy.md         # 最大光视效能
  328-lumen.md                             # 流明
  329-correlated-color-temperature.md      # 色温
  330-cri.md                               # 显色指数
  331-photopic-scotopic.md                 # 明视觉/暗视觉

20-formulas/
  320-luminous-flux-formula.md             # 光通量公式
  321-luminous-efficacy-formula.md         # 光视效能
  322-luminance-illuminance.md             # 亮度与照度
  323-illuminance-distance.md              # 照度距离定律
  324-illuminance-cosine.md                # 照度余弦定律
  325-lumen-candela.md                     # 流明与坎德拉

40-devices/
  320-lux-meter.md                         # 照度计
  321-luminance-meter.md                   # 亮度计
  322-spectrophotometer.md                 # 光谱光度计
  323-integrating-sphere-photometer.md     # 积分球光度计
  324-colorimeter.md                       # 色度计
```

---

### 4.3 光电探测器（Photodetectors）

#### 核心概念（14 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 光电二极管 | Photodiode (PD) | 基于光伏效应将光信号转换为电流的半导体器件 |
| 2 | 量子效率 | Quantum Efficiency (QE) | 每个入射光子产生的电子-空穴对数，$\eta = (I_{ph}/q) / (P_{in}/h
u)$ |
| 3 | 响应度 | Responsivity ($R$) | $R = I_{ph} / P_{in}$，单位 A/W，描述光电转换效率 |
| 4 | 暗电流 | Dark Current | 无光照时探测器中的漏电流，决定噪声下限 |
| 5 | 噪声等效功率 | Noise Equivalent Power (NEP) | 产生信噪比为 1 所需的输入光功率，单位 W/√Hz |
| 6 | 探测率 D* | Detectivity D* | $D^* = \sqrt{A \cdot \Delta f} / NEP$，归一化探测率，单位 cm·√Hz/W |
| 7 | 雪崩光电二极管 | Avalanche Photodiode (APD) | 利用雪崩倍增效应实现内部增益的高灵敏度探测器 |
| 8 | 倍增因子 | Multiplication Factor (M) | APD 中光生载流子的平均倍增倍数 |
| 9 | 光电倍增管 | Photomultiplier Tube (PMT) | 利用二次电子发射实现极高增益（10⁶–10⁸）的真空探测器 |
| 10 | 单光子雪崩二极管 | Single Photon Avalanche Diode (SPAD) | 工作于盖革模式，可探测单个光子的雪崩二极管 |
| 11 | 时间抖动 | Timing Jitter | SPAD/PMT 中光子到达与电脉冲输出的时间不确定性 |
| 12 | 死时间 | Dead Time | 探测器在触发后到恢复灵敏度的最小时间间隔 |
| 13 | 带宽 | Bandwidth | 探测器能响应的最高调制频率，受载流子渡越时间限制 |
| 14 | 噪声等效温差 | NETD | 红外探测器中，产生信噪比为 1 的等效温度差，单位 mK |

#### 核心公式 / 计算模型（8 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | 响应度 | $R = \eta q / (h
u) = \eta \lambda / 1.24$（A/W，$\lambda$ 单位 μm） | 量子效率与波长的关系 |
| 2 | 量子效率 | $\eta = R \cdot h
u / q = R \cdot 1.24 / \lambda$ | 响应度与量子效率换算 |
| 3 | 光电流 | $I_{ph} = R \cdot P_{in}$ | 线性响应区 |
| 4 | NEP | $NEP = i_n / R$ | $i_n$ 为总噪声电流（A/√Hz） |
| 5 | 探测率 D* | $D^* = \sqrt{A \Delta f} / NEP = R / \sqrt{i_n^2 / (A \Delta f)}$ | 归一化探测率 |
| 6 | APD 增益噪声 | $F(M) = M^x$ | $x$ 为过剩噪声指数，Si: 0.3–0.5，InGaAs: 0.5–0.7 |
| 7 | 带宽-增益积 | $BW \cdot M = 	ext{const}$ | APD 的典型约束 |
| 8 | 散粒噪声 | $i_{shot} = \sqrt{2q(I_{ph} + I_{dark})\Delta f}$ | 光电流和暗电流的量子噪声 |

#### 典型设备 / 组件（8 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 硅光电二极管 | Si Photodiode | 可见光-近红外（400–1000 nm），成本低、响应快 |
| 2 | InGaAs 光电二极管 | InGaAs PD | 近红外（900–1700 nm），光通信标准探测器 |
| 3 | 雪崩光电二极管 | APD | 高灵敏度探测，用于长距离光通信和激光雷达 |
| 4 | 光电倍增管 | PMT | 极高增益、极低噪声，用于单光子计数和极弱光探测 |
| 5 | 单光子雪崩二极管 | SPAD | 固态单光子探测，用于量子通信、激光雷达、FLIM |
| 6 | 焦平面阵列 | Focal Plane Array (FPA) | 二维探测器阵列，用于成像（IR FPA、InGaAs FPA） |
| 7 | 碲镉汞探测器 | MCT Detector | 中远红外（3–14 μm）制冷型探测器 |
| 8 | 微测辐射热计 | Microbolometer | 非制冷红外探测器，用于热成像 |

#### 建议知识库骨架（光电探测器）

```
10-concepts/
  340-photodiode.md                        # 光电二极管
  341-quantum-efficiency.md                # 量子效率
  342-responsivity.md                      # 响应度
  343-dark-current.md                      # 暗电流
  344-nep.md                               # 噪声等效功率
  345-detectivity.md                       # 探测率D*
  346-avalanche-photodiode.md              # 雪崩光电二极管
  347-multiplication-factor.md             # 倍增因子
  348-photomultiplier-tube.md              # 光电倍增管
  349-spad.md                              # 单光子雪崩二极管
  350-timing-jitter.md                     # 时间抖动
  351-dead-time.md                         # 死时间
  352-detector-bandwidth.md                # 带宽
  353-netd.md                              # 噪声等效温差（光电探测器语境）

20-formulas/
  340-responsivity-formula.md              # 响应度公式
  341-quantum-efficiency-formula.md        # 量子效率换算
  342-photocurrent-formula.md              # 光电流
  343-nep-formula.md                       # NEP
  344-detectivity-formula.md               # D*
  345-apd-noise-figure.md                  # APD增益噪声
  346-bandwidth-gain-product.md            # 带宽-增益积
  347-shot-noise.md                        # 散粒噪声

40-devices/
  340-si-photodiode.md                     # 硅光电二极管
  341-ingaas-photodiode.md                 # InGaAs光电二极管
  342-apd-device.md                        # 雪崩光电二极管
  343-pmt-device.md                        # 光电倍增管
  344-spad-device.md                         # 单光子雪崩二极管
  345-focal-plane-array.md                 # 焦平面阵列
  346-mct-detector.md                      # 碲镉汞探测器
  347-microbolometer.md                    # 微测辐射热计
```

---

### 4.4 光调制（Optical Modulation）

#### 核心概念（12 个）

| # | 中文术语 | 英文术语 | 一句话定义 |
|---|---------|---------|-----------|
| 1 | 电光效应 | Electro-Optic Effect | 外加电场改变材料折射率的现象，分 Pockels（线性）和 Kerr（二次）效应 |
| 2 | 泡克尔斯效应 | Pockels Effect | 线性电光效应，$\Delta n = rac{1}{2}n^3 r_{63} E$ |
| 3 | 克尔效应 | Kerr Effect | 二次电光效应，$\Delta n = n_2 I + \lambda K E^2$ |
| 4 | 声光效应 | Acousto-Optic Effect | 声波在介质中引起折射率周期性变化，形成可移动光栅 |
| 5 | 磁光效应 | Magneto-Optic Effect | 磁场引起材料光学性质变化，如法拉第旋转 |
| 6 | 法拉第旋转 | Faraday Rotation | 线偏振光在磁场中沿传播方向旋转偏振面的现象 |
| 7 | 相位调制 | Phase Modulation | 仅改变光波相位，载波信息在相位中 |
| 8 | 振幅调制 | Amplitude Modulation | 改变光波振幅（强度），如 MZM 偏置在正交点 |
| 9 | 强度调制 | Intensity Modulation | 直接调制光源电流或外调制器改变光强 |
| 10 | 频率调制 | Frequency Modulation | 改变光载波频率，用于相干光通信 |
| 11 | 半波电压 | Half-Wave Voltage ($V_\pi$) | 产生 $\pi$ 相位调制所需的电压 |
| 12 | 调制带宽 | Modulation Bandwidth | 调制器能响应的最高频率，受 RC 常数或渡越时间限制 |

#### 核心公式 / 计算模型（7 个）

| # | 公式名称 | 表达式 | 说明 |
|---|---------|--------|------|
| 1 | Pockels 相位调制 | $\Delta\phi = rac{2\pi}{\lambda} n^3 r_{eff} rac{V}{d} L$ | $V$ 为电压，$d$ 为电极间距，$L$ 为作用长度 |
| 2 | 半波电压 | $V_\pi = rac{\lambda d}{2 n^3 r_{eff} L}$ | 产生 $\pi$ 相移的电压 |
| 3 | MZM 强度调制 | $T = \cos^2(rac{\pi V}{2V_\pi})$ | 推挽 MZM 传输函数 |
| 4 | 声光衍射效率 | $\eta = \sin^2(rac{\pi}{\lambda}\sqrt{rac{M_2 P_a L}{2H}})$ | $M_2$ 为声光优值，$P_a$ 为声功率 |
| 5 | 法拉第旋转角 | $	heta = V B L$ | $V$ 为维尔德常数，$B$ 为磁场，$L$ 为作用长度 |
| 6 | 电光调制带宽 | $f_{3dB} = 1 / (2\pi RC)$ | 受电极电容和匹配电阻限制 |
| 7 | 行波调制器带宽 | $f_{3dB} = 1 / (2\pi 	au_{mismatch})$ | 受微波-光波速度匹配限制 |

#### 典型设备 / 组件（6 个）

| # | 中文名称 | 英文名称 | 功能说明 |
|---|---------|---------|---------|
| 1 | 铌酸锂电光调制器 | LiNbO₃ EOM | 最常用的宽带电光调制器，用于高速光通信 |
| 2 | 电吸收调制器 | Electro-Absorption Modulator (EAM) | 基于量子限制 Stark 效应，可集成激光器 |
| 3 | 声光调制器 | Acousto-Optic Modulator (AOM) | 用于光束偏转、Q 开关、频移 |
| 4 | 磁光调制器 | Magneto-Optic Modulator | 基于法拉第效应，用于光隔离器和调制 |
| 5 | 空间光调制器 | Spatial Light Modulator (SLM) | 二维相位/振幅调制，用于全息、光计算 |
| 6 | 微机电光调制器 | MEMS Optical Modulator | 利用微镜机械运动调制光，用于投影显示 |

#### 建议知识库骨架（光调制）

```
10-concepts/
  360-electro-optic-effect.md              # 电光效应
  361-pockels-effect.md                    # 泡克尔斯效应
  362-kerr-effect.md                       # 克尔效应
  363-acousto-optic-effect.md              # 声光效应
  364-magneto-optic-effect.md              # 磁光效应
  365-faraday-rotation.md                  # 法拉第旋转
  366-phase-modulation.md                  # 相位调制
  367-amplitude-modulation.md              # 振幅调制
  368-intensity-modulation.md              # 强度调制
  369-frequency-modulation.md              # 频率调制
  370-half-wave-voltage-modulator.md       # 半波电压
  371-modulation-bandwidth.md              # 调制带宽

20-formulas/
  360-pockels-phase-modulation.md          # Pockels相位调制
  361-half-wave-voltage-formula.md         # 半波电压
  362-mzm-transmission-modulation.md       # MZM强度调制
  363-acousto-optic-diffraction.md         # 声光衍射效率
  364-faraday-rotation-angle.md            # 法拉第旋转角
  365-eo-modulation-bandwidth.md           # 电光调制带宽
  366-traveling-wave-bandwidth.md          # 行波调制器带宽

40-devices/
  360-linbo3-modulator.md                  # 铌酸锂电光调制器
  361-electro-absorption-modulator.md      # 电吸收调制器
  362-aom-device.md                        # 声光调制器
  363-magneto-optic-modulator.md         # 磁光调制器
  364-spatial-light-modulator.md           # 空间光调制器
  365-mems-optical-modulator.md            # 微机电光调制器
```

---

## 建议的知识库扩展目录树（具体到文件级别）

基于现有 `OpticKnowledgeSpace` 的编号体系（10-concepts/ 以 000-099 为成像保留，100 起为非成像），建议新增目录结构如下：

```
OpticKnowledgeSpace/
│
├── 10-concepts/                          # 现有概念层（扩展）
│   ├── 000-099/                          # 现有成像+通用概念（保留不变）
│   ├── 100-etendue.md                    # 光学扩展量
│   ├── 101-luminous-flux.md              # 光通量/辐射通量
│   ├── 102-luminance.md                  # 亮度
│   ├── 103-illuminance.md              # 照度
│   ├── 104-intensity-distribution-curve.md # 配光曲线
│   ├── 105-light-extraction-efficiency.md # LED光提取效率
│   ├── 106-uniformity.md                 # 均匀性
│   ├── 107-lambertian-emitter.md        # 朗伯体
│   ├── 108-freeform-surface.md          # 自由曲面
│   ├── 109-light-coupling.md             # 光线耦合
│   ├── 110-optical-efficiency.md         # 光学效率
│   ├── 111-monte-carlo-ray-tracing.md    # 蒙特卡洛光线追迹
│   ├── 120-cpc-concentrator.md           # 复合抛物面聚光器
│   ├── 121-concentration-ratio.md        # 聚光比
│   ├── 122-acceptance-angle.md           # 接受角
│   ├── 123-geometric-concentration.md    # 几何聚光比
│   ├── 124-flux-mapping.md               # 光通量映射
│   ├── 125-edge-ray-principle.md         # 边缘光线原理
│   ├── 126-truncation.md                 # 截断
│   ├── 127-fresnel-lens.md               # 菲涅尔透镜
│   ├── 128-secondary-concentrator.md     # 二次反射聚光器
│   ├── 129-hot-spot-effect.md             # 热斑效应
│   ├── 130-solar-tracking.md              # 太阳跟踪
│   ├── 140-backlight-unit.md             # 背光模组
│   ├── 141-light-guide-plate.md          # 导光板
│   ├── 142-microlens-array-display.md    # 微透镜阵列（显示）
│   ├── 143-diffusion-film.md             # 扩散膜
│   ├── 144-brightness-enhancement-film.md # 增亮膜 BEF
│   ├── 145-reflective-polarizer.md       # 反射型偏振增亮膜 DBEF
│   ├── 146-total-internal-reflection-display.md # 全内反射（显示）
│   ├── 147-dot-pattern.md                # 网点/散射点
│   ├── 148-color-gamut.md                # 色域
│   ├── 149-luminance-uniformity.md       # 亮度均匀性
│   ├── 150-viewing-angle.md              # 视角特性
│   ├── 151-local-dimming.md              # 局部调光
│   ├── 152-mini-led-backlight.md         # Mini-LED背光
│   ├── 160-coupling-efficiency.md        # 耦合效率
│   ├── 161-mode-matching.md              # 模式匹配
│   ├── 162-fiber-na.md                   # 光纤数值孔径
│   ├── 163-mode-field-diameter.md        # 模场直径
│   ├── 164-butt-coupling-loss.md         # 对接损耗
│   ├── 165-lateral-misalignment.md       # 横向失准
│   ├── 166-angular-misalignment.md       # 角度失准
│   ├── 167-gap-loss.md                   # 轴向间隙损耗
│   ├── 168-lens-coupling.md              # 透镜耦合
│   ├── 169-fiber-splicing.md             # 光纤熔接
│   ├── 200-stimulated-emission.md        # 受激辐射
│   ├── 201-population-inversion.md       # 粒子数反转
│   ├── 202-optical-resonator.md          # 光学谐振腔
│   ├── 203-gain-medium.md                # 增益介质
│   ├── 204-pumping.md                    # 泵浦
│   ├── 205-laser-threshold.md             # 激光阈值
│   ├── 206-longitudinal-mode.md          # 纵模
│   ├── 207-transverse-mode.md             # 横模
│   ├── 208-quality-factor.md             # 品质因数Q
│   ├── 209-q-switching.md                # Q开关
│   ├── 210-mode-locking.md               # 锁模
│   ├── 211-cavity-dumping.md             # 腔倒空
│   ├── 212-slope-efficiency.md           # 斜率效率
│   ├── 213-beam-quality.md               # 光束质量
│   ├── 214-coherence-length.md           # 相干长度
│   ├── 220-gaussian-beam.md              # 高斯光束
│   ├── 221-beam-waist.md                 # 束腰
│   ├── 222-rayleigh-range.md             # 瑞利范围
│   ├── 223-beam-divergence.md            # 光束发散角
│   ├── 224-m2-factor.md                # 光束质量因子M²
│   ├── 225-beam-parameter-product.md     # 光束参数乘积
│   ├── 226-focused-spot.md               # 聚焦光斑
│   ├── 227-depth-of-focus.md             # 焦深
│   ├── 228-gouy-phase.md                 # Gouy相位
│   ├── 229-gaussian-focus-shift.md       # 高斯焦移
│   ├── 230-near-far-field.md             # 近场/远场
│   ├── 231-beam-shaping.md               # 光束整形
│   ├── 240-single-mode-fiber.md          # 单模光纤
│   ├── 241-multi-mode-fiber.md           # 多模光纤
│   ├── 242-fiber-numerical-aperture.md   # 光纤数值孔径
│   ├── 243-v-number.md                   # 归一化频率
│   ├── 244-attenuation.md                # 衰减
│   ├── 245-material-dispersion.md        # 材料色散
│   ├── 246-waveguide-dispersion.md       # 波导色散
│   ├── 247-intermodal-dispersion.md      # 模间色散
│   ├── 248-polarization-mode-dispersion.md # 偏振模色散
│   ├── 249-nonlinear-effects.md          # 非线性效应
│   ├── 250-self-phase-modulation.md      # 自相位调制
│   ├── 251-four-wave-mixing.md           # 四波混频
│   ├── 252-fiber-amplifier.md            # 光纤放大器
│   ├── 253-raman-amplifier.md            # 拉曼放大器
│   ├── 254-fiber-bragg-grating.md        # 光纤布拉格光栅
│   ├── 260-optical-waveguide.md          # 光波导
│   ├── 261-evanescent-field.md           # 倏逝场
│   ├── 262-directional-coupler.md        # 定向耦合器
│   ├── 263-coupling-coefficient.md       # 耦合系数
│   ├── 264-mmi-coupler.md                # MMI耦合器
│   ├── 265-electro-optic-modulator.md    # 电光调制器
│   ├── 266-mach-zehnder-modulator.md     # 马赫-曾德尔调制器
│   ├── 267-phase-modulator.md            # 相位调制器
│   ├── 268-microring-resonator.md        # 微环谐振器
│   ├── 269-free-spectral-range.md        # 自由光谱范围
│   ├── 270-quality-factor-pic.md         # 品质因数Q（PIC）
│   ├── 271-photonic-integrated-circuit.md # 光子芯片
│   ├── 272-silicon-photonics.md          # 硅光子学
│   ├── 300-radiant-flux.md               # 辐射通量
│   ├── 301-radiant-intensity.md          # 辐射强度
│   ├── 302-radiance.md                   # 辐射亮度
│   ├── 303-irradiance.md                 # 辐射照度
│   ├── 304-radiant-exitance.md           # 辐射出射度
│   ├── 305-solid-angle.md                # 立体角
│   ├── 306-lambertian-surface.md         # 朗伯体
│   ├── 307-etendue-radiometry.md         # 光学扩展量（辐射度学）
│   ├── 308-radiance-conservation.md      # 辐射度守恒
│   ├── 309-spectral-radiometric.md       # 光谱辐射量
│   ├── 310-brdf.md                       # 双向反射分布函数
│   ├── 311-blackbody-radiation.md          # 黑体辐射
│   ├── 320-luminous-flux.md              # 光通量
│   ├── 321-luminous-intensity.md         # 发光强度
│   ├── 322-luminance.md                  # 亮度
│   ├── 323-illuminance.md                # 照度
│   ├── 324-luminous-exitance.md          # 光出射度
│   ├── 325-spectral-luminous-efficiency.md # 光谱光视效率
│   ├── 326-luminous-efficacy.md          # 光视效能
│   ├── 327-maximum-luminous-efficacy.md  # 最大光视效能
│   ├── 328-lumen.md                      # 流明
│   ├── 329-correlated-color-temperature.md # 色温
│   ├── 330-cri.md                        # 显色指数
│   ├── 331-photopic-scotopic.md          # 明视觉/暗视觉
│   ├── 340-photodiode.md                 # 光电二极管
│   ├── 341-quantum-efficiency.md         # 量子效率
│   ├── 342-responsivity.md               # 响应度
│   ├── 343-dark-current.md               # 暗电流
│   ├── 344-nep.md                        # 噪声等效功率
│   ├── 345-detectivity.md                # 探测率D*
│   ├── 346-avalanche-photodiode.md       # 雪崩光电二极管
│   ├── 347-multiplication-factor.md      # 倍增因子
│   ├── 348-photomultiplier-tube.md       # 光电倍增管
│   ├── 349-spad.md                       # 单光子雪崩二极管
│   ├── 350-timing-jitter.md              # 时间抖动
│   ├── 351-dead-time.md                  # 死时间
│   ├── 352-detector-bandwidth.md         # 带宽
│   ├── 360-electro-optic-effect.md       # 电光效应
│   ├── 361-pockels-effect.md             # 泡克尔斯效应
│   ├── 362-kerr-effect.md                # 克尔效应
│   ├── 363-acousto-optic-effect.md       # 声光效应
│   ├── 364-magneto-optic-effect.md       # 磁光效应
│   ├── 365-faraday-rotation.md           # 法拉第旋转
│   ├── 366-phase-modulation.md           # 相位调制
│   ├── 367-amplitude-modulation.md       # 振幅调制
│   ├── 368-intensity-modulation.md       # 强度调制
│   ├── 369-frequency-modulation.md       # 频率调制
│   ├── 370-half-wave-voltage-modulator.md # 半波电压
│   └── 371-modulation-bandwidth.md       # 调制带宽
│
├── 20-formulas/                          # 现有公式层（扩展）
│   ├── 100-199/                          # 现有公式（保留）
│   ├── 100-etendue-conservation.md
│   ├── 101-lambert-cosine-law.md
│   ├── 102-inverse-square-law.md
│   ├── 103-uniformity-metrics.md
│   ├── 104-led-extraction-efficiency.md
│   ├── 105-freeform-mapping-equation.md
│   ├── 106-optical-efficiency-limit.md
│   ├── 107-lumen-calculation.md
│   ├── 120-cpc-concentration-ratio.md
│   ├── 121-3d-concentration-limit.md
│   ├── 122-optical-efficiency-concentrator.md
│   ├── 123-fresnel-lens-design.md
│   ├── 124-cpc-profile-equation.md
│   ├── 125-thermal-balance.md
│   ├── 126-annual-energy-gain.md
│   ├── 140-tir-critical-angle.md
│   ├── 141-dot-density-distribution.md
│   ├── 142-bef-gain.md
│   ├── 143-color-gamut-ratio.md
│   ├── 144-luminance-uniformity-formula.md
│   ├── 145-optical-efficiency-blu.md
│   ├── 160-fiber-na-formula.md
│   ├── 161-acceptance-angle.md
│   ├── 162-gaussian-coupling-efficiency.md
│   ├── 163-lateral-loss-formula.md
│   ├── 164-angular-loss-formula.md
│   ├── 165-fresnel-reflection-loss.md
│   ├── 200-laser-threshold-condition.md
│   ├── 201-output-coupling.md
│   ├── 202-slope-efficiency-formula.md
│   ├── 203-longitudinal-mode-frequency.md
│   ├── 204-finesse-formula.md
│   ├── 205-q-value.md
│   ├── 206-mode-locked-pulse-width.md
│   ├── 207-population-inversion-density.md
│   ├── 220-gaussian-beam-radius.md
│   ├── 221-rayleigh-range-formula.md
│   ├── 222-divergence-ideal.md
│   ├── 223-divergence-real.md
│   ├── 224-m2-factor-formula.md
│   ├── 225-focused-spot-radius.md
│   ├── 226-depth-of-focus-formula.md
│   ├── 227-gouy-phase-formula.md
│   ├── 240-fiber-na-formula.md
│   ├── 241-v-number-formula.md
│   ├── 242-attenuation-formula.md
│   ├── 243-material-dispersion-formula.md
│   ├── 244-total-dispersion.md
│   ├── 245-intermodal-dispersion-formula.md
│   ├── 246-nonlinear-refractive-index.md
│   ├── 247-edfa-gain.md
│   ├── 260-effective-refractive-index.md
│   ├── 261-coupling-length.md
│   ├── 262-coupler-output.md
│   ├── 263-mzm-transfer-function.md
│   ├── 264-half-wave-voltage.md
│   ├── 265-microring-resonance.md
│   ├── 266-fsr-formula.md
│   ├── 300-solid-angle-formula.md
│   ├── 301-radiance-intensity-relation.md
│   ├── 302-lambert-exitance.md
│   ├── 303-inverse-square-radiometry.md
│   ├── 304-etendue-formula.md
│   ├── 305-planck-law.md
│   ├── 306-stefan-boltzmann.md
│   ├── 320-luminous-flux-formula.md
│   ├── 321-luminous-efficacy-formula.md
│   ├── 322-luminance-illuminance.md
│   ├── 323-illuminance-distance.md
│   ├── 324-illuminance-cosine.md
│   ├── 325-lumen-candela.md
│   ├── 340-responsivity-formula.md
│   ├── 341-quantum-efficiency-formula.md
│   ├── 342-photocurrent-formula.md
│   ├── 343-nep-formula.md
│   ├── 344-detectivity-formula.md
│   ├── 345-apd-noise-figure.md
│   ├── 346-bandwidth-gain-product.md
│   ├── 347-shot-noise.md
│   ├── 360-pockels-phase-modulation.md
│   ├── 361-half-wave-voltage-formula.md
│   ├── 362-mzm-transmission-modulation.md
│   ├── 363-acousto-optic-diffraction.md
│   ├── 364-faraday-rotation-angle.md
│   ├── 365-eo-modulation-bandwidth.md
│   └── 366-traveling-wave-bandwidth.md
│
├── 30-domains/                           # 现有领域层（扩展）
│   ├── 006-illumination-design.md         # 照明设计（非成像）
│   ├── 007-solar-energy.md               # 太阳能光热/光伏
│   ├── 008-display-technology.md         # 显示技术
│   ├── 009-optical-communication.md      # 光通信
│   ├── 010-laser-material-processing.md  # 激光材料加工
│   ├── 011-biomedical-photonics.md       # 生物医学光子学
│   └── 012-quantum-optics.md             # 量子光学
│
├── 40-devices/                           # 现有设备层（扩展）
│   ├── 100-199/                          # 现有设备（保留）
│   ├── 100-led-source.md
│   ├── 101-freeform-lens.md
│   ├── 102-reflector-cup.md
│   ├── 103-light-pipe.md
│   ├── 104-integrating-rod.md
│   ├── 105-microlens-array.md
│   ├── 106-diffuser-plate.md
│   ├── 107-collimator-lens.md
│   ├── 120-cpc-concentrator.md
│   ├── 121-fresnel-concentrator.md
│   ├── 122-parabolic-trough.md
│   ├── 123-heliostat.md
│   ├── 124-solar-receiver.md
│   ├── 125-solar-tracker.md
│   ├── 140-edge-lit-blu.md
│   ├── 141-direct-lit-blu.md
│   ├── 142-light-guide-plate-device.md
│   ├── 143-bef-film.md
│   ├── 144-dbef-film.md
│   ├── 145-diffuser-film.md
│   ├── 146-reflective-sheet.md
│   ├── 160-fiber-connector.md
│   ├── 161-fusion-splicer.md
│   ├── 162-fiber-coupling-lens.md
│   ├── 163-fiber-adapter.md
│   ├── 164-alignment-stage.md
│   ├── 200-laser-diode.md
│   ├── 201-solid-state-laser.md
│   ├── 202-fiber-laser.md
│   ├── 203-gas-laser.md
│   ├── 204-electro-optic-modulator.md
│   ├── 205-acousto-optic-modulator.md
│   ├── 206-saturable-absorber.md
│   ├── 207-laser-power-supply.md
│   ├── 220-beam-quality-analyzer.md
│   ├── 221-scanning-slit-profiler.md
│   ├── 222-ccd-beam-profiler.md
│   ├── 223-beam-expander.md
│   ├── 224-focusing-lens.md
│   ├── 225-spatial-filter.md
│   ├── 240-smf-device.md
│   ├── 241-mmf-device.md
│   ├── 242-edfa.md
│   ├── 243-raman-amplifier-device.md
│   ├── 244-optical-isolator.md
│   ├── 245-optical-circulator.md
│   ├── 246-fiber-coupler.md
│   ├── 247-fbg-device.md
│   ├── 260-silicon-waveguide.md
│   ├── 261-directional-coupler-device.md
│   ├── 262-mmi-coupler-device.md
│   ├── 263-mzm-device.md
│   ├── 264-microring-resonator-device.md
│   ├── 265-pd-pic.md
│   ├── 266-tunable-laser-pic.md
│   ├── 300-radiometer.md
│   ├── 301-spectroradiometer.md
│   ├── 302-blackbody-furnace.md
│   ├── 303-integrating-sphere-radiometry.md
│   ├── 304-optical-power-meter.md
│   ├── 305-pyroelectric-detector.md
│   ├── 320-lux-meter.md
│   ├── 321-luminance-meter.md
│   ├── 322-spectrophotometer.md
│   ├── 323-integrating-sphere-photometer.md
│   ├── 324-colorimeter.md
│   ├── 340-si-photodiode.md
│   ├── 341-ingaas-photodiode.md
│   ├── 342-apd-device.md
│   ├── 343-pmt-device.md
│   ├── 344-spad-device.md
│   ├── 345-focal-plane-array.md
│   ├── 346-mct-detector.md
│   ├── 347-microbolometer.md
│   ├── 360-linbo3-modulator.md
│   ├── 361-electro-absorption-modulator.md
│   ├── 362-aom-device.md
│   ├── 363-magneto-optic-modulator.md
│   ├── 364-spatial-light-modulator.md
│   └── 365-mems-optical-modulator.md
│
├── 50-learning/                          # 现有学习层（扩展）
│   ├── 000-016/                          # 现有章节（保留）
│   ├── 017-illumination-design-nonimaging.md
│   ├── 018-solar-concentrator-design.md
│   ├── 019-display-optics.md
│   ├── 020-optical-communication-coupling.md
│   ├── 021-laser-principles.md
│   ├── 022-fiber-optics.md
│   ├── 023-integrated-photonics.md
│   ├── 024-radiometry-photometry.md
│   ├── 025-photodetectors.md
│   └── 026-optical-modulation.md
│
├── modules/                              # 新增模块（与现有五模块平行）
│   ├── 60-nonimaging-optics/             # 模块己｜非成像光学与辐射度学
│   │   ├── README.md
│   │   ├── concepts.md
│   │   ├── formulas.md
│   │   ├── 00-core-content/
│   │   │   ├── 01-illumination-design.md
│   │   │   ├── 02-solar-concentrator.md
│   │   │   ├── 03-display-backlight.md
│   │   │   └── 04-radiometry-photometry.md
│   │   ├── projects/
│   │   └── assessment/
│   ├── 70-laser-fiber/                   # 模块庚｜激光光学与光纤通信
│   │   ├── README.md
│   │   ├── concepts.md
│   │   ├── formulas.md
│   │   ├── 00-core-content/
│   │   │   ├── 01-laser-principles.md
│   │   │   ├── 02-gaussian-beam.md
│   │   │   ├── 03-fiber-optics.md
│   │   │   └── 04-optical-communication.md
│   │   ├── projects/
│   │   └── assessment/
│   └── 80-optoelectronics/               # 模块辛｜光电子学与光电探测
│       ├── README.md
│       ├── concepts.md
│       ├── formulas.md
│       ├── 00-core-content/
│       │   ├── 01-integrated-photonics.md
│       │   ├── 02-photodetectors.md
│       │   ├── 03-optical-modulation.md
│       │   └── 04-optoelectronic-systems.md
│       ├── projects/
│       └── assessment/
│
└── 90-maps/                              # 知识地图更新
    ├── 009-Nonimaging Optics Topic.md     # 非成像光学专题地图
    ├── 010-Laser and Photonics Topic.md   # 激光与光子学专题地图
    └── 011-Optoelectronics Topic.md       # 光电子学专题地图
```

---

## 与现有 v4.0 五模块结构的融合建议

### 融合原则

1. **不破坏现有五模块**：现有 `modules/10-foundations/` 到 `modules/50-optical-design/` 的成像光学微专业体系是知识库的核心资产，完全保留。
2. **通用基础跨模块共享**：将现有 53 个通用基础文件从单模块归属改为"多模块共享"，在新增模块的 `concepts.md` 和 `formulas.md` 中通过 Obsidian 双链引用，而非物理移动文件。
3. **新增模块作为平行扩展**：新增模块（己、庚、辛）与现有五模块平行，形成"成像五模块 + 非成像三模块"的完整光学体系。
4. **光谱学作为桥梁**：现有 `modules/40-spectroscopy/`（模块丁）是成像与非成像的最佳桥梁，可在其基础上向辐射度学（模块己）自然延伸。

### 具体融合方案

| 现有模块 | 现有内容 | 新增非成像内容 | 融合方式 |
|---------|---------|--------------|---------|
| **模块甲｜桥接** | 折射率、波长、薄透镜、基本术语 | 增加"光学扩展量"直觉、"辐射度学最小术语集" | 在 `10-foundations/concepts.md` 中新增指向 `100-etendue` 的链接，扩展"术语最小集" |
| **模块乙｜几何光学** | 光线追迹、近轴、成像、像差、照明几何 | 增加"非成像光线追迹"（照明、聚光）、"边缘光线原理" | 将 `13a-illumination-geometry` 扩展为"照明设计（成像+非成像）"双轨 |
| **模块丙｜波动光学** | 干涉、衍射、PSF/OTF/MTF、傅里叶 | 增加"激光光束传播"、"光纤模式理论"、"倏逝场" | 在 `30-wave-optics/concepts.md` 中新增激光高斯光束、光纤模式作为"波动光学在非成像中的应用" |
| **模块丁｜光谱学** | 色散、光栅、光谱仪、分辨率 | 增加"辐射度学基础"、"光谱辐射度测量"、"积分球绝对测量" | 将光谱学从"成像光谱"扩展为"光谱测量与辐射度学"，自然过渡到模块己 |
| **模块戊｜光学设计** | 设计闭环、像质评价、优化、容差 | 增加"照明系统设计（非成像）"、"激光光学设计"、"耦合光学设计" | 新增设计专题页，说明成像设计与非成像设计的差异（目标函数不同） |
| **模块己｜非成像光学与辐射度学** | **新建** | 照明设计、太阳能聚光、显示光学、辐射度学、光度学 | 新建模块，先修模块甲+乙，与模块丁可并行 |
| **模块庚｜激光光学与光纤通信** | **新建** | 激光器原理、高斯光束、光纤光学、光通信耦合 | 新建模块，先修模块丙（波动光学），与模块戊可并行 |
| **模块辛｜光电子学与光电探测** | **新建** | 集成光子学、光电探测器、光调制、光电子系统 | 新建模块，先修模块庚（光纤光学）+ 模块己（辐射度学） |

### 双链融合示例

在新增模块的 README 中，应建立如下跨模块链接：

```markdown
## 与本模块相关的前置知识

- [[modules/10-foundations/README|模块甲｜桥接]] — 基础术语与单位
- [[modules/20-geometric-optics/README|模块乙｜几何光学]] — 光线追迹、NA、F值（重新标注为非成像通用）
- [[modules/30-wave-optics/README|模块丙｜波动光学]] — 干涉、衍射、相干长度
- [[modules/40-spectroscopy/README|模块丁｜光谱学]] — 色散、光谱分辨率（向辐射度学延伸）

## 跨模块共享概念

- [[10-concepts/006-数值孔径|数值孔径]] — 在光纤、聚光器、LED光提取中的非成像应用
- [[10-concepts/050-polarization|偏振]] — 在电光调制、液晶显示、光纤通信中的扩展
- [[10-concepts/025-diffraction-limit|衍射极限]] — 在激光聚焦、光刻、CPC中的通用性
- [[10-concepts/064-发射率|发射率]] — 从红外成像向辐射度学的迁移
- [[10-concepts/021-干涉|干涉]] — 在激光器谐振腔、光纤干涉仪、集成光子学中的应用
```

### 建议的重新标注文件清单

以下现有文件建议通过 `aliases` 或 `domains` frontmatter 字段增加"非成像"标签，使其在 Obsidian 图谱中可见于多个模块：

```yaml
# 以 10-concepts/006-数值孔径.md 为例
---
id: concepts.numerical-aperture
title: 数值孔径
type: concept
domains: [imaging, fiber-optics, illumination, solar-concentrator]  # 新增非成像 domain
status: reviewed
aliases:
  - 数值孔径
  - NA
---
```

| 文件 | 建议新增 domains |
|------|---------------|
| `10-concepts/006-数值孔径` | `fiber-optics`, `illumination`, `solar-concentrator` |
| `10-concepts/050-polarization` | `display`, `electro-optic-modulation`, `fiber-communication` |
| `10-concepts/016-abbe-number` / `017-色散` | `fiber-optics`, `laser-optics` |
| `10-concepts/025-衍射极限` | `laser-optics`, `lithography`, `solar-concentrator` |
| `10-concepts/038-nyquist-frequency` | `optoelectronics`, `optical-communication` |
| `10-concepts/064-发射率` | `radiometry`, `thermal-detection` |
| `10-concepts/049-分光镜` | `fiber-coupler`, `interferometer` |
| `10-concepts/021-干涉` | `laser-cavity`, `fiber-sensor`, `integrated-photonics` |
| `20-formulas/015-planck-blackbody` | `radiometry`, `infrared-detection` |
| `20-formulas/012-grating-equation` | `laser-wavelength-selection`, `fiber-communication` |
| `40-devices/014-integrating-sphere` | `radiometry`, `led-measurement` |

---

## 附录：参考来源

| 领域 | 核心教材 / 参考 |
|------|----------------|
| 非成像光学 | Winston, Minano & Benitez,《Nonimaging Optics》(Elsevier, 2005) |
| 照明设计 | Cassarly,《Illumination Design: From Concepts to Implementation》(SPIE) |
| 太阳能聚光 | Rabl,《Active Solar Collectors and Their Applications》(Oxford, 1985) |
| 激光光学 | Siegman,《Lasers》(University Science Books, 1986) |
| 光纤光学 | Saleh & Teich,《Fundamentals of Photonics》(3rd ed., Wiley) — 知识库已有索引 |
| 集成光子学 | Reed & Knights,《Silicon Photonics》(Wiley) |
| 辐射度学 | Boyd,《Radiometry and the Detection of Optical Radiation》(Wiley) |
| 光电探测器 | Dereniak & Boreman,《Infrared Detectors and Systems》(Wiley) |
| 光调制 | Yariv & Yeh,《Photonics》(Oxford, 2007) |
| 显示光学 | Chen, Cranton & Fihn,《Handbook of Visual Display Technology》(Springer) |
