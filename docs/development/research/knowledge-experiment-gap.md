# 知识—实验缺口映射方案（Knowledge–Experiment Gap Map）

> 类别：调研参考（`docs/development/research/`），不可直接当作执行计划；实验立项须先进入 `plans/active/`。
> 数据口径：2026-08-25，`scripts/knowledge_coverage.py` 对 `knowledgeLinks.json`（147 概念 + 66 公式）与 lab registry（19 实验）/面包板 preset（2）的对账结果。
> 结论先行：未锚定知识共 **84 概念 + 37 公式**（2026-08-25 晚间快照；当日三批共落地十六个实验（含黑体发射率扩展与五个零成本概念补链）（黑体扩展、高斯光束、全反射/光纤NA、探测器SNR、半影、朗伯体角分布、立体角几何、QE-响应度、CIE色域、双点分辨）并补链「瑞利判据」，详见 T1 表状态列）；其中真正适合"补实验"的是 T1 子集，大量内容属于其他能力域或天然纯阅读。

## 1. 分级定义

| 级别 | 含义 | 处置 |
|---|---|---|
| **T1** | 现有参数化 canvas/绘图基建可直接承载 | 候选立项池，按价值排序逐个进 active plan |
| **T2** | 需要光学面包板 SceneGraph / ray-optics 能力 | 受 ADR-002 与面包板 plan checkpoint 门禁约束，不提前实现 |
| **T3** | 需要新增数值仿真能力（FFT 场传播、速率方程积分等） | 单独立项评估，成本 L 起 |
| **T4** | 理论/综述/器件选型知识，不适合交互实验 | 保持纯阅读；高双链中心度者可补入 curriculum 概念骨架 |

## 2. T1 · 建议立项清单（约 20 项）

