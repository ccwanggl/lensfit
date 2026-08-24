# OptiBench 光学知识库扩展规划研究报告：非成像、激光、光电子与辐射度学

---

## 1. 执行摘要

OptiBench 知识库当前拥有约 **134 个核心文件**（88 个概念、22 个公式、6 个领域、18 个设备），其中 **超过 70% 的内容高度聚焦成像光学**（镜头、传感器、像质评价、机器视觉）。本报告通过对现有知识资产的深度审计，识别出约 40 个可重新标注为"通用基础"的概念/公式，并系统构建了 **非成像光学、激光光学与光子学、光电子与辐射度学** 三大新增领域的核心知识骨架。建议将现有 v4.0 五模块环形结构扩展为 **七模块体系**：在保留模块甲~戊的基础上，新增 **模块己｜激光与光子学** 和 **模块庚｜辐射度学与光电子**，同时将非成像光学内容作为跨模块通用资源与专用分支融入现有架构。报告包含具体的目录树、文件命名规范和双链集成建议，可直接作为知识库扩展的路线图使用。

---

## 2. 任务 1：现有成像光学偏向性深度分析

### 2.1 文件分类统计

对 `OpticKnowledgeSpace` 核心知识资产（`10-concepts/`、`20-formulas/`、`30-domains/`、`40-devices/`）的 134 个文件进行四象限分类：

| 类别 | 定义 | 文件数量 | 占比 | 代表性文件 |
|------|------|---------|------|-----------|
| **【纯成像光学】** | 仅在成像系统（摄影、显微镜、工业视觉、红外热像）中有明确意义，非成像领域几乎不使用的概念/设备/公式 | **93** | **69.4%** | PSF、OTF、MTF、像圈、视场、景深、像素、全局快门、C-mount 镜头、远心镜头、高光谱相机 |
| **【通用基础】** | 在成像、非成像、激光、光通信、照明、光谱等多个光学子领域均有核心应用 | **31** | **23.1%** | 折射率、波长、干涉、衍射光栅、偏振、色散、斯涅尔定律、光栅方程、普朗克黑体辐射、光谱功率分布 |
| **【已覆盖非成像】** | 当前知识库已涉及但仅作为成像系统附属或边缘主题的非成像内容 | **6** | **4.5%** | 光谱仪（模块丁）、积分球（校准）、衍射光栅（光谱色散）、带通滤光片、荧光、拉曼散射 |
| **【未覆盖】** | 完全缺失的非成像光学、激光光学、辐射度学、光电子学核心内容 | **4 大类** | **N/A** | 激光谐振腔、高斯光束、光纤放大器、波导、辐射通量、光电二极管、电光效应等（约 200+ 个潜在概念） |

> **统计口径**：不含 `README.md`、MOC 索引、学习章节（`50-learning/`）和重构规划文件。公式与概念的中英双语 stub 分别计数。

### 2.2 成像光学独占的核心概念及跨领域应用缺口

以下概念在现有知识库中被**严格限定于成像语境**，但它们在非成像领域同样具有核心地位，知识库未覆盖其跨领域应用：

| 成像独占概念 | 当前知识库定位 | 在非成像/激光/光电子领域的应用 | 覆盖缺口 |
|-------------|--------------|------------------------------|---------|
| **MTF / 调制传递函数** | 镜头-传感器像质评价 | 激光光束质量评价（类比概念）、光学系统频率响应通用理论、光通信链路带宽 | ❌ 未提及 |
| **PSF / 点扩散函数** | 成像模糊核 | 激光聚焦光斑分布（高斯光束是 PSF 的特例）、衍射光学元件设计、光刻曝光分布 | ❌ 未提及 |
| **像差（球差/彗差/像散/场曲/畸变/色差）** | 成像镜头缺陷 | 激光谐振腔模式像差、自适应光学波前校正、光刻投影物镜、光纤耦合透镜设计 | ❌ 未提及 |
| **数值孔径 NA** | 显微镜物镜集光能力 | 光纤数值孔径（接受角）、激光聚焦物镜 NA、光通信耦合效率 | ⚠️ 仅在成像中定义 |
| **衍射极限 / 艾里斑** | 成像分辨率上限 | 激光聚焦极限光斑、光刻分辨率极限、光学捕获（光镊）力计算 | ⚠️ 仅讨论成像分辨率 |
| **景深 / 焦深** | 摄影/工业视觉清晰范围 | 激光加工焦深容忍、光刻焦深预算（DOF ~ λ/NA²）、光学相干断层扫描（OCT）焦深 | ❌ 未提及 |
| **视场 / 像圈** | 镜头覆盖范围 | 激光扫描视场（f-theta 镜头）、显示面板照明均匀性视场、太阳能聚光器接受角 | ❌ 未提及 |
| **渐晕 / 平场 / 均匀性** | 像面照度分布 | 照明光学均匀性（均匀度公式）、显示背光均匀性、激光光束均匀化（beam homogenizer） | ⚠️ 仅在成像照明中讨论 |
| **像素 / 奈奎斯特频率 / 混叠** | 传感器采样理论 | 光通信 ADC 采样、光谱仪探测器采样、激光脉冲数字化、计算光学采样 | ⚠️ 仅讨论图像采样 |
| **4f 系统 / 空间滤波** | 傅里叶光学成像系统 | 激光光束整形（spatial light modulator, SLM）、光通信模式滤波、全息再现 | ⚠️ 仅作为成像系统讨论 |
| **Fabry-Perot 微腔** | 光谱分光器件 | 激光谐振腔（核心结构）、光纤 FP 滤波器、光学频率梳 | ⚠️ 仅讨论光谱仪应用 |
| **超表面（Metasurface）** | 新型光谱器件 | 激光光束偏转、聚焦超透镜（metalens）、光通信波前整形、偏振调控 | ⚠️ 仅讨论光谱应用 |
| **偏振 / 分光镜** | 成像对比度增强 | 激光偏振态控制、光纤保偏、电光调制、量子光学纠缠光子、光通信相干接收 | ⚠️ 基础定义已有，但激光/光纤应用未展开 |
| **干涉** | 成像干涉（全息） | 激光干涉仪（干涉测量、引力波探测）、光纤干涉传感器（Mach-Zehnder、Fabry-Perot）、光学相干层析 | ⚠️ 仅讨论双缝/薄膜干涉 |
| **衍射光栅** | 光谱仪分光 | 激光光栅耦合器（集成光子学）、光通信波分复用/解复用（AWG）、光栅压缩器（飞秒激光啁啾管理） | ⚠️ 仅讨论光谱色散 |

### 2.3 建议重新标注为"通用基础"的现有内容

以下 18 个现有概念/公式笔记应扩展其定义边界，从"成像专属"重新标注为"光学通用基础"，并在正文中增加跨领域应用段落：

| 文件编号 | 文件名 | 重新标注理由 | 建议补充的跨领域链接 |
|---------|--------|-------------|---------------------|
| `000` | `refractive-index` | 已通用，但可强化 | 光纤纤芯/包层折射率差、波导有效折射率 |
| `001` | `近轴近似` | 几何光学基础，非成像专属 | 激光谐振腔近轴分析（ABCD 矩阵）、光纤耦合近轴条件 |
| `016` | `abbe-number` | 材料色散属性，通用 | 激光玻璃色散、光纤色散（材料色散分量）、超透镜色散设计 |
| `021/022` | `interference/干涉` | 波动光学基础 | 激光干涉仪、光纤传感、光频梳 |
| `023/024` | `diffraction-grating/衍射光栅` | 通用光学元件 | 光通信 AWG、激光啁啾脉冲放大（CPA）压缩光栅、集成光子学光栅耦合器 |
| `029` | `瑞利判据` | 光学分辨率极限 | 激光聚焦光斑极限、光刻分辨率、光谱仪分辨率 |
| `038/039` | `nyquist-frequency/奈奎斯特频率` | 采样定理通用 | 光通信 ADC、光谱仪采样、激光脉冲数字化 |
| `040/041` | `aliasing/混叠` | 采样混叠通用 | 光谱重建混叠、光通信频谱混叠、光场采样 |
| `049` | `分光镜` | 通用光学元件 | 激光干涉仪、光通信耦合器、量子光学 |
| `050/051` | `polarization/偏振` | 波动光学基础 | 激光偏振控制、光纤保偏、电光调制、液晶显示 |
| `064` | `发射率` | 辐射度学基础 | 黑体辐射、红外探测、激光材料热辐射 |
| `066` | `spectral-power-distribution` | 光源光谱属性 | LED 光谱、激光线宽、荧光光谱、太阳光谱 |
| `070` | `fluorescence` | 光-物质相互作用 | 激光诱导荧光（LIF）、荧光显微镜、生物成像 |
| `071` | `raman-scattering` | 光-物质相互作用 | 拉曼激光器、光纤拉曼放大器、生物医学传感 |
| `077` | `fabry-perot-microcavity` | 谐振腔通用结构 | 激光谐振腔、光纤 FP 传感器、光学频率梳 |
| `078` | `metasurface` | 新型光学元件 | 超透镜（metalens）、激光光束偏转、全息显示 |
| `012` | `grating-equation` | 通用公式 | 光通信 WDM、激光脉冲压缩、AR/VR 光波导光栅 |
| `015` | `planck-blackbody` | 辐射度学基础 | 红外探测、热辐射、LED 色温、激光器热负载 |

---

## 3. 任务 2：非成像光学核心知识骨架

### 3.1 照明光学（Illumination Design）

> **定位**：以能量传输效率和光分布控制为目标，而非成像质量。核心关注点：光提取效率、配光曲线、均匀性、眩光控制。

#### 核心概念（15 个）

| 序号 | 中文术语 | 英文术语 | 一句话定义 |
|------|---------|---------|-----------|
| 1 | 光提取效率 | Light Extraction Efficiency (LEE) | LED 芯片产生的光子中实际逸出到外部环境的比例 |
| 2 | 配光曲线 | Luminous Intensity Distribution / IES Curve | 光源在不同方向上的发光强度分布，通常用极坐标图表示 |
| 3 | 朗伯体 | Lambertian Emitter | 发光强度随观察角度按余弦规律衰减的理想漫射体 |
| 4 | 光学扩展量 | Étendue / Geometric Extent | $G = n^2 A \Omega$，描述光束空间-角度占据体积，守恒量 |
| 5 | 集光率 | Concentration Ratio / Acceptance Angle | 聚光器将大面积光汇聚到小面积的能力 |
| 6 | 均匀度 | Uniformity | 照明面上光强/亮度的最大-最小比值或标准差 |
| 7 | 混光距离 | Mixing Distance | LED 阵列中不同颜色芯片的光充分混合所需的传播距离 |
| 8 | 全内反射 | Total Internal Reflection (TIR) | 光从光密介质到光疏介质时，入射角大于临界角时全部反射 |
| 9 | 菲涅尔损耗 | Fresnel Loss | 光在界面处因反射导致的能量损失，约 4%（n=1.5，正入射） |
| 10 | 光线追迹 | Ray Tracing | 在照明设计中模拟光线路径以预测光分布的数值方法 |
| 11 | 蒙特卡洛光线追迹 | Monte Carlo Ray Tracing | 随机采样光线方向以统计预测光分布的仿真方法 |
| 12 | 眩光 | Glare | 过亮光源或强光对比引起视觉不适或功能丧失的现象 |
| 13 | 统一眩光等级 | Unified Glare Rating (UGR) | 量化室内照明眩光程度的指标 |
| 14 | 光通量维持率 | Lumen Maintenance | LED 光源在额定寿命末期相对于初始光通量的百分比 |
| 15 | 色容差 | Color Tolerance / MacAdam Ellipse | 人眼不可察觉的色度差异范围，用麦克亚当椭圆描述 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 变量说明 |
|------|---------|--------|---------|
| 1 | 光学扩展量 | $G = n^2 A \cdot \Omega$ | $n$：折射率；$A$：截面积；$\Omega$：立体角 |
| 2 | 朗伯面发光强度 | $I(\theta) = I_0 \cos\theta$ | $I_0$：法向发光强度；$\theta$：与法线夹角 |
| 3 | 菲涅尔反射率（s 偏振） | $R_s = \left|\frac{n_1\cos\theta_i - n_2\cos\theta_t}{n_1\cos\theta_i + n_2\cos\theta_t}\right|^2$ | $n_1, n_2$：介质折射率；$\theta_i, \theta_t$：入射/折射角 |
| 4 | 菲涅尔反射率（p 偏振） | $R_p = \left|\frac{n_1\cos\theta_t - n_2\cos\theta_i}{n_1\cos\theta_t + n_2\cos\theta_i}\right|^2$ | 同上 |
| 5 | LED 光提取效率（简化） | $\eta_{LEE} = \frac{P_{out}}{P_{gen}} \approx \frac{1}{2}\left(1 - \cos\theta_c\right)$ | $\theta_c = \arcsin(1/n)$：临界角 |
| 6 | 照度平方反比定律 | $E = \frac{I}{d^2} \cos\theta$ | $I$：发光强度；$d$：距离；$\theta$：入射角 |
| 7 | 均匀度（最小/最大） | $U = \frac{E_{min}}{E_{max}}$ 或 $U = \frac{E_{min}}{E_{avg}}$ | $E$：照度 |
| 8 | 混光距离估算 | $d_{mix} \approx p \cdot \tan\theta_{1/2}$ | $p$：LED 像素间距；$\theta_{1/2}$：半功率角 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 功能说明 |
|------|----------|------|---------|
| 1 | LED 芯片 | LED Chip / Die | 半导体发光源，核心电光转换器件 |
| 2 | 反射杯/反射器 | Reflector / Reflector Cup | 收集和定向 LED 背向光子的光学元件 |
| 3 | 准直透镜 | Collimating Lens | 将 LED 发散光转换为平行光束 |
| 4 | 自由曲面透镜 | Freeform Lens | 非旋转对称曲面，用于实现特定配光曲线 |
| 5 | TIR 透镜 | TIR (Total Internal Reflection) Lens | 利用全内反射收集 LED 大角度光，提高效率 |
| 6 | 导光板 | Light Guide Plate (LGP) | 将边缘入射光均匀分布到整个平面的波导结构 |
| 7 | 扩散板/扩散膜 | Diffuser / Diffusion Film | 将准直光漫射为均匀面光源 |
| 8 | 积分球 | Integrating Sphere | 已存在于知识库（`40-devices/014-integrating-sphere`），用于测量总光通量 |

