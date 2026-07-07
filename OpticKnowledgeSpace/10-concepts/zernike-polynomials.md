---
id: concept.zernike-polynomials
title: Zernike 多项式
type: concept
domains: [optical-design]
status: draft
aliases:
  - zernike-polynomials
  - Zernike多项式
  - 波前拟合
  - zernike-coefficients
---

# Zernike 多项式

## 定义

Zernike 多项式（Zernike Polynomials）是定义在单位圆（$\rho \leq 1$）上的一组正交多项式，广泛应用于光学系统中对波前像差（Wavefront Aberration）的分解、描述和拟合。由于它们在单位圆上正交，非常适合描述圆形瞳孔（如光学透镜、人眼瞳孔）的波前畸变。

径向多项式 $R_n^m(\rho)$ 与角向函数 $\cos(m\theta)$ 或 $\sin(m\theta)$ 组合构成完整的 Zernike 项：
$$
Z_n^m(\rho, \theta) = R_n^m(\rho) \cdot \begin{cases} \cos(m\theta) & m \geq 0 \\ \sin(|m|\theta) & m < 0 \end{cases}
$$

其中 $n$ 为径向阶数（$n \geq 0$），$m$ 为角向阶数（$|m| \leq n$，且 $n - |m|$ 为偶数）。

**常用 Zernike 项与像差对应**：
| 项 | 名称 | 像差类型 |
|----|------|----------|
| $Z_0^0$ |  piston | 整体平移 |
| $Z_1^{\pm1}$ |  tilt | 倾斜（x/y） |
| $Z_2^0$ |  defocus | 离焦 |
| $Z_2^{\pm2}$ |  astigmatism | 像散 |
| $Z_3^{\pm1}$ |  coma | 彗差 |
| $Z_3^{\pm3}$ |  trefoil | 三叶草 |
| $Z_4^0$ |  spherical | 球差 |

## 直观理解

Zernike 多项式就像波前像差的“化学元素周期表”：
- 任何复杂的波前畸变都可以被分解成这些“基本元素”的叠加。
- 每个 Zernike 项对应一种特定的“扭曲模式”——比如离焦像整个波前像气球一样鼓出或凹陷，像散像波前被“挤压”成马鞍形。
- **正交性**意味着：改变一个 Zernike 系数不会影响其他系数对波前误差的贡献（类似化学元素之间互不干扰）。

**类比**：就像傅里叶变换把信号分解成不同频率的正弦波，Zernike 分解把波前畸变分解成不同空间模式的“形状基元”。

## 关键参数/公式

| 参数 | 符号 | 说明 |
|------|------|------|
| 径向坐标 | $\rho$ | 归一化到瞳孔半径，$0 \leq \rho \leq 1$ |
| 角向坐标 | $\theta$ | 方位角，$0 \leq \theta < 2\pi$ |
| Zernike 系数 | $c_i$ | 第 $i$ 项 Zernike 的权重，单位通常为波长 $\lambda$ |
| 拟合波前 | $W(\rho, \theta)$ | $W = \sum_i c_i \cdot Z_i(\rho, \theta)$ |
| RMS 波前误差 | $\sigma_{WFE}$ | 拟合后残余波前的均方根值 |

径向多项式递推公式：
$$
R_n^m(\rho) = \sum_{k=0}^{(n-m)/2} \frac{(-1)^k (n-k)!}{k! \left(\frac{n+m}{2}-k\right)! \left(\frac{n-m}{2}-k\right)!} \rho^{n-2k}
$$

## 适用场景

- **光学设计与优化**：在 Zemax、Code V 等光学设计软件中，Zernike 系数用于描述和优化波前像差。
- **自适应光学**：实时波前传感器（如 Shack-Hartmann）测量波前，通过 Zernike 分解驱动可变形镜校正像差。
- **眼科与视觉科学**：描述人眼角膜和晶状体的高阶像差，指导个性化 LASIK 手术和隐形眼镜设计。
- **干涉测量**：从干涉图中提取波前误差并分解为 Zernike 成分，诊断光学元件的面形误差。
- **天文观测**：大口径望远镜的主动光学系统使用 Zernike 分解来监测和校正镜面热变形与重力变形。
- **光学检测**：检测非球面镜时，用 Zernike 多项式描述偏离理想球面的形状偏差。

## 关键关系
- 相关概念：[[./wavefront-error|波前误差]]（Zernike 是描述波前误差的标准工具）
- 相关概念：[[./strehl-ratio|Strehl 比]]（Zernike 系数与 Strehl 比存在解析关系）
- 相关概念：[[./merit-function|评价函数]]（优化过程中 Zernike 系数常作为优化目标）
- 相关公式：[[../20-formulas/rms-wavefront-error|RMS 波前误差]]（拟合后残余误差的量化指标）
- 相关公式：[[../20-formulas/strehl-ratio|Strehl 比公式]]
- 相关教程：[[../modules/50-optical-design/learning/06b-wavefront-aberrations|像差（下）｜高阶像差与设计关联]]

## 常见误区

1. **Zernike 项 = Seidel 像差？** 不完全等同。低阶 Zernike 与经典 Seidel 像差有对应关系，但 Zernike 是正交基，而 Seidel 像差在瞳孔上并不严格正交。Zernike 更适合描述实际波前。
2. **高阶项一定不重要？** 不是。大视场系统、大 NA 显微镜和自由曲面光学中，高阶 Zernike 项（如 5 阶、7 阶）对像质有显著影响。
3. **Zernike 适用于任意孔径？** 不是。Zernike 多项式定义在单位圆上，对于非圆瞳孔（如矩形光阑、环形成像），需要采用其他正交基（如 Karhunen-Loève 或广义 Zernike）。
4. **忽略系数单位**：Zernike 系数通常以波长为单位（如 $\lambda = 632.8$ nm），但在不同软件和数据源中可能使用不同归一化（如 Noll 归一化 vs Fringe 归一化），直接比较系数前需确认归一化方式。

## 来源

- Noll, "Zernike Polynomials and Atmospheric Turbulence," *JOSA*, 1976
- Mahajan, "Zernike Circle Polynomials and Optical Aberrations of Systems with Circular Pupils," *Engineering and Laboratory Notes*, 1994
- Born & Wolf, *Principles of Optics*, Chapter 9