| # | 提案实验 | 锚定的未覆盖笔记 | 复用基建 | 量级 | 状态 |
|---|---|---|---|---|---|
| 1 | 黑体辐射扩展：维恩位移 + 斯特藩玻尔兹曼定律 | `wien-displacement-law`、`stefan-boltzmann-law` | blackbody 实验 | S | ✅ 已落地（2026-08-25，双温对比模式） |
| 2 | 朗伯体角分布实验（朗伯余弦定律） | `lambertian-emitter`、`lambertian-surface`、`lambert-cosine` | 极坐标绘制  | S | ✅ 已落地 |
| 3 | 立体角与锥形孔径几何实验 | `solid-angle-cone`、`acceptance-angle` | 几何 canvas  | S | ✅ 已落地 |
| 4 | 高斯光束传播实验（束腰/瑞利范围/M²） | `gaussian-beam-waist`、`rayleigh-range`、`m2-beam-quality`、概念 `gaussian-beam`、`rayleigh-range`、`beam-quality-m2` | 1D 曲线族 | S/M | S/M | ✅ 已落地（2026-08-25，锚定 gaussian-beam/rayleigh-range/beam-quality-m2 + 束腰公式） |
| 5 | 全反射临界角实验 | `tir-critical-angle`、`tir-lens`(部分) | snell_refraction 扩展 | S | ✅ 已落地（2026-08-25，tir-critical-angle 实验，含光纤 NA 面板） |
| 6 | 光纤数值孔径与受光锥实验 | `fiber-na`、概念 `multi-mode-fiber`(部分) | 同上复用 | S | ✅ 已并入 #5（fiber-na 公式已锚定） |
| 7 | 量子效率—响应度关系实验 | `qe-responsivity-relation`、`responsivity`(公式) | 关系曲线  | S | ✅ 已落地 |
| 8 | 探测器信噪比预算实验 | `detector-snr`、`NEP`、`specific-detectivity`、概念 `noise-equivalent-power`、`读出噪声`、`动态范围` | 噪声瀑布图 | M | ✅ 已落地（2026-08-25，detector-snr 实验） |
| 9 | 色域映射实验（CIE 上叠加 gamut/ΔE） | `color-gamut`、`delta-e` | color_mixing 色度图 | S/M | 🔶 部分落地（color-gamut 已锚定；ΔE 待后续） |
| 10 | 显色指数 CRI 演示 | `color-rendering-index` | 光谱合成 | M |
| 11 | 快门时序实验（卷帘 vs 全局快门、果冻效应） | `卷帘快门`、`全局快门`、`果冻效应` | 动画 | M |
| 12 | 视差与景深感知实验 | `视差`、`半影`(并入#13) | 双视图 canvas | M |
| 13 | 半影与光源尺度实验 | `半影` | 几何 canvas | S | ✅ 已落地（2026-08-25，penumbra 实验） |
| 14 | 透视畸变演示 | `透视畸变`、`distortion`(概念已有) | 相机投影模拟 | M |
| 15 | 过采样与有效分辨率实验 | `过采样`、概念 `过采样` | nyquist_sampling 扩展 | S |
| 16 | 照明均匀度实验 | `illumination-uniformity`、概念 `均匀性`、`mixing-rod`(简化) | 热图 | M |
| 17 | 发射率与红外测温实验 | `发射率` | blackbody 扩展 | S |
| 18 | 光通量可见度积分实验 | `visible-flux-integral`、概念 `luminous-flux`、`发光强度` | 数值积分曲线  | S/M | ✅ 已落地 |
| 19 | 边缘检测与空间滤波直觉实验 | `边缘检测`、`spatial-filtering`(简化版) | 图像卷积 | M |
| 20 | 双点分辨增强（可选） | `瑞利分辨率`(公式) | ~~瑞利判据概念~~ 已于 2026-08-25 补链至 diffraction 实验 | S |

> 注：#20 与现有 `diffraction`（圆孔衍射）高度相关，优先考虑作为其第二模式而非新实验。

## 3. T2 · 待面包板/设计能力解锁（checkpoint 门禁内不做）

- **多透镜与傅里叶光学**：`4f-system`、`spatial-filtering`、`doublet`、`field-curvature`/`平场`
- **光学设计与优化**：`merit-function`、`zernike-polynomials`、`wavefront-error`、`rms-wavefront-error`、`strehl-ratio`、`doublet`
- **远心系统**：`双远心`
- **非成像/照明设计**：`cpc`、`cpc-geometry`、`concentration-ratio`(概念+公式)、`edge-ray-principle`、`freeform-optics`、`freeform-mapping`、`tir-lens`、`mixing-rod`、`light-guide-plate`、`brightness-enhancement-film`、`quantum-dot-film`、`local-dimming`、`source-target-mapping`
- **光谱仪结构**：`czerny-turner`、`czerny-turner-resolution`、`slit`、`free-spectral-range`、`spectral-bandwidth`、`prism-dispersion`（棱镜色散已在面包板 plan 缺口清单）
- **偏振/电光器件**：`faraday-rotation`、`faraday-rotation-angle`、`pockels-effect`、`half-wave-voltage`、`extinction-ratio`(公式)、`mz-transfer-function`、`mach-zehnder-modulator`
- **分光器件**：`分光镜`、`fabry-perot-microcavity`

## 4. T3 · 需新增数值仿真能力

- **傅里叶光学**：`fourier-transform-pair`、`fourier-transform-optics`、`angular-spectrum`（FFT 场传播，价值高、成本 M-L，建议 T3 内最优先评估）
- **光纤物理**：`single-mode-fiber`、`multi-mode-fiber`、`chromatic-dispersion`、`fiber-v-parameter`、`fiber-bending-loss`、`soliton-condition`、`pulse-broadening-gvd`
- **激光物理**：`gain-medium`、`population-inversion`、`optical-resonator`、`laser-threshold`(概念+公式)、`laser-rate-equations`、`mode-locking`、`q-switching`、`laser-linewidth`、`saturation-intensity`、`gain-bandwidth`（速率方程数值积分为核心）
- **非线性/放大器**：`nonlinear-effects`、`nonlinear-phase-matching`、`edfa`、`edfa-gain-model`
- **集成光子学**：`microring-resonator`、`microring-resonance`、`directional-coupler`、`grating-coupler`、`silicon-photonics`、`photonic-integrated-circuit`、`metasurface`

## 5. T4 · 保持纯阅读（含建议补入课程骨架者）

- 应用综述类：`hyperspectral-imaging`、`multispectral-imaging`、`snapshot-spectral-imaging`、`multispectral-filter-array`、`spectral-reconstruction`
- 度量学补充（高中心度，建议下批补入 curriculum 概念骨架）：`luminous-intensity`、`radiant-intensity`、`irradiance`(公式侧)、`亮度-照度关系`、`radiance-flux`
- 其余零散：`concepts`(元笔记)、`speed-of-light` 等——已由骨架节点覆盖导航

## 6. 维护方式

1. 每次知识库同步后运行 `python scripts/knowledge_coverage.py --write-report` 刷新覆盖率与本清单的事实基础。
2. 从 T1 提案进入 active plan 时，同步勾选本表并在 `linked_concepts`/`linked_formulas` 中挂接全部相关 slug。
3. T2/T3 条目的解锁条件以各自能力 checkpoint 为准，不在学习主线 plan 中提前排期。

## 7. 与既有计划的关系

- 本文件是选题池，不是排期表；不改变 ADR-002/003 及各 active plan 的任何门禁。
- 学习路径视图当前已通过 concept 骨架节点把未覆盖知识以「理论节点」形态暴露（点击跳知识库），因此本清单的落地节奏不影响学习者可见的知识广度。
