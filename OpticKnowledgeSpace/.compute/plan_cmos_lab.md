# CMOS Sensor Interactive Lab — 设计方案

## 背景

"Understanding CMOS Image Sensor" 笔记对 CMOS 传感器进行了全面剖析，涵盖光电转换、像素结构、噪声模型、动态范围、WDR 技术、接口、图像伪影等内容。但纯文字阅读难以建立直觉，尤其对于噪声叠加、动态范围压缩、WDR 响应曲线等概念，需要交互式可视化的辅助。

## 目标

开发一个基于 Python (Streamlit) 的交互式教学应用，让用户通过调节参数，实时观察 CMOS 传感器的行为变化，从而直观理解笔记中的核心概念。

## 技术选型

| 组件 | 选型 | 理由 |
|------|------|------|
| **框架** | Streamlit | 纯 Python，无需前端开发；支持 matplotlib 实时更新；可通过 `Custom Frames` 嵌入 Obsidian |
| **计算** | NumPy + SciPy | 科学计算，模拟传感器物理过程 |
| **可视化** | Matplotlib | 与 rayoptics 脚本统一，可复用知识库中的图像风格 |
| **输出** | 图像 + 数据表 | 结果可保存到 `attachments/computed/` |

## 应用架构

```
cmos_sensor_lab/
├── app.py                  # Streamlit 入口
├── pages/                  # 多页面应用
│   ├── 01_photon_to_dn.py     # 光电转换链路
│   ├── 02_noise_model.py      # 噪声模型与 SNR
│   ├── 03_dynamic_range.py    # 动态范围与 WDR
│   ├── 04_exposure_control.py # 曝光控制（卷帘/全局）
│   └── 05_artifacts.py        # 图像伪影模拟
├── core/                   # 物理模型核心库
│   ├── __init__.py
│   ├── sensor.py           # 传感器模型（像素、读出、ADC）
│   ├── noise.py            # 噪声生成器
│   ├── wdr.py              # WDR 响应模型（线性、Lin-log、Dual-diode 等）
│   └── artifacts.py        # 伪影生成器
├── utils/                  # 工具函数
│   ├── __init__.py
│   ├── plots.py            # 统一绘图风格
│   └── widgets.py          # 常用控件封装
└── assets/                 # 静态资源（示意图等）
```

## 模块设计

### 模块 1: 光电转换链路 (Photon → Electron → DN)

**对应笔记章节**：1.2 光电转换、1.3 像点微观结构、3.6 灵敏度

**可调节参数**：
- 量子效率 QE (0.1-1.0)
- 曝光时间 t (1μs-100ms)
- 入射光子数 N (1-100000 photons)
- 增益系数 g (1-10)
- ADC 位数 (8-16 bit)
- 势阱容量 FWC (1000-100000 e-)

**可视化输出**：
- 光子→电子→DN 的链路流程图
- 输入输出曲线（光子数 vs DN 值），展示线性区、饱和区、截止区
- 光子散粒噪声（泊松分布）的直观展示
- 不同增益下的 DN 分布直方图

**物理直觉**：
- 为什么增大增益不改变信噪比？（增益只是放大信号，散粒噪声也同比放大）
- 为什么 ADC 位数不够会导致量化噪声？（展示 8-bit vs 12-bit 的阶梯效应）
- 势阱满了会怎样？（展示饱和截止）

### 模块 2: 噪声模型与 SNR

**对应笔记章节**：3.3 噪声、3.4 信噪比

**可调节参数**：
- 光子数 N (暗光/正常/强光)
- 暗电流 σ_D (0-50 e-)
- 读出噪声 σ_R (0.5-20 e-)
- 温度 T (0°C-60°C)
- 固定模式噪声 (FPN) 系数
- kTC 噪声开关
- 散粒噪声开关（不可关，但可高亮）

**可视化输出**：
- 噪声频谱图：总噪声 = √(散粒² + 暗电流² + 读出² + FPN² + ADC²)
- SNR 随光子数变化的曲线（展示三条：25°C、0°C、-25°C）
- 实测噪声直方图（模拟拍摄 1000 帧的 DN 分布）
- 噪声分解饼图（展示当前条件下哪种噪声占主导）

**物理直觉**：
- 暗光时读出噪声主导，强光时散粒噪声主导
- 温度降低为什么能改善噪声？（暗电流指数下降）
- CDS 的效果（对比有无 CDS 的 kTC 噪声）

### 模块 3: 动态范围与 WDR

**对应笔记章节**：3.5 动态范围、3.18 宽动态（WDR）

**可调节参数**：
- 场景动态范围 (1-120 dB)
- 传感器 FWC 和 σ_R
- WDR 模式选择：
  - 线性模式（无 WDR）
  - Lin-log 响应
  - Dual-diode 高/低增益
  - 多帧曝光融合
  - Staggered HDR
- 色调映射算法（可选）

**可视化输出**：
- 输入输出响应曲线（线性 vs Lin-log vs Dual-diode）
- 同一场景在不同 WDR 模式下的输出图像对比
- 动态范围计算：DR = 20·log₁₀(FWC/σ_R)
- 伪影对比（多帧融合的鬼影 vs Staggered 的锯齿）