### 3.2 太阳能聚光（Solar Concentrator）

> **定位**：以最大化光通量汇聚到太阳能电池为目标，接受角与聚光比的权衡是核心设计矛盾。

#### 核心概念（12 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 聚光比 | Concentration Ratio (C) | 聚光器出口处辐照度与入口处之比，或面积比 |
| 2 | 复合抛物面聚光器 | Compound Parabolic Concentrator (CPC) | 由两段抛物线旋转组成的两维/三维聚光器，最大接受角内无像差聚光 |
| 3 | 接受角 | Acceptance Angle ($\theta_a$) | 聚光器能收集的最大入射偏离角 |
| 4 | 光学效率 | Optical Efficiency | 到达接收器的辐射通量与入射通量之比 |
| 5 | 几何聚光比 | Geometric Concentration Ratio | $C_g = A_{entry} / A_{exit}$ |
| 6 | 光学聚光比 | Optical Concentration Ratio | $C_o = C_g \cdot \eta_{opt}$ |
| 7 | 菲涅尔透镜聚光器 | Fresnel Lens Concentrator | 通过阶梯化曲面减少厚度和重量的聚光透镜 |
| 8 | 定日镜 | Heliostat | 跟踪太阳并将光反射到固定接收器的大型平面镜 |
| 9 | 塔式聚光系统 | Solar Power Tower | 多个定日镜将光汇聚到中央塔顶接收器 |
| 10 | 槽式聚光系统 | Parabolic Trough Collector | 线性抛物面镜将光汇聚到焦线接收管 |
| 11 | 光谱分束聚光 | Spectrum-Splitting Concentrator | 将太阳光按波长分离后分别汇聚到不同带隙电池 |
| 12 | 热斑效应 | Hot Spot Effect | 聚光不均匀导致电池局部过热和效率下降 |

#### 核心公式/计算模型（7 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | CPC 最大聚光比（2D） | $C_{max,2D} = \frac{1}{\sin\theta_a}$ | $\theta_a$：半接受角 |
| 2 | CPC 最大聚光比（3D） | $C_{max,3D} = \frac{1}{\sin^2\theta_a}$ | 3D 旋转对称 CPC |
| 3 | 光学效率 | $\eta_{opt} = \tau \cdot \alpha \cdot \rho \cdot \gamma \cdot (1 - f_{sh})$ | 透射率×吸收率×反射率×拦截因子×(1-遮挡率) |
| 4 | 太阳辐射功率 | $P_{sun} = 1361 \text{ W/m}^2$（大气层外） | AM1.5 标准光谱约 $1000 \text{ W/m}^2$ |
| 5 | 聚光太阳能电池效率 | $\eta_{cell}(C, T) = \eta_{ref} \left[1 - \beta(T - T_{ref})\right] \cdot f_{fill}(C)$ | 温度系数 $\beta$ 约 $0.05\% / ^\circ\text{C}$ |
| 6 | 光学扩展量守恒（聚光极限） | $C \cdot \sin^2\theta_{out} \leq \frac{n^2}{\sin^2\theta_a}$ | 导出聚光比上限 |
| 7 | 太阳张角对应聚光极限 | $C_{max,3D} \approx \frac{1}{(0.27^\circ)^2} \approx 46,000$ | 太阳角直径约 $0.53^\circ$ |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 复合抛物面聚光器 (CPC) | Compound Parabolic Concentrator | 无像差非成像聚光器的典型代表 |
| 2 | 菲涅尔透镜 | Fresnel Lens | 轻薄化聚光，常用于 CPV（聚光光伏） |
| 3 | 二次聚光器 | Secondary Concentrator | 放置在主聚光器焦点后，进一步提升聚光比 |
| 4 | III-V 多结太阳能电池 | III-V Multi-junction Solar Cell | 聚光光伏中使用的高效电池（GaInP/GaAs/Ge） |
| 5 | 太阳跟踪器 | Solar Tracker | 单轴或双轴机械跟踪，维持聚光对准 |
| 6 | 聚光光伏模块 | CPV Module | 聚光器 + 接收器 + 散热的集成封装 |
| 7 | 接收器/吸热器 | Receiver / Absorber | 将汇聚光能转化为热能或电能的终端器件 |

### 3.3 显示光学（Display Optics）

> **定位**：以人眼感知质量为目标，核心关注点：亮度均匀、色域覆盖、视角、功耗。

#### 核心概念（14 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 背光模组 | Backlight Unit (BLU) | LCD 显示中提供均匀面光源的组件 |
| 2 | 导光板网点 | Dot Pattern / Prism Pattern | 导光板底部的微结构，用于破坏 TIR 实现光提取 |
| 3 | 微透镜阵列 | Microlens Array (MLA) | 微米级透镜阵列，用于增强光提取、均匀化或 3D 显示 |
| 4 | 增亮膜 / 棱镜片 | Brightness Enhancement Film (BEF) / Prism Sheet | 通过折射回收大角度光，提升正面亮度 |
| 5 | 反射式偏振增亮膜 | Reflective Polarizer / DBEF | 反射再利用废偏振光，提升效率约 50% |
| 6 | 量子点增强膜 | Quantum Dot Enhancement Film (QDEF) | 用量子点将蓝光转换为窄带红绿光，提升色域 |
| 7 |  Mini-LED / Micro-LED | Mini-LED / Micro-LED | 分区背光或自发光像素，提升对比度和 HDR |
| 8 | 视角 | Viewing Angle | 可接受亮度/颜色变化的最大观察角度 |
| 9 | 色域 | Color Gamut | 显示系统能再现的颜色范围（如 DCI-P3, Rec.2020） |
| 10 | 对比度 | Contrast Ratio | 最白与最黑亮度比值 |
| 11 | 响应时间 | Response Time | 像素从一种灰度切换到另一种的时间 |
| 12 | 光刻图案化 | Photolithography Patterning | 制造显示面板中 TFT 和像素电极的关键工艺 |
| 13 | 光波导显示 | Waveguide Display | AR 眼镜中使用的超薄光学传输方案 |
| 14 | 出瞳扩展 | Exit Pupil Expansion (EPE) | 波导显示中通过衍射光栅将光束扩展到更大眼盒 |

#### 核心公式/计算模型（6 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 导光板提取效率 | $\eta_{out} = \frac{P_{out}}{P_{in}} \approx \frac{N_{dots} \cdot A_{dot}}{A_{total}} \cdot f_{scatter}$ | 网点密度与光提取效率的关系 |
| 2 | 亮度均匀度 | $U = \frac{L_{min}}{L_{max}}$ 或 $U = 1 - \frac{\sigma_L}{\bar{L}}$ | 亮度标准差/均值表征 |
| 3 | 微透镜焦距 | $f = \frac{R}{n - 1}$ | $R$：曲率半径；$n$：透镜材料折射率 |
| 4 | 视角半宽（波导） | $\theta_{view} \approx \arcsin\left(\frac{\lambda}{d}\right)$ | $d$：出瞳扩展光栅周期 |
| 5 | LCD 光利用率 | $\eta_{LCD} = \eta_{pol} \cdot \eta_{LC} \cdot \eta_{CF} \approx 0.5 \times 0.9 \times 0.33 \approx 15\%$ | 偏振损失 + 液晶开关损失 + 彩膜损失 |
| 6 | 量子点发光波长 | $\lambda = \frac{hc}{E_g + \Delta E}$ | 量子限域效应导致能隙增大，蓝移发射 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 导光板 (LGP) | Light Guide Plate | 显示背光中传输并分配光能的透明平板 |
| 2 | 扩散膜 | Diffusion Film | 雾化光线，消除 LED 点光源可见性 |
| 3 | 棱镜片 (BEF) | Prism Sheet / Brightness Enhancement Film | 将离轴光折回正面，提升亮度 |
| 4 | 反射片 | Reflective Sheet | 导光板底部反射，提高光利用率 |
| 5 | 微透镜阵列膜 | MLA Film | 用于增强正面亮度或实现 2D/3D 可切换显示 |
| 6 | 量子点膜 (QDEF) | QD Enhancement Film | 提升 LCD 色域至接近 OLED |
| 7 | 偏振片 | Polarizer | LCD 核心组件，控制光偏振态 |
| 8 | 衍射光波导 | Diffractive Waveguide | AR 眼镜中传输图像到人眼的关键光学元件 |

### 3.4 光通信耦合光学（Coupling Optics）

> **定位**：以最大化光功率从光源/光纤耦合到目标波导/光纤为目标，接受角和模式匹配是核心。

#### 核心概念（12 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 耦合效率 | Coupling Efficiency | 耦合到目标波导的功率与入射功率之比 |
| 2 | 模式匹配 | Mode Matching | 使入射光场分布与波导基模分布一致以最大化耦合 |
| 3 | 数值孔径匹配 | NA Matching | 光源 NA 与光纤/波导 NA 的匹配 |
| 4 | 光纤对准公差 | Fiber Alignment Tolerance | 横向/角度偏移导致耦合效率下降的容限 |
| 5 | 透镜耦合 | Lens Coupling | 使用透镜将光束聚焦到光纤端面 |
| 6 | 直接耦合 / 对接耦合 | Butt Coupling | 激光器与光纤直接端面接触耦合 |
| 7 | 楔形耦合 | Tapered Coupling | 通过锥形波导逐渐匹配模式尺寸 |
| 8 | 光栅耦合 | Grating Coupling | 通过表面光栅将垂直入射光耦合到平面波导 |
| 9 | 回波损耗 | Return Loss | 反射光功率与入射光功率之比，单位为 dB |
| 10 | 插入损耗 | Insertion Loss | 耦合器/连接器引入的功率损耗，单位为 dB |
| 11 | 单模条件 | Single-Mode Condition | $V = \frac{2\pi a}{\lambda} \sqrt{n_{core}^2 - n_{clad}^2} < 2.405$ | 归一化频率 |
| 12 | 模场直径 | Mode Field Diameter (MFD) | 基模光强分布的 $1/e^2$ 宽度 |

