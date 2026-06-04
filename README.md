# LensFit — 智能镜头与传感器匹配系统

**LensFit — Intelligent Lens & Sensor Matching System**

<p align="center">
  <img src="apps/desktop/src-tauri/icons/128x128.png" alt="LensFit Logo" width="96">
</p>

<p align="center">
  <a href="#中文">中文</a> | <a href="#english">English</a>
</p>

---

<a name="中文"></a>
## 中文

### 简介

LensFit 是一款面向光学工程师和系统集成商的智能镜头与传感器匹配软件。它基于物理光学和几何光学的严谨计算，帮助用户在不同应用场景（工业视觉、摄影、显微镜、红外成像）中快速找到最优的镜头-传感器组合。

### 核心特性

| 特性 | 说明 |
|---|---|
| **多领域匹配** | 支持工业视觉、摄影、显微镜、红外成像四大领域 |
| **智能评分** | 基于覆盖比、分辨率、像素精度、放大倍率等多维度综合评分 |
| **物理知识库** | 内置 9 个光学公式、5 条物理约束，实时推理计算过程 |
| **推导链可视化** | 展示每个匹配结果背后的完整光学计算推导过程 |
| **传感器覆盖分析** | 交互式 SVG 覆盖图，直观展示像圈与传感器的关系 |
| **What-if 分析** | 调整参数后实时对比基准方案，评估灵敏度 |
| **方案对比** | 同时对比多个匹配方案，雷达图直观展示优劣 |
| **诊断面板** | 零结果时自动分析原因，给出参数调整建议 |
| **报告导出** | 支持 PDF 和 Excel 格式的专业报告导出 |
| **项目管理** | 保存匹配方案到项目，支持历史追溯 |
| **光学术语提示** | 鼠标悬停即可查看专业术语解释 |

### 技术架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Desktop App (Tauri 2)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  React 19   │  │  Tailwind   │  │  Recharts / Fabric  │  │
│  │  TypeScript │  │  CSS 4      │  │  (Visualization)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Sidecar (PyInstaller)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Python / FastAPI / SQLAlchemy / Alembic               ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ││
│  │  │  Core    │ │  Matching│ │  Knowledge│ │  Export  │  ││
│  │  │  (Optics)│ │  Engine  │ │  Base     │ │  (PDF/XLS)│ ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