**物理直觉**：
- 为什么人眼能同时看清室内外，但传感器不行？（人眼动态范围 ~100dB，普通传感器 ~60dB）
- Lin-log 为什么牺牲线性度换取动态范围？
- Dual-diode 的"近饱和时切换高增益"机制

### 模块 4: 曝光控制（卷帘 vs 全局）

**对应笔记章节**：1.6 卷帘曝光、1.7 Rolling shutter 效应、4.4 曝光控制时序

**可调节参数**：
- 曝光模式：全局 vs 卷帘
- 曝光时间 (1μs-100ms)
- 物体运动速度 (静止/慢速/高速)
- 行读出时间
- 工频闪烁频率 (50/60Hz)
- 积分时间 (行数)

**可视化输出**：
- 全局 vs 卷帘的曝光时序图
- 运动物体的成像对比（全局清晰 vs 卷帘畸变）
- Rolling shutter 效应：风扇叶片、振动车辆的形变
- 工频闪烁模拟：不同积分时间下的明暗条纹
- 不同 int_t 对应的闪烁程度

**物理直觉**：
- 为什么卷帘曝光不能拍高速运动？（每行曝光时刻不同）
- 为什么 1/100s 在 50Hz 灯光下可能不闪烁？（整周期）
- 为什么全局快门贵？（需要额外存储电容）

### 模块 5: 图像伪影模拟

**对应笔记章节**：5. 图像伪影

**可调节参数**：
- 伪影类型：摩尔纹、迷宫格、紫边、条纹、面纱眩光、等高线
- 场景类型：高频率条纹、强光源、高对比度边缘
- 传感器参数：有无 OLPF、Bayer 排列、ADC 位数

**可视化输出**：
- 伪影成因示意图 + 实际模拟图像
- 摩尔纹：不同空间频率与采样频率的混叠
- 迷宫格：Bayer 去马赛克算法缺陷
- 紫边：轴向色差（红蓝焦点分离）
- 条纹：行噪声 + FPN 的可视化
- 等高线：8-bit 低动态场景下的量化效应
- 面纱眩光：杂散光对对比度的影响

**物理直觉**：
- 为什么 OLPF 能消除摩尔纹？（模糊高频，避免混叠）
- 为什么紫边出现在高对比度边缘？（短波折射率大，焦点前移）
- 为什么手机不用 OLPF？（牺牲锐度换取无摩尔纹，靠计算锐化）

## 与知识库的双向链接

每个模块的页面上提供「相关笔记」链接，如：
```markdown
> 📚 相关笔记：[[50-learning/Understanding CMOS Image Sensor#33-噪声|3.3 噪声]]
> 🔬 运行命令：`python -m scripts.noise_model --no-display`
```

## 统一视觉风格

- 使用与 `prism_refraction.py` 一致的 matplotlib 样式
- 配色：低饱和度、暖色调，与知识库风格一致
- 图表 DPI：150，字体清晰
- Streamlit 页面宽度：wide
- 中文标签和说明

## 文件规划

```
OpticKnowledgeSpace/.compute/
├── requirements.txt          # streamlit, numpy, matplotlib, scipy
├── cmos_sensor_lab/
│   ├── app.py                # 主入口
│   ├── core/
│   │   ├── __init__.py
│   │   ├── sensor.py         # CMOS 传感器物理模型
│   │   ├── noise.py          # 噪声生成
│   │   ├── wdr.py            # WDR 响应模型
│   │   └── artifacts.py      # 伪影生成
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── 01_photon_to_dn.py
│   │   ├── 02_noise_model.py
│   │   ├── 03_dynamic_range.py
│   │   ├── 04_exposure_control.py
│   │   └── 05_artifacts.py
│   └── utils/
│       ├── __init__.py
│       ├── plots.py
│       └── widgets.py
└── scripts/                   # 已有脚本
```

## 开发计划

| 阶段 | 内容 | 时间 |
|------|------|------|
| 1 | 搭建 `core/` 物理模型（sensor、noise、wdr、artifacts） | 2-3 小时 |
| 2 | 开发 `pages/01_photon_to_dn.py`（光电转换） | 2 小时 |
| 3 | 开发 `pages/02_noise_model.py`（噪声与SNR） | 2 小时 |
| 4 | 开发 `pages/03_dynamic_range.py`（WDR） | 2 小时 |
| 5 | 开发 `pages/04_exposure_control.py`（曝光） | 2 小时 |
| 6 | 开发 `pages/05_artifacts.py`（伪影） | 2 小时 |
| 7 | 统一 UI、添加笔记链接、集成测试 | 2 小时 |

**总计**：约 14-16 小时，可分 2-3 批次完成。

## 运行方式

```bash
cd /e/DevSpace/lensfit/OpticKnowledgeSpace/.compute
source .venv/bin/activate  # 或 .venv/Scripts/activate
pip install -r requirements.txt
streamlit run cmos_sensor_lab/app.py
```

在 Obsidian 中嵌入：
- Custom Frames 插件 → URL: `http://localhost:8501`

## 扩展性

- 新增伪影类型：只需扩展 `artifacts.py` + 新增页面
- 新增传感器模型：扩展 `sensor.py` 的物理模型
- 新增 WDR 算法：扩展 `wdr.py` 的响应函数
- 导出结果：每个模块的结果可保存到 `attachments/computed/cmos_lab/`