#### 核心公式/计算模型（7 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 高斯光束耦合效率（横向偏移） | $\eta = \exp\left(-\frac{d^2}{w^2}\right)$ | $d$：横向偏移；$w$：光束半径 |
| 2 | 高斯光束耦合效率（角度偏移） | $\eta = \exp\left(-\frac{(k w \theta/2)^2}{}\right)$ | $\theta$：角度偏移；$k = 2\pi/\lambda$ |
| 3 | 光纤 NA | $NA = \sqrt{n_{core}^2 - n_{clad}^2} \approx n_{core}\sqrt{2\Delta}$ | $\Delta = (n_{core}-n_{clad})/n_{core}$ |
| 4 | 透镜耦合焦距选择 | $f = \frac{w_{beam}}{NA_{fiber}}$ | 将光束半径 $w_{beam}$ 聚焦到光纤 NA |
| 5 | 菲涅尔反射损耗（端面） | $R = \left(\frac{n_1 - n_2}{n_1 + n_2}\right)^2$ | 单界面反射率，如空气-硅约 $30\%$ |
| 6 | 光栅耦合效率（近似） | $\eta_{grating} \propto \left|\int E_{inc}(x) \cdot E_{wg}^*(x) \cdot \alpha(x) dx\right|^2$ | 入射场与波导场重叠积分 |
| 7 | 插入损耗（dB） | $IL = -10 \log_{10}(P_{out}/P_{in})$ | 功率比转换为 dB |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 光纤准直器 | Fiber Collimator | 将光纤出射光准直为平行光束 |
| 2 | 光纤聚焦器 | Fiber Focus Assembly | 将自由空间光聚焦耦合到光纤 |
| 3 | 光纤 V 型槽 | Fiber V-groove | 精密硅基底槽，用于多光纤阵列对准 |
| 4 | 光纤耦合器（熔融拉锥） | Fused Fiber Coupler | 将一根光纤的光分/合到另一根 |
| 5 | 光隔离器 | Optical Isolator | 基于法拉第旋光效应，只允许单向传输 |
| 6 | 光衰减器 | Optical Attenuator | 精确降低光功率的组件 |
| 7 | 光栅耦合器（芯片级） | On-chip Grating Coupler | 硅光子芯片上耦合光进出平面波导的器件 |

### 3.5 非成像光学：可扩展为知识库笔记的骨架结构

```
📁 10-concepts/
├── ...（现有文件保留）
├── 081-light-extraction-efficiency.md        # LED 光提取效率
├── 082-luminous-intensity-distribution.md    # 配光曲线 / IES 曲线
├── 083-lambertian-emitter.md                 # 朗伯体
├── 084-etendue.md                            # 光学扩展量
├── 085-concentration-ratio.md                # 聚光比
├── 086-acceptance-angle.md                   # 接受角
├── 087-compound-parabolic-concentrator.md    # CPC 聚光器
├── 088-light-guide-plate.md                 # 导光板
├── 089-microlens-array.md                    # 微透镜阵列
├── 090-brightness-enhancement-film.md        # 增亮膜 / BEF
├── 091-quantum-dot-enhancement.md            # 量子点增强膜
├── 092-waveguide-display.md                  # 光波导显示
├── 093-exit-pupil-expansion.md               # 出瞳扩展
├── 094-coupling-efficiency.md               # 耦合效率
├── 095-mode-matching.md                      # 模式匹配
├── 096-fiber-alignment-tolerance.md          # 光纤对准公差
├── 097-grating-coupler.md                    # 光栅耦合器
├── 098-total-internal-reflection-lens.md     # TIR 透镜
├── 099-freeform-optics.md                    # 自由曲面光学
└── 100-solar-tracker.md                      # 太阳跟踪器

📁 20-formulas/
├── ...（现有文件保留）
├── 017-etendue-conservation.md               # 光学扩展量守恒
├── 018-fresnel-reflectance.md               # 菲涅尔反射率（s/p）
├── 019-lambert-cosine-law.md                # 朗伯余弦定律
├── 020-cpc-concentration-limit.md           # CPC 最大聚光比
├── 021-illumination-uniformity.md           # 照明均匀度公式
├── 022-gaussian-coupling-lateral.md         # 高斯光束耦合（横向）
├── 023-gaussian-coupling-angular.md         # 高斯光束耦合（角度）
├── 024-fiber-na.md                          # 光纤 NA 公式
└── 025-insertion-loss-db.md                 # 插入损耗 dB

📁 30-domains/
├── ...（现有文件保留）
├── 006-illumination-design.md               # 照明设计领域
├── 007-solar-concentrator.md                # 太阳能聚光领域
├── 008-display-optics.md                    # 显示光学领域
└── 009-optical-communication.md             # 光通信领域

📁 40-devices/
├── ...（现有文件保留）
├── 018-led-chip.md                          # LED 芯片
├── 019-fresnel-lens.md                      # 菲涅尔透镜
├── 020-cpc-concentrator.md                  # CPC 聚光器
├── 021-microlens-array-film.md              # 微透镜阵列膜
├── 022-prism-sheet.md                       # 棱镜片 / BEF
├── 023-quantum-dot-film.md                  # 量子点膜
├── 024-fiber-collimator.md                  # 光纤准直器
├── 025-fiber-v-groove.md                    # 光纤 V 型槽
├── 026-optical-isolator.md                  # 光隔离器
├── 027-on-chip-grating-coupler.md           # 芯片光栅耦合器
└── 028-diffractive-waveguide.md             # 衍射光波导
```

---

## 4. 任务 3：激光光学与光子学核心知识骨架

### 4.1 激光器原理（Laser Principles）

> **定位**：以受激辐射光放大为核心，理解谐振腔、增益、泵浦和调制是掌握激光系统的基础。

#### 核心概念（15 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 受激辐射 | Stimulated Emission | 入射光子诱导激发态原子发射同相位、同方向、同频率光子的过程 |
| 2 | 粒子数反转 | Population Inversion | 高能级粒子数多于低能级，激光增益的必要条件 |
| 3 | 光学谐振腔 | Optical Resonator / Cavity | 两个反射镜之间形成的光反馈结构，决定激光模式 |
| 4 | 增益介质 | Gain Medium | 通过泵浦实现粒子数反转、提供光放大的介质（固体/气体/半导体/光纤） |
| 5 | 泵浦 | Pumping | 向增益介质输入能量以实现粒子数反转的过程 |
| 6 | 激光阈值 | Laser Threshold | 增益等于损耗时的临界点，超过此点才有激光输出 |
| 7 | 纵模 | Longitudinal Mode | 谐振腔中沿光轴方向的驻波模式，频率间隔 $\Delta\nu = c/2L$ |
| 8 | 横模 | Transverse Mode | 垂直于光轴方向的场分布，如 TEM$_{00}$（高斯模） |
| 9 | 品质因数 Q | Quality Factor | $Q = 2\pi \nu \cdot \frac{E_{stored}}{P_{loss}}$，表征谐振腔储能能力 |
| 10 | Q 开关 | Q-Switching | 突然降低腔损耗以释放储存能量，产生纳秒级高功率脉冲 |
| 11 | 锁模 | Mode Locking | 使多个纵模保持固定相位关系，产生飞秒/皮秒超短脉冲 |
| 12 | 可饱和吸收体 | Saturable Absorber | 强光下吸收降低、弱光下吸收高的材料，用于被动 Q 开关和锁模 |
| 13 | 调谐 | Tuning | 改变激光输出波长的方法（光栅、温度、电流等） |
| 14 | 线宽 | Linewidth / Spectral Width | 激光光谱的半高全宽（FWHM），表征单色性 |
| 15 | 相干长度 | Coherence Length | $L_c = c / \Delta\nu$，与线宽成反比，决定干涉可测距离 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 激光阈值条件 | $g_{th} = \frac{\alpha + T}{2L}$ | $g_{th}$：阈值增益系数；$\alpha$：损耗；$T$：输出镜透射率；$L$：腔长 |
| 2 | 小信号增益 | $g_0 = \sigma \Delta N$ | $\sigma$：受激辐射截面；$\Delta N$：粒子数反转密度 |
| 3 | 饱和光强 | $I_s = \frac{h\nu}{\sigma \tau}$ | $\tau$：上能级寿命 |
| 4 | 增益饱和 | $g = \frac{g_0}{1 + I/I_s}$ | 强光下增益下降 |
| 5 | 纵模频率间隔 | $\Delta\nu = \frac{c}{2nL}$ | $n$：腔内折射率；$L$：腔长 |
| 6 | 谐振腔稳定性条件 | $0 < g_1 g_2 < 1$ | $g_i = 1 - L/R_i$，$R_i$ 为镜曲率半径 |
| 7 | Q 开关脉冲峰值功率 | $P_{peak} \approx \frac{E_{stored}}{\tau_{cavity}}$ | $\tau_{cavity} = L/(c\cdot losses)$ |
| 8 | 锁模脉冲宽度 | $\Delta t \approx \frac{1}{N \cdot \Delta\nu}$ | $N$：锁模纵模数；$\Delta\nu$：纵模间隔 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 固体激光器 | Solid-State Laser (Nd:YAG, Ti:Sapphire) | 掺杂晶体制增益介质，高功率、窄线宽 |
| 2 | 半导体激光器 / 激光二极管 | Semiconductor Laser / Laser Diode | 基于 p-n 结电注入，小型化、高效、可快速调制 |
| 3 | 光纤激光器 | Fiber Laser | 掺杂光纤为增益介质，散热好、光束质量高 |
| 4 | 气体激光器 | Gas Laser (HeNe, CO₂, Ar⁺) | 气体放电泵浦，特定波长（如 632.8 nm, 10.6 μm） |
| 5 | 染料激光器 | Dye Laser | 有机染料溶液增益，宽调谐范围 |
| 6 | 声光 Q 开关 | Acousto-Optic Q-Switch | 利用声光衍射改变腔损耗，主动 Q 开关 |
| 7 | 电光调制器 | Electro-Optic Modulator (EOM) | 利用电光效应（Pockels/Kerr）调制相位/振幅 |
| 8 | 可饱和吸收镜 (SESAM) | SESAM | 半导体可饱和吸收镜，用于被动锁模 |

### 4.2 光束传播（Beam Propagation）

> **定位**：激光光束以高斯光束为基本模型，理解其传播、聚焦和光束质量是激光应用的核心。