**前端桌面应用**
- [React 19](https://react.dev/) — UI 框架
- [TypeScript](https://www.typescriptlang.org/) — 类型安全
- [Vite](https://vitejs.dev/) — 构建工具
- [Tailwind CSS 4](https://tailwindcss.com/) — 样式系统
- [Tauri 2](https://tauri.app/) — 跨平台桌面壳
- [Recharts](https://recharts.org/) — 图表可视化
- [Lucide React](https://lucide.dev/) — 图标系统

**后端引擎**
- [Python 3.11+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) — Web API
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- [Alembic](https://alembic.sqlalchemy.org/) — 数据库迁移
- [PyInstaller](https://pyinstaller.org/) — 二进制打包

### 快速开始

#### 环境要求

- Node.js 20+
- Python 3.11+
- Rust（用于 Tauri 构建）

#### 安装依赖

```bash
# 前端依赖
cd apps/desktop
npm install

# 后端依赖
cd ../../engine
pip install -e .
```

#### 开发模式

```bash
# 终端 1：启动后端
cd engine
python -m lensfit

# 终端 2：启动前端
cd apps/desktop
npm run dev
```

#### 构建生产版本

```bash
# 构建后端 sidecar
cd engine
python build_sidecar.py

# 构建桌面应用
cd ../apps/desktop
npm run tauri build
```

### 项目结构

```
lensfit/
├── apps/
│   └── desktop/              # Tauri 桌面应用
│       ├── src/              # React 前端源码
│       │   ├── components/   # 可复用组件
│       │   ├── pages/        # 页面组件
│       │   ├── utils/        # 工具函数 / API 封装
│       │   └── hooks/        # React Hooks
│       └── src-tauri/        # Tauri Rust 配置
│           ├── src/          # Rust 源码
│           └── binaries/     # 后端 sidecar 二进制
├── engine/
│   └── lensfit/              # Python 后端引擎
│       ├── api/              # FastAPI 路由
│       ├── core/             # 光学核心计算
│       ├── matching/         # 匹配引擎与评分
│       ├── knowledge/        # 物理光学知识库
│       ├── db/               # 数据库模型与目录
│       ├── domains/          # 领域适配器
│       └── visualization/    # 可视化数据生成
└── README.md
```

### 支持的匹配维度

| 维度 | 工业视觉 | 摄影 | 显微镜 | 红外 |
|---|---|---|---|---|
| 焦距 (Focal Length) | ✅ | ✅ | ✅ | ✅ |
| 放大倍率 (Magnification) | ✅ | — | ✅ | — |
| 视场角 (FOV) | ✅ | ✅ | — | ✅ |
| 工作距离 (WD) | ✅ | — | ✅ | — |
| 像素精度 | ✅ | — | ✅ | — |
| 分辨率 / MTF | ✅ | ✅ | ✅ | ✅ |
| 像圈覆盖 | ✅ | ✅ | ✅ | ✅ |
| 奈奎斯特极限 | ✅ | ✅ | ✅ | ✅ |
| 渐晕分析 | ✅ | ✅ | ✅ | ✅ |

### 许可证

MIT License — 详见 [LICENSE](LICENSE) 文件。

---

<a name="english"></a>
## English

### Introduction

LensFit is an intelligent lens and sensor matching system for optical engineers and system integrators. Based on rigorous calculations from physical and geometric optics, it helps users quickly find optimal lens-sensor combinations across various application domains (industrial vision, photography, microscopy, infrared imaging).

### Key Features

| Feature | Description |
|---|---|
| **Multi-domain Matching** | Supports industrial vision, photography, microscopy, and infrared imaging |
| **Intelligent Scoring** | Multi-dimensional scoring based on coverage ratio, resolution, pixel accuracy, magnification |
| **Physics Knowledge Base** | Built-in 9 optical formulas and 5 physical constraints with real-time inference |
| **Derivation Chain Visualization** | Complete optical calculation derivation shown for every match result |
| **Sensor Coverage Analysis** | Interactive SVG overlay diagram showing image circle vs sensor relationship |
| **What-if Analysis** | Real-time comparison against baseline when parameters change |
| **Scheme Comparison** | Side-by-side comparison of multiple candidates with radar charts |
| **Diagnostics Panel** | Automatic root-cause analysis when no matches found, with actionable suggestions |
| **Report Export** | Professional PDF and Excel report generation |
| **Project Management** | Save match results to projects with full history |
| **Optical Glossary** | Hover to see explanations for professional optical terms |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Desktop App (Tauri 2)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │  React 19   │  │  Tailwind   │  │  Recharts / Fabric  │  │
│  │  TypeScript │  │  CSS 4      │  │  (Visualization)    │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      Sidecar (PyInstaller)                   │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Python / FastAPI / SQLAlchemy / Alembic               ││
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  ││
│  │  │  Core    │ │  Matching│ │  Knowledge│ │  Export  │  ││
│  │  │  (Optics)│ │  Engine  │ │  Base     │ │  (PDF/XLS)│ ││
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘  ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

**Frontend Desktop App**
- [React 19](https://react.dev/) — UI framework
- [TypeScript](https://www.typescriptlang.org/) — Type safety
- [Vite](https://vitejs.dev/) — Build tool
- [Tailwind CSS 4](https://tailwindcss.com/) — Styling
- [Tauri 2](https://tauri.app/) — Cross-platform desktop shell
- [Recharts](https://recharts.org/) — Data visualization
- [Lucide React](https://lucide.dev/) — Icon system

**Backend Engine**
- [Python 3.11+](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/) — Web API framework
- [SQLAlchemy](https://www.sqlalchemy.org/) — ORM
- [Alembic](https://alembic.sqlalchemy.org/) — Database migrations
- [PyInstaller](https://pyinstaller.org/) — Binary bundling

### Quick Start

#### Prerequisites

- Node.js 20+
- Python 3.11+
- Rust (for Tauri builds)

#### Install Dependencies

```bash
# Frontend dependencies
cd apps/desktop
npm install

# Backend dependencies
cd ../../engine
pip install -e .
```

#### Development Mode

```bash
# Terminal 1: Start backend
cd engine
python -m lensfit

# Terminal 2: Start frontend
cd apps/desktop
npm run dev
```

#### Build Production

```bash
# Build backend sidecar
cd engine
python build_sidecar.py

# Build desktop app
cd ../apps/desktop
npm run tauri build
```

### Project Structure

```
lensfit/
├── apps/
│   └── desktop/              # Tauri desktop application
│       ├── src/              # React frontend source
│       │   ├── components/   # Reusable components
│       │   ├── pages/        # Page components
│       │   ├── utils/        # Utilities / API wrappers
│       │   └── hooks/        # React Hooks
│       └── src-tauri/        # Tauri Rust configuration
│           ├── src/          # Rust source
│           └── binaries/     # Backend sidecar binaries
├── engine/
│   └── lensfit/              # Python backend engine
│       ├── api/              # FastAPI routes
│       ├── core/             # Core optical computations
│       ├── matching/         # Matching engine & scoring
│       ├── knowledge/        # Physics & optics knowledge base
│       ├── db/               # Database models & catalog
│       ├── domains/          # Domain adapters
│       └── visualization/    # Visualization data generation
└── README.md
```

### Supported Matching Dimensions

| Dimension | Industrial | Photography | Microscopy | Infrared |
|---|---|---|---|---|
| Focal Length | ✅ | ✅ | ✅ | ✅ |
| Magnification | ✅ | — | ✅ | — |
| Field of View (FOV) | ✅ | ✅ | — | ✅ |
| Working Distance (WD) | ✅ | — | ✅ | — |
| Pixel Accuracy | ✅ | — | ✅ | — |
| Resolution / MTF | ✅ | ✅ | ✅ | ✅ |
| Image Circle Coverage | ✅ | ✅ | ✅ | ✅ |
| Nyquist Limit | ✅ | ✅ | ✅ | ✅ |
| Vignetting Analysis | ✅ | ✅ | ✅ | ✅ |

### License

MIT License — see [LICENSE](LICENSE) file for details.