#### 核心概念（14 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 高斯光束 | Gaussian Beam | 横截面光强呈高斯分布的激光束，TEM$_{00}$ 模式的典型输出 |
| 2 | 光束腰 / 束腰 | Beam Waist ($w_0$) | 高斯光束最小半径处，光强降至 $1/e^2$ 的半径 |
| 3 | 瑞利范围 | Rayleigh Range ($z_R$) | 束腰到光束面积 doubled 的距离，$z_R = \pi w_0^2 / \lambda$ |
| 4 | 发散角 | Divergence Angle ($\theta$) | 远场光束半角扩展，$\theta = \lambda / (\pi w_0)$（理想高斯） |
| 5 | 光束质量因子 M² | Beam Quality Factor M² | 实际光束与理想高斯光束的接近程度，$M^2 \geq 1$ |
| 6 | 光束半径 | Beam Radius ($w(z)$) | 距离束腰 $z$ 处的 $1/e^2$ 半径：$w(z) = w_0\sqrt{1 + (z/z_R)^2}$ |
| 7 | 波前曲率半径 | Radius of Curvature ($R(z)$) | 高斯光束等相位面的曲率半径 |
| 8 | 高斯光束 q 参数 | Complex Beam Parameter $q$ | $\frac{1}{q(z)} = \frac{1}{R(z)} - i\frac{\lambda}{\pi w^2(z)}$，方便 ABCD 矩阵传输 |
| 9 | 聚焦光斑 | Focused Spot Size | 透镜聚焦后焦面上的光斑直径，$d = \frac{4\lambda f}{\pi D} = \frac{2\lambda}{\pi} \cdot \frac{f}{w}$ |
| 10 | 焦深 / 景深 | Depth of Focus (DOF) | 聚焦光斑保持在可接受尺寸内的轴向范围，$DOF \approx \pm 2\lambda(f/D)^2$ |
| 11 | 贝塞尔光束 | Bessel Beam | 无衍射光束，中心光斑在传播中保持不变，由轴锥镜产生 |
| 12 | 艾里光束 | Airy Beam | 自加速、无衍射光束，沿弯曲路径传播 |
| 13 | 光束整形 | Beam Shaping | 将高斯光束转换为平顶（top-hat）、环形或其他分布 |
| 14 | 空间光调制器 | Spatial Light Modulator (SLM) | 可编程控制波前的液晶或微镜阵列器件 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 高斯光束半径 | $w(z) = w_0 \sqrt{1 + \left(\frac{z}{z_R}\right)^2}$ | $z_R = \frac{\pi w_0^2}{\lambda}$ |
| 2 | 瑞利范围 | $z_R = \frac{\pi w_0^2}{\lambda}$ | 束腰到光斑面积翻倍的位置 |
| 3 | 远场发散角 | $\theta = \frac{\lambda}{\pi w_0}$（理想高斯） | $M^2$ 实际：$\theta = M^2 \frac{\lambda}{\pi w_0}$ |
| 4 | 聚焦光斑直径 | $d = \frac{4\lambda f}{\pi D} = \frac{2\lambda}{\pi} \cdot F\#$ | $D$：入射光束直径；$f$：透镜焦距 |
| 5 | 焦深 | $DOF = \pm 2\lambda\left(\frac{f}{D}\right)^2 = \pm 2\lambda \cdot (F\#)^2$ | 聚焦光斑保持接近最小尺寸的轴向范围 |
| 6 | q 参数传输 | $q_2 = \frac{A q_1 + B}{C q_1 + D}$ | 用 ABCD 矩阵描述高斯光束通过光学系统 |
| 7 | 高斯光束通过薄透镜 | $\frac{1}{q_{out}} = \frac{1}{q_{in}} - \frac{1}{f}$ | 类似几何光学，但使用复参数 |
| 8 | 光束质量 M² | $M^2 = \frac{\pi w_0 \theta}{\lambda}$ | $M^2 = 1$ 为理想高斯光束 |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 透镜（聚焦/扩束） | Focusing Lens / Beam Expander | 控制激光束腰位置和大小 |
| 2 | 针孔滤波器 | Pinhole Spatial Filter | 阻挡高阶横模，净化光束质量 |
| 3 | 准直器 | Collimator | 将发散激光变为平行光 |
| 4 | 扩束镜 | Beam Expander (Galilean / Keplerian) | 增大光束直径以减小发散角 |
| 5 | 轴锥镜 | Axicon | 产生贝塞尔光束的锥形透镜 |
| 6 | 空间光调制器 (SLM) | Spatial Light Modulator | 可编程波前控制，用于全息、光束整形 |
| 7 | 光束分析仪 | Beam Profiler | 测量光束腰、发散角、M² 的仪器 |

### 4.3 光纤光学（Fiber Optics）

> **定位**：以光导纤维为传输介质，理解模式、色散、损耗和非线性效应是光纤通信和传感的基础。

#### 核心概念（15 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 单模光纤 | Single-Mode Fiber (SMF) | 仅支持基模（HE₁₁）传输，芯径约 8-10 μm |
| 2 | 多模光纤 | Multi-Mode Fiber (MMF) | 支持多个模式传输，芯径 50/62.5 μm，模间色散大 |
| 3 | 阶跃折射率光纤 | Step-Index Fiber | 纤芯与包层折射率突变的结构 |
| 4 | 渐变折射率光纤 | Graded-Index Fiber (GRIN) | 纤芯折射率从中心向外渐变，减小模间色散 |
| 5 | 归一化频率 V | Normalized Frequency V | $V = \frac{2\pi a}{\lambda} \sqrt{n_{core}^2 - n_{clad}^2}$，决定模式数量 |
| 6 | 截止波长 | Cutoff Wavelength | 高阶模截止的波长，低于此波长单模光纤变为多模 |
| 7 | 模场直径 | Mode Field Diameter (MFD) | 基模光强分布 $1/e^2$ 处的宽度，通常大于芯径 |
| 8 | 衰减 / 损耗 | Attenuation / Loss | 光纤中光功率随距离的指数衰减，单位 dB/km |
| 9 | 材料色散 | Material Dispersion | 纤芯材料折射率随波长变化导致的脉冲展宽 |
| 10 | 波导色散 | Waveguide Dispersion | 波导结构导致的有效折射率随波长变化 |
| 11 | 色散位移光纤 | Dispersion-Shifted Fiber (DSF) | 将零色散点从 1310 nm 移到 1550 nm 的光纤 |
| 12 | 非线性效应 | Nonlinear Effects | 强光下光纤中的 Kerr 效应、自相位调制 (SPM)、交叉相位调制 (XPM)、四波混频 (FWM) |
| 13 | 受激拉曼散射 | Stimulated Raman Scattering (SRS) | 非线性效应，光能量向长波长斯托克斯光转移 |
| 14 | 受激布里渊散射 | Stimulated Brillouin Scattering (SBS) | 非线性效应，光向后散射并产生频移声波 |
| 15 | 光纤放大器 | Optical Fiber Amplifier (EDFA) | 掺杂光纤（如 Er³⁺）在泵浦光作用下放大信号光 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 光纤 NA | $NA = \sqrt{n_{core}^2 - n_{clad}^2} \approx n_{core}\sqrt{2\Delta}$ | $\Delta$：相对折射率差 |
| 2 | 单模条件 | $V < 2.405$ | 贝塞尔函数 $J_0$ 的第一个零点 |
| 3 | 模场直径近似（阶跃） | $MFD \approx 2w_0 \approx 2a\left(0.65 + \frac{1.619}{V^{1.5}} + \frac{2.879}{V^6}\right)$ | Marcuse 公式 |
| 4 | 衰减（dB） | $\alpha(dB/km) = \frac{10}{L} \log_{10}\left(\frac{P_{in}}{P_{out}}\right)$ | 典型值：0.2 dB/km @ 1550 nm |
| 5 | 色散参数 | $D = -\frac{\lambda}{c} \frac{d^2 n_{eff}}{d\lambda^2}$ | 单位 ps/(nm·km)，表征脉冲展宽 |
| 6 | 脉冲展宽（色散） | $\Delta\tau = D \cdot L \cdot \Delta\lambda$ | $\Delta\lambda$：光源光谱宽度 |
| 7 | 非线性折射率（Kerr） | $n = n_0 + n_2 I$ | $n_2 \approx 2.6 \times 10^{-20}$ m²/W（硅光纤） |
| 8 | EDFA 增益 | $G = \exp(g_0 L_{eff})$ | $g_0$：小信号增益系数；$L_{eff}$：有效作用长度 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 单模光纤 (SMF-28) | Single-Mode Fiber | 标准通信光纤，零色散 @ 1310 nm，最低损耗 @ 1550 nm |
| 2 | 多模光纤 (OM3/OM4) | Multi-Mode Fiber | 短距离高速通信，支持 10/40/100 Gbps |
| 3 | 掺铒光纤放大器 (EDFA) | Erbium-Doped Fiber Amplifier | 1550 nm 波段光信号放大，光通信核心器件 |
| 4 | 光纤耦合器 | Fiber Coupler / Splitter | 熔融拉锥分光器件，1×2、1×N 等 |
| 5 | 光纤布拉格光栅 (FBG) | Fiber Bragg Grating | 纤芯折射率周期性调制，用作滤波器、传感器 |
| 6 | 光隔离器 | Optical Isolator | 防止反射光回到激光器，保护光源 |
| 7 | 光纤环形器 | Optical Circulator | 单向传输路由器件，三端口或四端口 |
| 8 | 光纤偏振控制器 | Fiber Polarization Controller | 调整光纤中光的偏振态 |

### 4.4 集成光子学（Integrated Photonics）

> **定位**：在芯片尺度上构建光学功能器件，是光通信、传感、量子信息和计算的核心技术平台。

#### 核心概念（15 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 光波导 | Optical Waveguide | 限制光在特定区域传播的微纳结构（脊波导、条波导、槽波导） |
| 2 | 倏逝场 | Evanescent Field | 波导芯层外指数衰减的光场，用于传感和耦合 |
| 3 | 有效折射率 | Effective Refractive Index ($n_{eff}$) | 波导模式的等效折射率，$n_{clad} < n_{eff} < n_{core}$ |
| 4 | 群速度 | Group Velocity | 光脉冲包络的传播速度，$v_g = c / n_g$ |
| 5 | 群折射率 | Group Index ($n_g$) | $n_g = n_{eff} - \lambda \frac{dn_{eff}}{d\lambda}$ |
| 6 | 定向耦合器 | Directional Coupler | 两个靠近波导通过倏逝场交换光能的器件 |
| 7 | 耦合长度 | Coupling Length | 光能从一根波导完全转移到另一根所需的距离 |
| 8 | Y 分支 | Y-Branch / Power Splitter | 将一路光分成两路的波导结构 |
| 9 | 马赫-曾德尔干涉仪 (MZI) | Mach-Zehnder Interferometer | 两臂波导干涉结构，用于调制和传感 |
| 10 | 微环谐振器 | Microring Resonator | 环形波导，特定波长满足共振条件时增强/滤除 |
| 11 | 自由光谱范围 | Free Spectral Range (FSR) | 相邻共振峰之间的波长/频率间隔 |
| 12 | 品质因数 Q | Quality Factor | $Q = \lambda / \Delta\lambda_{FWHM}$，表征谐振器储能能力 |
| 13 | 电光调制器 | Electro-Optic Modulator | 利用电光效应（Pockels）改变波导折射率，调制相位/振幅 |
| 14 | 热光调谐 | Thermo-Optic Tuning | 通过加热改变硅波导折射率，实现波长调谐 |
| 15 | 光子芯片 | Photonic Integrated Circuit (PIC) | 将多个光子器件集成在单一芯片上的系统 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 波导模式条件 | $\beta = k_0 n_{eff} = \frac{2\pi}{\lambda} n_{eff}$ | $\beta$：传播常数 |
| 2 | 倏逝场衰减长度 | $d_{ev} = \frac{1}{\gamma} = \frac{\lambda}{2\pi\sqrt{n_{eff}^2 - n_{clad}^2}}$ | 光场强度降至 $1/e^2$ 的距离 |
| 3 | 定向耦合器耦合系数 | $\kappa = \frac{\pi}{2L_c}$ | $L_c$：耦合长度 |
| 4 | 耦合长度 | $L_c = \frac{\pi}{2\kappa}$ | 完全功率转移距离 |
| 5 | 微环共振条件 | $2\pi R \cdot n_{eff} = m\lambda$ | $R$：环半径；$m$：整数级次 |
| 6 | 自由光谱范围 | $FSR = \frac{\lambda^2}{2\pi R \cdot n_g}$ | 或频率域 $FSR_\nu = c/(2\pi R \cdot n_g)$ |
| 7 | 微环 Q 值 | $Q = \frac{\lambda}{\Delta\lambda} = \frac{\omega \tau_{photon}}{2}$ | $\tau_{photon}$：光子寿命 |
| 8 | 电光相位调制（Pockels） | $\Delta\phi = \frac{2\pi}{\lambda} \cdot \Delta n \cdot L = \frac{2\pi}{\lambda} \cdot \frac{1}{2}n^3 r_{63} E \cdot L$ | $r_{63}$：电光系数；$E$：电场 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 硅光子芯片 | Silicon Photonics PIC | 基于 SOI（绝缘体上硅）平台，CMOS 兼容制造 |
| 2 | 氮化硅波导 | SiN Waveguide | 更宽透明窗口（可见到近红外），低损耗 |
| 3 | III-V 激光器集成 | III-V-on-Silicon Laser | 将 InP 基激光器键合到硅光子芯片 |
| 4 | 微环调制器 | Microring Modulator | 高速电光调制器，体积小、功耗低 |
| 5 | 阵列波导光栅 (AWG) | Arrayed Waveguide Grating | 波分复用/解复用器，光通信核心器件 |
| 6 | 光栅耦合器 | Grating Coupler | 将光纤光垂直耦合到芯片波导 |
| 7 | 波导光电探测器 | Waveguide Photodetector | 集成 Ge-on-Si 探测器，与硅光子平台兼容 |
| 8 | 可调谐激光器 (DBR/DFB) | Tunable Laser | 集成布拉格光栅的窄线宽激光器 |

### 4.5 激光光学与光子学：可扩展为知识库笔记的骨架结构

```
📁 10-concepts/
├── ...（现有文件 + 非成像概念）
├── 101-stimulated-emission.md             # 受激辐射
├── 102-population-inversion.md            # 粒子数反转
├── 103-optical-resonator.md               # 光学谐振腔
├── 104-gain-medium.md                     # 增益介质
├── 105-laser-pumping.md                   # 泵浦
├── 106-laser-threshold.md                 # 激光阈值
├── 107-longitudinal-mode.md               # 纵模
├── 108-transverse-mode.md                 # 横模
├── 109-quality-factor-q.md                # 品质因数 Q
├── 110-q-switching.md                     # Q 开关
├── 111-mode-locking.md                    # 锁模
├── 112-saturable-absorber.md              # 可饱和吸收体
├── 113-laser-linewidth.md                 # 激光线宽
├── 114-coherence-length.md                # 相干长度（与现有 coherence 关联）
├── 115-gaussian-beam.md                   # 高斯光束
├── 116-beam-waist.md                      # 束腰
├── 117-rayleigh-range.md                  # 瑞利范围
├── 118-beam-divergence.md                 # 发散角
├── 119-beam-quality-m2.md               # 光束质量因子 M²
├── 120-q-parameter.md                     # 高斯光束 q 参数
├── 121-focused-spot-size.md              # 聚焦光斑
├── 122-bessel-beam.md                     # 贝塞尔光束
├── 123-spatial-light-modulator.md        # 空间光调制器
├── 124-single-mode-fiber.md              # 单模光纤
├── 125-multi-mode-fiber.md               # 多模光纤
├── 126-graded-index-fiber.md             # 渐变折射率光纤
├── 127-normalized-frequency-v.md         # 归一化频率 V
├── 128-mode-field-diameter.md            # 模场直径
├── 129-fiber-attenuation.md              # 光纤衰减
├── 130-material-dispersion.md            # 材料色散
├── 131-waveguide-dispersion.md           # 波导色散
├── 132-nonlinear-effects.md              # 非线性效应（SPM/XPM/FWM/SRS/SBS）
├── 133-edfa.md                            # 掺铒光纤放大器
├── 134-optical-waveguide.md              # 光波导
├── 135-evanescent-field.md               # 倏逝场
├── 136-effective-refractive-index.md     # 有效折射率
├── 137-directional-coupler.md            # 定向耦合器
├── 138-coupling-length.md                # 耦合长度
├── 139-mach-zehnder-interferometer.md    # 马赫-曾德尔干涉仪
├── 140-microring-resonator.md            # 微环谐振器
├── 141-free-spectral-range.md            # 自由光谱范围
├── 142-quality-factor-microring.md        # 微环品质因数 Q
├── 143-electro-optic-modulator.md       # 电光调制器
├── 144-thermo-optic-tuning.md            # 热光调谐
└── 145-photonic-integrated-circuit.md      # 光子芯片

📁 20-formulas/
├── ...（现有 + 非成像公式）
├── 026-laser-threshold-condition.md       # 激光阈值条件
├── 027-longitudinal-mode-spacing.md      # 纵模频率间隔
├── 028-cavity-stability-condition.md     # 谐振腔稳定性条件
├── 029-gaussian-beam-waist.md            # 高斯光束半径
├── 030-rayleigh-range.md                 # 瑞利范围
├── 031-beam-divergence-angle.md          # 远场发散角
├── 032-focused-spot-diameter.md          # 聚焦光斑直径
├── 033-depth-of-focus.md                 # 焦深（与现有景深关联扩展）
├── 034-beam-quality-m2.md                # 光束质量 M²
├── 035-fiber-na.md                        # 光纤 NA（与现有 NA 关联）
├── 036-single-mode-condition.md          # 单模条件
├── 037-fiber-attenuation-db.md           # 光纤衰减 dB
├── 038-pulse-broadening-dispersion.md   # 色散脉冲展宽
├── 039-kerr-nonlinear-index.md           # Kerr 非线性折射率
├── 040-microring-resonance.md            # 微环共振条件
├── 041-free-spectral-range.md            # 自由光谱范围
├── 042-microring-q-factor.md             # 微环 Q 值
└── 043-pockels-phase-modulation.md       # Pockels 相位调制

📁 30-domains/
├── ...（现有 + 非成像领域）
├── 010-laser-systems.md                  # 激光系统领域
├── 011-fiber-optic-communication.md      # 光纤通信领域
├── 012-integrated-photonics.md           # 集成光子学领域
└── 013-laser-material-processing.md      # 激光材料加工领域

📁 40-devices/
├── ...（现有 + 非成像设备）
├── 029-solid-state-laser.md              # 固体激光器
├── 030-laser-diode.md                    # 激光二极管
├── 031-fiber-laser.md                    # 光纤激光器
├── 032-co2-laser.md                      # CO₂ 激光器
├── 033-acousto-optic-q-switch.md        # 声光 Q 开关
├── 034-electro-optic-modulator.md       # 电光调制器
├── 035-sesam.md                          # 可饱和吸收镜
├── 036-beam-expander.md                  # 扩束镜
├── 037-spatial-light-modulator.md       # 空间光调制器
├── 038-beam-profiler.md                  # 光束分析仪
├── 039-smf-28.md                         # 单模光纤 SMF-28
├── 040-edfa.md                           # 掺铒光纤放大器
├── 041-fiber-coupler.md                  # 光纤耦合器
├── 042-fiber-bragg-grating.md           # 光纤布拉格光栅
├── 043-optical-circulator.md            # 光纤环形器
├── 044-silicon-photonics-pic.md         # 硅光子芯片
├── 045-microring-modulator.md            # 微环调制器
├── 046-arrayed-waveguide-grating.md    # 阵列波导光栅 AWG
└── 047-tunable-laser.md                  # 可调谐激光器
```

---

## 5. 任务 4：光电子与辐射度学核心知识骨架

### 5.1 辐射度学（Radiometry）

> **定位**：以物理量客观测量电磁辐射能量，与"人眼感知"无关，是光电子系统的物理基础。

#### 核心概念（14 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 辐射通量 / 辐射功率 | Radiant Flux ($\Phi_e$) | 单位时间内发射、传输或接收的辐射能量，单位 W |
| 2 | 辐射强度 | Radiant Intensity ($I_e$) | 单位立体角内的辐射通量，单位 W/sr |
| 3 | 辐射亮度 | Radiance ($L_e$) | 单位投影面积、单位立体角内的辐射通量，单位 W/(m²·sr) |
| 4 | 辐射出度 / 辐射发射度 | Radiant Exitance ($M_e$) | 单位表面积发出的辐射通量，单位 W/m² |
| 5 | 辐射照度 | Irradiance ($E_e$) | 单位接收面积上的辐射通量，单位 W/m² |
| 6 | 辐射曝光量 | Radiant Exposure ($H_e$) | 辐射照度对时间的积分，单位 J/m² |
| 7 | 光谱辐射量 | Spectral Radiant Quantity | 单位波长间隔内的辐射量，如光谱辐射亮度 $L_{e,\lambda}$ |
| 8 | 立体角 | Solid Angle ($\Omega$) | 球面上面积与半径平方之比，单位 sr（球面度） |
| 9 | 朗伯体 / 朗伯辐射面 | Lambertian Surface | 辐射亮度与方向无关的理想漫射面，$M_e = \pi L_e$ |
| 10 | 黑体辐射 | Blackbody Radiation | 理想吸收体/发射体的辐射，普朗克定律描述 |
| 11 | 发射率 | Emissivity ($\epsilon$) | 实际物体辐射出度与同温度黑体辐射出度之比 |
| 12 | 比辐射率 | Spectral Emissivity | 单位波长处的发射率 |
| 13 | 反射率 / 透射率 / 吸收率 | Reflectance / Transmittance / Absorptance | $\rho + \tau + \alpha = 1$（能量守恒） |
| 14 | 基尔霍夫热辐射定律 | Kirchhoff's Law | 热平衡下，发射率等于吸收率（$\epsilon = \alpha$） |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 辐射强度定义 | $I_e = \frac{d\Phi_e}{d\Omega}$ | 立体角微分内的辐射通量 |
| 2 | 辐射亮度定义 | $L_e = \frac{d^2\Phi_e}{dA \cdot d\Omega \cdot \cos\theta}$ | 投影面积与立体角内的辐射通量 |
| 3 | 辐射照度（点源） | $E_e = \frac{I_e}{r^2} \cos\theta$ | 平方反比定律 + 余弦因子 |
| 4 | 朗伯面辐射出度 | $M_e = \pi L_e$ | 亮度均匀的漫射面 |
| 5 | 立体角（锥角） | $\Omega = 2\pi(1 - \cos\theta)$ | 半角 $\theta$ 的圆锥立体角 |
| 6 | 立体角（全空间） | $\Omega = 4\pi$ sr | 球面全空间 |
| 7 | 普朗克黑体辐射定律（光谱辐射亮度） | $L_{e,\lambda} = \frac{2hc^2}{\lambda^5} \frac{1}{e^{hc/\lambda kT} - 1}$ | 单位波长、单位面积、单位立体角 |
| 8 | 斯特藩-玻尔兹曼定律 | $M_e = \sigma T^4$ | $\sigma = 5.67 \times 10^{-8}$ W/(m²·K⁴)，黑体总辐射出度 |
| 9 | 维恩位移定律 | $\lambda_{max} T = b$ | $b \approx 2898$ μm·K，峰值波长 |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 热电堆探测器 | Thermopile Detector | 基于温差电动势，宽光谱响应，用于激光功率测量 |
| 2 | 热释电探测器 | Pyroelectric Detector | 基于温度变化导致电极化，响应脉冲辐射 |
| 3 | 辐射计 | Radiometer | 测量辐射通量/照度的通用仪器 |
| 4 | 光谱辐射计 | Spectroradiometer | 测量光谱辐射亮度/照度随波长分布 |
| 5 | 黑体辐射源 | Blackbody Source | 校准用标准辐射源，温度可控 |
| 6 | 积分球 | Integrating Sphere | 已存在于知识库，用于测量总辐射通量 |
| 7 | 功率计探头 | Power Meter Head | 激光功率测量专用热释电或热电堆探头 |

### 5.2 光度学（Photometry）

> **定位**：以人眼视觉响应加权测量光，与辐射度学的区别在于引入了 "光谱光视效率函数" $V(\lambda)$。

#### 核心概念（12 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 光通量 | Luminous Flux ($\Phi_v$) | 人眼感知的光功率，单位流明 (lm) |
| 2 | 发光强度 | Luminous Intensity ($I_v$) | 单位立体角内的光通量，单位坎德拉 (cd) |
| 3 | 亮度 | Luminance ($L_v$) | 单位投影面积、单位立体角内的光通量，单位 cd/m² |
| 4 | 照度 | Illuminance ($E_v$) | 单位接收面积上的光通量，单位勒克斯 (lux = lm/m²) |
| 5 | 光出度 | Luminous Exitance ($M_v$) | 单位表面积发出的光通量，单位 lm/m² |
| 6 | 光谱光视效率 | Spectral Luminous Efficiency $V(\lambda)$ | 人眼对不同波长光的相对灵敏度，明视觉峰值 @ 555 nm |
| 7 | 光谱光视效率（暗视觉） | Scotopic Luminous Efficiency $V'(\lambda)$ | 暗视觉峰值 @ 507 nm |
| 8 | 流明 | Lumen (lm) | 光通量单位，1 lm = 1 cd·sr |
| 9 | 坎德拉 | Candela (cd) | 发光强度 SI 基本单位，1 cd = 1 lm/sr |
| 10 | 色温 | Correlated Color Temperature (CCT) | 光源颜色与黑体辐射最接近时的温度，单位 K |
| 11 | 显色指数 | Color Rendering Index (CRI) | 光源还原物体真实颜色的能力，满分 100 |
| 12 | 光视效能 | Luminous Efficacy | 光源光通量与电功率之比，单位 lm/W |

#### 核心公式/计算模型（7 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 光通量与辐射通量转换 | $\Phi_v = K_m \int_{380}^{780} \Phi_{e,\lambda} \cdot V(\lambda) \, d\lambda$ | $K_m = 683$ lm/W（明视觉最大光视效能） |
| 2 | 光视效能 | $\eta_v = \frac{\Phi_v}{P_{electrical}}$ | 单位 lm/W，包含电光转换和人眼加权 |
| 3 | 照度（点光源） | $E_v = \frac{I_v}{r^2} \cos\theta$ | 平方反比定律 |
| 4 | 亮度与发光强度 | $L_v = \frac{dI_v}{dA \cdot \cos\theta}$ | 投影面积定义 |
| 5 | 朗伯面亮度与出度 | $M_v = \pi L_v$ | 均匀漫射面 |
| 6 | 色温近似（ Wien 位移） | $T \approx \frac{2898 \, \mu m \cdot K}{\lambda_{peak}(\mu m)}$ | 仅适用于近似黑体光源 |
| 7 | CIE 1931 色度坐标 | $x = \frac{X}{X+Y+Z}, \quad y = \frac{Y}{X+Y+Z}$ | $X,Y,Z$ 为三刺激值 |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 照度计 | Lux Meter / Illuminance Meter | 测量照度（lux）的便携仪器 |
| 2 | 亮度计 | Luminance Meter | 测量亮度（cd/m²），用于显示/照明评估 |
| 3 | 分光辐射度计 | Spectroradiometer | 测量光谱辐射量，可计算色度、色温、CRI |
| 4 | 积分球光度计 | Integrating Sphere Photometer | 测量总光通量的标准设备 |
| 5 | 分布光度计 | Goniophotometer | 测量光源配光曲线（IES 文件生成） |
| 6 | 标准光源 | Standard Lamp | 校准用已知色温和光通量的光源 |
| 7 | 色度计 | Colorimeter | 测量色度坐标、色温、Delta E 的便携设备 |

### 5.3 光电探测器（Photodetectors）

> **定位**：将光信号转换为电信号，是光电子系统的"感官器官"。核心指标：响应度、速度、噪声、光谱范围。

#### 核心概念（15 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 光电二极管 | Photodiode (PD) | 基于 p-n 结内光电效应，反向偏置下光生电流与光功率成正比 |
| 2 | 量子效率 | Quantum Efficiency (QE) | 每个入射光子产生的电子-空穴对数，$\eta = \frac{N_e}{N_{photon}}$ |
| 3 | 响应度 | Responsivity ($R$) | 光电流与入射光功率之比，$R = \eta \cdot q / (h\nu)$，单位 A/W |
| 4 | 暗电流 | Dark Current | 无光照时的反向漏电流，决定探测器噪声下限 |
| 5 | 结电容 | Junction Capacitance | 限制探测器响应速度的 RC 时间常数 |
| 6 | 带宽 / 截止频率 | Bandwidth ($f_{3dB}$) | 响应度降至直流值 $1/\sqrt{2}$ 时的调制频率 |
| 7 | 雪崩光电二极管 (APD) | Avalanche Photodiode | 内部增益（M=10-100），通过雪崩倍增提高灵敏度 |
| 8 | 光电倍增管 (PMT) | Photomultiplier Tube | 极高增益（10⁶-10⁸），极弱光探测，需高压 |
| 9 | 单光子雪崩二极管 (SPAD) | Single-Photon Avalanche Diode | 工作在盖革模式，可检测单个光子 |
| 10 | 等效噪声功率 (NEP) | Noise Equivalent Power | 产生等于探测器噪声的信号所需光功率，单位 W/√Hz |
| 11 | 探测率 D* | Specific Detectivity | $D^* = \frac{\sqrt{A \cdot \Delta f}}{NEP}$，单位 Jones (cm·√Hz/W) |
| 12 | 噪声等效温差 (NETD) | Noise Equivalent Temperature Difference | 红外热像仪中可分辨的最小温差（知识库已有） |
| 13 | 光伏模式 / 光导模式 | Photovoltaic / Photoconductive Mode | 零偏（光伏）与反向偏置（光导）工作模式 |
| 14 | 电荷耦合器件 (CCD) | Charge-Coupled Device | 移位寄存器传输电荷的图像传感器（知识库已有基础） |
| 15 | 互补金属氧化物半导体 (CMOS) | CMOS Image Sensor | 主动像素读出，知识库已有基础 |

#### 核心公式/计算模型（8 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | 光电流 | $I_{ph} = R \cdot P_{opt} = \eta \cdot \frac{q \lambda}{hc} \cdot P_{opt}$ | $P_{opt}$：入射光功率 |
| 2 | 响应度与量子效率 | $R = \eta \cdot \frac{q}{h\nu} = \eta \cdot \frac{q\lambda}{hc}$ | $\lambda$ 单位 μm 时，$R \approx \eta \cdot \lambda / 1.24$（A/W） |
| 3 | 光电二极管带宽 | $f_{3dB} = \frac{1}{2\pi R_L C_j}$ | $R_L$：负载电阻；$C_j$：结电容 |
| 4 | APD 增益 | $M = \frac{1}{1 - (V/V_{br})^n}$ | $V_{br}$：击穿电压；$n$：材料参数 |
| 5 | 散粒噪声电流 | $i_{shot} = \sqrt{2qI_{ph}B}$ | $B$：带宽；与光电流成正比 |
| 6 | 热噪声（Johnson） | $i_{thermal} = \sqrt{\frac{4kTB}{R_L}}$ | 与温度、负载电阻有关 |
| 7 | NEP（噪声等效功率） | $NEP = \frac{i_{noise}}{R} = \frac{\sqrt{2qI_{ph}B + \frac{4kTB}{R_L}}}{R}$ | 总噪声电流除以响应度 |
| 8 | 探测率 D* | $D^* = \frac{\sqrt{A \cdot B}}{NEP} = R \cdot \sqrt{\frac{A}{2qI_{ph} + 4kT/R_L}}$ | 归一化到面积和带宽的探测能力 |

#### 典型设备/组件（8 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 硅光电二极管 | Silicon Photodiode | 可见到近红外（400-1000 nm），低成本 |
| 2 | InGaAs 光电二极管 | InGaAs Photodiode | 近红外（900-1700 nm），光通信标准 |
| 3 | 雪崩光电二极管 (APD) | APD | 高灵敏度接收，用于长距离光纤通信 |
| 4 | 光电倍增管 (PMT) | PMT | 极弱光、快速响应，用于荧光光谱、辐射测量 |
| 5 | 单光子雪崩二极管 (SPAD) | SPAD | 量子光学、LiDAR、时间分辨荧光 |
| 6 | 焦平面阵列 (FPA) | Focal Plane Array | 成像探测器阵列，如 InGaAs FPA、MCT FPA（知识库已有） |
| 7 | 微测辐射热计 | Microbolometer | 非制冷红外探测，热敏电阻阵列（知识库已有） |
| 8 | 平衡探测器 | Balanced Detector | 两路相减抑制共模噪声，用于相干光通信 |

### 5.4 光调制（Optical Modulation）

> **定位**：以电/声/磁信号控制光的振幅、相位、频率或偏振，是光通信、光计算和激光系统的核心功能。

#### 核心概念（14 个）

| 序号 | 中文术语 | 英文术语 | 定义 |
|------|---------|---------|------|
| 1 | 电光效应 | Electro-Optic Effect | 电场改变材料折射率的现象，包括 Pockels（线性）和 Kerr（二次）效应 |
| 2 | 泡克耳斯效应 | Pockels Effect | 线性电光效应，$\Delta n \propto E$，仅存在于非中心对称晶体 |
| 3 | 克尔效应 | Kerr Effect | 二次电光效应，$\Delta n \propto E^2$，所有材料均存在 |
| 4 | 声光效应 | Acousto-Optic Effect | 声波引起材料密度/折射率周期性变化，使光发生衍射 |
| 5 | 声光调制器 | Acousto-Optic Modulator (AOM) | 利用声光效应调制光强或偏转光束方向 |
| 6 | 磁光效应 | Magneto-Optic Effect | 磁场导致材料光学性质变化，如法拉第旋转 |
| 7 | 法拉第旋转 | Faraday Rotation | 线偏振光在磁场中传播时偏振面旋转，旋转角 $\theta = V \cdot B \cdot L$ |
| 8 | 相位调制 | Phase Modulation | 改变光载波的相位，保持振幅不变 |
| 9 | 振幅调制 | Amplitude Modulation | 改变光载波的振幅，如 Mach-Zehnder 调制器 |
| 10 | 强度调制 | Intensity Modulation | 直接调制光源电流改变输出光强 |
| 11 | 外调制 / 内调制 | External / Internal Modulation | 外调制：光源后加调制器；内调制：直接调制光源 |
| 12 | 半波电压 $V_\pi$ | Half-Wave Voltage | 电光调制器产生 $\pi$ 相位变化所需的电压 |
| 13 | 啁啾 | Chirp | 光脉冲频率随时间变化的现象，内调制激光器常见 |
| 14 | 消光比 | Extinction Ratio | 调制器"开"态与"关"态的光强比，单位 dB |

#### 核心公式/计算模型（7 个）

| 序号 | 公式名称 | 表达式 | 说明 |
|------|---------|--------|------|
| 1 | Pockels 效应折射率变化 | $\Delta\left(\frac{1}{n^2}\right) = r_{ij} E_j$ | $r_{ij}$：电光张量系数 |
| 2 | 线性电光相位调制 | $\Delta\phi = \frac{2\pi}{\lambda} \cdot \frac{1}{2} n^3 r_{63} E \cdot L = \frac{\pi}{\lambda} n^3 r_{63} \frac{V}{d} L$ | $V$：施加电压；$d$：电极间距；$L$：作用长度 |
| 3 | 半波电压 | $V_\pi = \frac{\lambda d}{n^3 r_{63} L}$ | 产生 $\pi$ 相位变化的电压 |
| 4 | Mach-Zehnder 振幅调制 | $I_{out} = I_{in} \cos^2\left(\frac{\Delta\phi}{2}\right) = I_{in} \cos^2\left(\frac{\pi V}{2V_\pi}\right)$ | 推挽式结构 |
| 5 | 声光衍射角（布拉格） | $\sin\theta_B = \frac{\lambda}{2\Lambda}$ | $\Lambda$：声波波长；$\theta_B$：布拉格角 |
| 6 | 法拉第旋转角 | $\theta = V \cdot B \cdot L$ | $V$：维尔德常数；$B$：磁感应强度；$L$：传播长度 |
| 7 | 消光比（dB） | $ER = 10 \log_{10}\left(\frac{I_{on}}{I_{off}}\right)$ | 理想值 > 20 dB |

#### 典型设备/组件（7 个）

| 序号 | 设备/组件 | 英文 | 说明 |
|------|----------|------|------|
| 1 | 电光调制器 (EOM) | Electro-Optic Modulator | 基于 LiNbO₃ 或聚合物，高速相位/振幅调制 |
| 2 | Mach-Zehnder 调制器 | Mach-Zehnder Modulator (MZM) | 集成波导型电光振幅调制器，光通信核心器件 |
| 3 | 声光调制器 (AOM) | Acousto-Optic Modulator | 调制光强或偏转光束，用于 Q 开关和光束扫描 |
| 4 | 声光偏转器 | Acousto-Optic Deflector (AOD) | 改变声波频率实现光束角度扫描 |
| 5 | 法拉第隔离器 | Faraday Isolator | 利用法拉第旋转实现单向光传输，保护激光器 |
| 6 | 电吸收调制器 (EAM) | Electro-Absorption Modulator | 基于量子限制斯塔克效应，与 DFB 激光器单片集成 |
| 7 | 液晶调制器 / 空间光调制器 | Liquid Crystal Modulator / SLM | 电控双折射实现相位/振幅调制 |

### 5.5 光电子与辐射度学：可扩展为知识库笔记的骨架结构

```
📁 10-concepts/
├── ...（现有 + 激光/非成像概念）
├── 146-radiant-flux.md                    # 辐射通量
├── 147-radiant-intensity.md              # 辐射强度
├── 148-radiance.md                       # 辐射亮度
├── 149-radiant-exitance.md               # 辐射出度
├── 150-irradiance.md                     # 辐射照度
├── 151-spectral-radiant-quantity.md     # 光谱辐射量
├── 152-solid-angle.md                    # 立体角
├── 153-lambertian-surface.md             # 朗伯体（与现有漫射关联）
├── 154-blackbody-radiation.md            # 黑体辐射（与现有普朗克公式关联）
├── 155-emissivity.md                     # 发射率（已存在，可扩展）
├── 156-kirchhoff-law.md                  # 基尔霍夫热辐射定律
├── 157-luminous-flux.md                  # 光通量
├── 158-luminous-intensity.md             # 发光强度
├── 159-luminance.md                      # 亮度
├── 160-illuminance.md                    # 照度
├── 161-spectral-luminous-efficiency.md # 光谱光视效率 V(λ)
├── 162-candela.md                        # 坎德拉
├── 163-lumen.md                          # 流明
├── 164-cri.md                            # 显色指数 CRI
├── 165-luminous-efficacy.md             # 光视效能
├── 166-photodiode.md                     # 光电二极管
├── 167-quantum-efficiency.md            # 量子效率
├── 168-responsivity.md                   # 响应度
├── 169-dark-current.md                   # 暗电流
├── 170-avalanche-photodiode.md          # 雪崩光电二极管 APD
├── 171-photomultiplier-tube.md          # 光电倍增管 PMT
├── 172-spad.md                           # 单光子雪崩二极管
├── 173-nep.md                            # 等效噪声功率
├── 174-detectivity-d-star.md            # 探测率 D*
├── 175-electro-optic-effect.md          # 电光效应
├── 176-pockels-effect.md                 # 泡克耳斯效应
├── 177-kerr-effect.md                    # 克尔效应
├── 178-acousto-optic-effect.md           # 声光效应
├── 179-magneto-optic-effect.md          # 磁光效应
├── 180-faraday-rotation.md              # 法拉第旋转
├── 181-phase-modulation.md              # 相位调制
├── 182-amplitude-modulation.md          # 振幅调制
├── 183-extinction-ratio.md              # 消光比
└── 184-chirp.md                          # 啁啾

📁 20-formulas/
├── ...（现有 + 激光/非成像公式）
├── 044-radiance-definition.md            # 辐射亮度定义
├── 045-lambertian-radiant-exitance.md   # 朗伯面辐射出度
├── 046-irradiance-inverse-square.md    # 照度平方反比
├── 047-stefan-boltzmann-law.md          # 斯特藩-玻尔兹曼定律
├── 048-wien-displacement-law.md         # 维恩位移定律
├── 049-luminous-flux-conversion.md      # 光通量-辐射通量转换
├── 050-photocurrent.md                  # 光电流
├── 051-responsivity-quantum-efficiency.md # 响应度与 QE
├── 052-photodiode-bandwidth.md          # 光电二极管带宽
├── 053-nep-noise.md                     # NEP 公式
├── 054-detectivity-d-star.md            # D* 公式
├── 055-pockels-phase-shift.md           # Pockels 相位偏移
├── 056-half-wave-voltage.md             # 半波电压
├── 057-mach-zehnder-modulation.md       # MZM 调制特性
├── 058-faraday-rotation-angle.md        # 法拉第旋转角
└── 059-acousto-optic-bragg-angle.md     # 声光布拉格角

📁 30-domains/
├── ...（现有 + 激光/非成像领域）
├── 014-radiometry-photometry.md         # 辐射度学与光度学领域
├── 015-optoelectronic-detection.md      # 光电探测领域
├── 016-optical-modulation.md            # 光调制领域
└── 017-infrared-systems.md              # 红外系统领域（与现有红外成像关联）

📁 40-devices/
├── ...（现有 + 激光/非成像设备）
├── 048-thermopile-detector.md           # 热电堆探测器
├── 049-pyroelectric-detector.md         # 热释电探测器
├── 050-radiometer.md                    # 辐射计
├── 051-blackbody-source.md             # 黑体辐射源
├── 052-lux-meter.md                     # 照度计
├── 053-luminance-meter.md               # 亮度计
├── 054-goniophotometer.md              # 分布光度计
├── 055-silicon-photodiode.md            # 硅光电二极管
├── 056-ingaas-photodiode.md             # InGaAs 光电二极管
├── 057-apd-device.md                    # 雪崩光电二极管（设备级）
├── 058-pmt-device.md                    # 光电倍增管
├── 059-spad-device.md                   # 单光子雪崩二极管
├── 060-balanced-detector.md             # 平衡探测器
├── 061-linbo3-modulator.md              # 铌酸锂调制器
├── 062-mach-zehnder-modulator.md       # Mach-Zehnder 调制器
├── 063-aom-device.md                    # 声光调制器
├── 064-faraday-isolator.md              # 法拉第隔离器
├── 065-eam-device.md                    # 电吸收调制器
└── 066-lc-slm.md                        # 液晶空间光调制器
```

---

## 6. 建议的知识库扩展目录树（具体到文件级别）

综合以上四个任务，以下是建议在现有 OptiBench 知识库中新增的内容目录树。命名遵循现有约定：`数字编号 + 英文 kebab-case`，编号从 `081` 开始延续现有概念编号。

```
OpticKnowledgeSpace/
│
├── 📁 10-concepts/
│   ├── ...（现有 000-080 及额外文件保留）
│   ├── 081-light-extraction-efficiency.md
│   ├── 082-luminous-intensity-distribution.md
│   ├── 083-lambertian-emitter.md
│   ├── 084-etendue.md
│   ├── 085-concentration-ratio.md
│   ├── 086-acceptance-angle.md
│   ├── 087-compound-parabolic-concentrator.md
│   ├── 088-light-guide-plate.md
│   ├── 089-microlens-array.md
│   ├── 090-brightness-enhancement-film.md
│   ├── 091-quantum-dot-enhancement.md
│   ├── 092-waveguide-display.md
│   ├── 093-exit-pupil-expansion.md
│   ├── 094-coupling-efficiency.md
│   ├── 095-mode-matching.md
│   ├── 096-fiber-alignment-tolerance.md
│   ├── 097-grating-coupler.md
│   ├── 098-total-internal-reflection-lens.md
│   ├── 099-freeform-optics.md
│   ├── 100-solar-tracker.md
│   ├── 101-stimulated-emission.md
│   ├── 102-population-inversion.md
│   ├── 103-optical-resonator.md
│   ├── 104-gain-medium.md
│   ├── 105-laser-pumping.md
│   ├── 106-laser-threshold.md
│   ├── 107-longitudinal-mode.md
│   ├── 108-transverse-mode.md
│   ├── 109-quality-factor-q.md
│   ├── 110-q-switching.md
│   ├── 111-mode-locking.md
│   ├── 112-saturable-absorber.md
│   ├── 113-laser-linewidth.md
│   ├── 114-coherence-length.md
│   ├── 115-gaussian-beam.md
│   ├── 116-beam-waist.md
│   ├── 117-rayleigh-range.md
│   ├── 118-beam-divergence.md
│   ├── 119-beam-quality-m2.md
│   ├── 120-q-parameter.md
│   ├── 121-focused-spot-size.md
│   ├── 122-bessel-beam.md
│   ├── 123-spatial-light-modulator.md
│   ├── 124-single-mode-fiber.md
│   ├── 125-multi-mode-fiber.md
│   ├── 126-graded-index-fiber.md
│   ├── 127-normalized-frequency-v.md
│   ├── 128-mode-field-diameter.md
│   ├── 129-fiber-attenuation.md
│   ├── 130-material-dispersion.md
│   ├── 131-waveguide-dispersion.md
│   ├── 132-nonlinear-effects.md
│   ├── 133-edfa.md
│   ├── 134-optical-waveguide.md
│   ├── 135-evanescent-field.md
│   ├── 136-effective-refractive-index.md
│   ├── 137-directional-coupler.md
│   ├── 138-coupling-length.md
│   ├── 139-mach-zehnder-interferometer.md
│   ├── 140-microring-resonator.md
│   ├── 141-free-spectral-range.md
│   ├── 142-quality-factor-microring.md
│   ├── 143-electro-optic-modulator.md
│   ├── 144-thermo-optic-tuning.md
│   ├── 145-photonic-integrated-circuit.md
│   ├── 146-radiant-flux.md
│   ├── 147-radiant-intensity.md
│   ├── 148-radiance.md
│   ├── 149-radiant-exitance.md
│   ├── 150-irradiance.md
│   ├── 151-spectral-radiant-quantity.md
│   ├── 152-solid-angle.md
│   ├── 153-lambertian-surface.md
│   ├── 154-blackbody-radiation.md
│   ├── 155-emissivity.md
│   ├── 156-kirchhoff-law.md
│   ├── 157-luminous-flux.md
│   ├── 158-luminous-intensity.md
│   ├── 159-luminance.md
│   ├── 160-illuminance.md
│   ├── 161-spectral-luminous-efficiency.md
│   ├── 162-candela.md
│   ├── 163-lumen.md
│   ├── 164-cri.md
│   ├── 165-luminous-efficacy.md
│   ├── 166-photodiode.md
│   ├── 167-quantum-efficiency.md
│   ├── 168-responsivity.md
│   ├── 169-dark-current.md
│   ├── 170-avalanche-photodiode.md
│   ├── 171-photomultiplier-tube.md
│   ├── 172-spad.md
│   ├── 173-nep.md
│   ├── 174-detectivity-d-star.md
│   ├── 175-electro-optic-effect.md
│   ├── 176-pockels-effect.md
│   ├── 177-kerr-effect.md
│   ├── 178-acousto-optic-effect.md
│   ├── 179-magneto-optic-effect.md
│   ├── 180-faraday-rotation.md
│   ├── 181-phase-modulation.md
│   ├── 182-amplitude-modulation.md
│   ├── 183-extinction-ratio.md
│   └── 184-chirp.md
│
├── 📁 20-formulas/
│   ├── ...（现有 000-016 及额外文件保留）
│   ├── 017-etendue-conservation.md
│   ├── 018-fresnel-reflectance.md
│   ├── 019-lambert-cosine-law.md
│   ├── 020-cpc-concentration-limit.md
│   ├── 021-illumination-uniformity.md
│   ├── 022-gaussian-coupling-lateral.md
│   ├── 023-gaussian-coupling-angular.md
│   ├── 024-fiber-na.md
│   ├── 025-insertion-loss-db.md
│   ├── 026-laser-threshold-condition.md
│   ├── 027-longitudinal-mode-spacing.md
│   ├── 028-cavity-stability-condition.md
│   ├── 029-gaussian-beam-waist.md
│   ├── 030-rayleigh-range.md
│   ├── 031-beam-divergence-angle.md
│   ├── 032-focused-spot-diameter.md
│   ├── 033-depth-of-focus.md
│   ├── 034-beam-quality-m2.md
│   ├── 035-fiber-na.md
│   ├── 036-single-mode-condition.md
│   ├── 037-fiber-attenuation-db.md
│   ├── 038-pulse-broadening-dispersion.md
│   ├── 039-kerr-nonlinear-index.md
│   ├── 040-microring-resonance.md
│   ├── 041-free-spectral-range.md
│   ├── 042-microring-q-factor.md
│   ├── 043-pockels-phase-modulation.md
│   ├── 044-radiance-definition.md
│   ├── 045-lambertian-radiant-exitance.md
│   ├── 046-irradiance-inverse-square.md
│   ├── 047-stefan-boltzmann-law.md
│   ├── 048-wien-displacement-law.md
│   ├── 049-luminous-flux-conversion.md
│   ├── 050-photocurrent.md
│   ├── 051-responsivity-quantum-efficiency.md
│   ├── 052-photodiode-bandwidth.md
│   ├── 053-nep-noise.md
│   ├── 054-detectivity-d-star.md
│   ├── 055-pockels-phase-shift.md
│   ├── 056-half-wave-voltage.md
│   ├── 057-mach-zehnder-modulation.md
│   ├── 058-faraday-rotation-angle.md
│   └── 059-acousto-optic-bragg-angle.md
│
├── 📁 30-domains/
│   ├── ...（现有 000-005 保留）
│   ├── 006-illumination-design.md
│   ├── 007-solar-concentrator.md
│   ├── 008-display-optics.md
│   ├── 009-optical-communication.md
│   ├── 010-laser-systems.md
│   ├── 011-fiber-optic-communication.md
│   ├── 012-integrated-photonics.md
│   ├── 013-laser-material-processing.md
│   ├── 014-radiometry-photometry.md
│   ├── 015-optoelectronic-detection.md
│   ├── 016-optical-modulation.md
│   └── 017-infrared-systems.md
│
└── 📁 40-devices/
    ├── ...（现有 000-017 保留）
    ├── 018-led-chip.md
    ├── 019-fresnel-lens.md
    ├── 020-cpc-concentrator.md
    ├── 021-microlens-array-film.md
    ├── 022-prism-sheet.md
    ├── 023-quantum-dot-film.md
    ├── 024-fiber-collimator.md
    ├── 025-fiber-v-groove.md
    ├── 026-optical-isolator.md
    ├── 027-on-chip-grating-coupler.md
    ├── 028-diffractive-waveguide.md
    ├── 029-solid-state-laser.md
    ├── 030-laser-diode.md
    ├── 031-fiber-laser.md
    ├── 032-co2-laser.md
    ├── 033-acousto-optic-q-switch.md
    ├── 034-electro-optic-modulator.md
    ├── 035-sesam.md
    ├── 036-beam-expander.md
    ├── 037-spatial-light-modulator.md
    ├── 038-beam-profiler.md
    ├── 039-smf-28.md
    ├── 040-edfa.md
    ├── 041-fiber-coupler.md
    ├── 042-fiber-bragg-grating.md
    ├── 043-optical-circulator.md
    ├── 044-silicon-photonics-pic.md
    ├── 045-microring-modulator.md
    ├── 046-arrayed-waveguide-grating.md
    ├── 047-tunable-laser.md
    ├── 048-thermopile-detector.md
    ├── 049-pyroelectric-detector.md
    ├── 050-radiometer.md
    ├── 051-blackbody-source.md
    ├── 052-lux-meter.md
    ├── 053-luminance-meter.md
    ├── 054-goniophotometer.md
    ├── 055-silicon-photodiode.md
    ├── 056-ingaas-photodiode.md
    ├── 057-apd-device.md
    ├── 058-pmt-device.md
    ├── 059-spad-device.md
    ├── 060-balanced-detector.md
    ├── 061-linbo3-modulator.md
    ├── 062-mach-zehnder-modulator.md
    ├── 063-aom-device.md
    ├── 064-faraday-isolator.md
    ├── 065-eam-device.md
    └── 066-lc-slm.md
```

---

## 7. 与现有 v4.0 五模块结构的融合建议

### 7.1 融合原则

1. **不破坏现有模块**：模块甲~戊保持不动，新增内容作为独立模块或跨模块通用资源引入。
2. **渐进式扩展**：新增内容先从 `10-concepts/`、`20-formulas/`、`30-domains/`、`40-devices/` 原子笔记层开始填充，再通过模块 MOC 索引引用，而非立即重构模块目录。
3. **跨模块链接**：利用 Obsidian 双链语法 `[[...]]` 建立新内容与现有内容的关联（如 `[[高斯光束]]` 链接到 `[[焦距]]` 的聚焦公式、`[[光纤 NA]]` 链接到 `[[数值孔径]]`）。
4. **通用基础优先**：新增内容中属于通用基础的概念（如辐射度学、激光基本原理）可提升为模块甲/乙的扩展内容，而非仅限新模块。

### 7.2 新增模块建议：七模块环形架构

```
┌─────────────────────────────────────────────────────────────┐
│                    模块甲｜桥接（数学/物理/语言）              │
│                         ↓ 支撑所有模块                        │
├─────────────────────────────────────────────────────────────┤
│  模块乙｜几何光学与一阶成像  →  模块丙｜波动光学与傅里叶成像  │
│  （近轴、成像、孔径、像差）      （干涉、衍射、PSF/OTF/MTF）  │
│         ↓                              ↓                     │
│  ┌──────────────┐              ┌──────────────┐           │
│  │ 模块丁｜光谱学 │ ←────────→ │ 模块戊｜光学设计 │           │
│  │ （色散、光栅、  │   交叉：     │ （闭环、优化、   │           │
│  │  分辨率、仪器） │  MTF/分辨率  │  容差、评价）   │           │
│  └──────────────┘              └──────────────┘           │
│         ↓                              ↓                     │
│  ┌────────────────────────────────────────────────────┐    │
│  │  模块己｜激光与光子学  ←────→  模块庚｜辐射度学与光电子  │    │
│  │  （激光原理、高斯光束、   交叉：     （辐射度学、光电探测、 │    │
│  │   光纤、集成光子学）     光调制      光调制、光度学）      │    │
│  └────────────────────────────────────────────────────┘    │
│                         ↓                                   │
│              ┌──────────────────┐                          │
│              │   90-综合项目      │                          │
│              │ （成像/激光/光谱/  │                          │
│              │  光电子跨域项目）  │                          │
│              └──────────────────┘                          │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 内容放入现有模块 vs. 新建模块的映射

| 新增内容 | 建议归属 | 理由 | 与现有模块的关联 |
|---------|---------|------|----------------|
| 受激辐射、粒子数反转、谐振腔 | **模块己｜激光与光子学** | 全新领域，不属于成像 | 与模块丙的「干涉、相干」关联 |
| 高斯光束、光束质量 M²、聚焦 | **模块己** | 激光专属内容 | 与模块乙的「焦距、F值、数值孔径」深度关联，可双向链接 |
| 单模/多模光纤、色散、EDFA | **模块己** | 光纤光子学核心 | 与模块丁的「光谱分辨率」关联（光谱测量用光纤） |
| 波导、耦合器、微环谐振器、MZI | **模块己** | 集成光子学专属 | 与模块丙的「干涉」关联；与模块丁的「光栅」关联 |
| 辐射通量、辐射亮度、照度、立体角 | **模块庚｜辐射度学与光电子** | 基础物理量，但现有知识库极度缺失 | 建议作为模块甲的扩展内容（通用基础）或模块庚核心 |
| 黑体辐射、发射率、普朗克公式 | **模块庚 / 模块甲扩展** | 已有普朗克公式，但辐射度学框架缺失 | 与模块丁的「色温、光谱功率分布」深度关联 |
| 光电二极管、APD、PMT、SPAD、NEP、D* | **模块庚** | 光电子探测器专属 | 与模块乙的「传感器、CMOS」关联；与模块戊的「像质评价」关联（探测器是系统终端） |
| 电光/声光/磁光效应、光调制 | **模块庚** | 光电子调制专属 | 与模块丙的「偏振」关联；与模块己的「激光器」关联（Q 开关、锁模） |
| 光度学（流明、坎德拉、照度、CRI） | **模块庚 / 通用基础** | 照明/显示专属 | 与模块丁的「色温、色度图」深度关联 |
| 照明光学（光提取、配光曲线、均匀性） | **30-domains/006 + 40-devices 扩展** | 非成像领域，但通用性强 | 与模块乙的「照明方式」关联（工业视觉照明） |
| 太阳能聚光（CPC、接受角、聚光比） | **30-domains/007** | 非成像专属 | 与模块乙的「数值孔径、F值」关联（聚光类比） |
| 显示光学（背光、导光板、波导、量子点） | **30-domains/008** | 非成像专属 | 与模块丁的「色度图、色温」关联；与模块丙的「衍射光栅」关联（出瞳扩展） |
| 光通信耦合光学（耦合效率、对准、光栅耦合） | **30-domains/009** | 非成像专属 | 与模块乙的「数值孔径」关联（光纤 NA）；与模块己的「光纤」关联 |

### 7.4 模块己与模块庚的详细规格建议

#### 模块己｜激光与光子学

| 属性 | 内容 |
|------|------|
| **目标** | 理解激光产生原理、高斯光束传播特性、光纤传输与放大、集成光子芯片基础，建立从激光器到光子芯片的完整认知 |
| **先修** | 模块甲（基础）+ 模块乙（几何光学）+ 模块丙（波动光学） |
| **核心概念** | 受激辐射、粒子数反转、谐振腔、纵模/横模、Q开关、锁模、高斯光束、M²、光纤模式、色散、非线性、波导、微环、MZI、光栅耦合器 |
| **核心公式** | 激光阈值条件、高斯光束半径/瑞利范围/发散角、聚焦光斑、光纤 NA/单模条件、微环共振/FSR、Pockels相位调制 |
| **预计时长** | 35-50 小时 |
| **评估方式** | 计算高斯光束通过透镜的聚焦参数；设计一个微环谐振器的 FSR；解释光纤单模条件 |
| **产出物** | 高斯光束传播仿真（Python）；光纤色散计算表；微环谐振器设计草图 |

#### 模块庚｜辐射度学与光电子

| 属性 | 内容 |
|------|------|
| **目标** | 掌握光的物理量测量体系（辐射度学+光度学）、光电探测器原理与选型、光调制技术基础，建立光电子系统的"感官+控制"认知 |
| **先修** | 模块甲（基础）+ 模块乙（传感器部分） |
| **核心概念** | 辐射通量/强度/亮度/照度、朗伯体、黑体辐射、光通量/发光强度/亮度/照度、光谱光视效率、光电二极管/量子效率/响应度、APD/PMT/SPAD、NEP/D*、电光/声光/磁光效应、相位/振幅调制 |
| **核心公式** | 辐射亮度/照度定义、普朗克定律、斯特藩-玻尔兹曼定律、光通量-辐射通量转换、光电流/响应度/量子效率、NEP/D*、Pockels相位偏移、半波电压、MZM调制特性 |
| **预计时长** | 25-40 小时 |
| **评估方式** | 给定光源光谱计算光通量；比较光电二极管与 APD 的灵敏度；计算电光调制器的半波电压 |
| **产出物** | 辐射度学-光度学单位换算表；光电探测器选型决策树；光调制器对比表 |

### 7.5 关键跨模块双链建议

以下是在 Obsidian 中应建立的核心双向链接（示例）：

```markdown
# 在 [[高斯光束]] 笔记中
- 高斯光束通过透镜聚焦时，可使用 [[几何光学]] 的薄透镜公式估算腰斑位置：参见 [[20-formulas/000-thin-lens-gauss|薄透镜高斯公式]]
- 聚焦极限光斑大小受 [[衍射极限]] 限制：参见 [[10-concepts/025-diffraction-limit|衍射极限]]
- 聚焦光斑大小与 [[数值孔径]] 的关系：参见 [[10-concepts/006-数值孔径|数值孔径]]
- 光束质量 M² 是实际光束与理想 [[艾里斑]] 的偏离度量：参见 [[10-concepts/027-airy-disk|艾里斑]]

# 在 [[光纤 NA]] 笔记中
- 光纤 NA 与 [[10-concepts/006-数值孔径|数值孔径]] 的定义一致，但应用语境不同
- 光纤模式分析基于 [[波动光学]]：参见 [[modules/30-wave-optics/README|模块丙]]
- 光纤放大器 [[EDFA]] 用于 [[光通信]]：参见 [[30-domains/009-optical-communication|光通信]]
- 光纤色散限制 [[光谱分辨率]]：参见 [[10-concepts/074-spectral-resolution|光谱分辨率]]

# 在 [[光电二极管]] 笔记中
- 光电二极管是 [[CMOS 传感器]] 的核心单元：参见 [[40-devices/003-global-shutter-cmos|全局快门 CMOS]]
- 响应度与 [[量子效率]] 的换算涉及 [[光子能量]]：参见 [[10-concepts/000-refractive-index|折射率]]（或新建波长-频率-能量）
- 探测器性能评价使用 [[MTF]]：参见 [[10-concepts/034-mtf|MTF]]（探测器 MTF 与光学 MTF 级联）
- 暗电流噪声与 [[读出噪声]] 共同决定系统信噪比：参见 [[10-concepts/061-读出噪声|读出噪声]]
```

### 7.6 实施优先级建议

| 阶段 | 优先级 | 内容 | 预估工作量 | 依赖 |
|------|--------|------|-----------|------|
| **Phase 1** | P0 | 创建模块己、庚的 `README.md` 和 MOC 索引文件 | 4h | 现有模块结构稳定 |
| **Phase 1** | P0 | 填充通用基础概念（辐射度学、发射率、黑体辐射扩展） | 8h | 无 |
| **Phase 2** | P1 | 创建激光光学核心概念笔记（101-123） | 12h | Phase 1 |
| **Phase 2** | P1 | 创建光纤与集成光子学核心概念笔记（124-145） | 12h | Phase 1 |
| **Phase 3** | P2 | 创建光电探测器与光调制核心概念笔记（166-184） | 10h | Phase 1 |
| **Phase 3** | P2 | 创建非成像光学核心概念笔记（081-100） | 10h | Phase 1 |
| **Phase 4** | P3 | 创建对应公式笔记（017-059） | 15h | Phase 2-3 |
| **Phase 5** | P4 | 创建领域和设备笔记 | 10h | Phase 2-4 |
| **Phase 6** | P5 | 建立跨模块双链、更新知识地图 | 6h | Phase 1-5 |

> **总计新增文件**：约 **184 个概念** + **59 个公式** + **17 个领域** + **66 个设备** = **326 个新文件**，可在 3-4 个月内分阶段完成。

---

*报告结束。本报告作为 OptiBench 光学知识库从"成像光学"向"完整光学体系"扩展的顶层设计文档，建议在 `90-maps/` 中归档为 `knowledge-expansion-plan-laser-photonics-radiometry.md`。*
