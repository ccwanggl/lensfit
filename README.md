# OptiBench — 光学工程工作台

**OptiBench — Optical Engineering Workbench**

<p align="center">
  <img src="apps/desktop/src-tauri/icons/128x128.png" alt="OptiBench Logo" width="96">
</p>

<p align="center">
  <a href="#中文">中文</a> | <a href="#english">English</a>
</p>

---

<a name="中文"></a>
## 中文

### 简介

OptiBench 是一款面向光学工程师和系统集成商的光学工程工作台，原名 LensFit。它以镜头-传感器智能匹配为主线，基于物理光学和几何光学的严谨计算，帮助用户在不同应用场景（工业视觉、摄影、显微镜、红外成像）中快速找到最优的镜头-传感器组合；同时内置 Self-Study Lab 交互式光学实验与光学知识库，覆盖从选型决策到原理学习的完整工作流。

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
- Python 3.12+
- Rust 1.75+（用于 Tauri 构建）
- [uv](https://docs.astral.sh/uv/)（可选但强烈推荐，用于加速虚拟环境与依赖安装）

#### 一键启动开发环境（推荐）

OptiBench 提供了跨平台的启动脚本，自动创建 Python 虚拟环境、安装依赖、初始化数据库并同时启动前后端。**Windows、macOS、Linux 上使用同一条命令**：

```bash
cd optibench
uv run scripts/dev.py
```

> 没有安装 [uv](https://docs.astral.sh/uv/) 时，用任意在 PATH 上的 Python 3.12+ 运行同一路径即可：`python3 scripts/dev.py`。

脚本会：
1. 创建 `engine/.venv` 并安装 Python 依赖（可编辑模式）
   - 若已安装 [uv](https://docs.astral.sh/uv/)，自动使用 `uv venv` + `uv pip install`
   - 否则回退到标准 `venv` + `pip`
   - 如果 `engine/.venv` 是在其他操作系统上创建的，脚本会自动识别并重建
2. 安装前端 `node_modules`（若目录来自其他操作系统，会自动重装）
3. 运行 Alembic 数据库迁移
4. 导入种子数据（如数据库不存在）
5. 启动 FastAPI 后端（`http://127.0.0.1:8765`）
6. 启动 Vite 前端开发服务器（`http://localhost:5173`）

#### 手动启动

如果你希望分别启动前后端：

```bash
# 终端 1：启动后端
cd engine

# 创建虚拟环境（二选一）
uv venv .venv
# python -m venv .venv

.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# 安装依赖（二选一）
uv pip install -e ".[dev]"
# pip install -e ".[dev]"

alembic upgrade head
python database/import_scripts/import_seed.py
python -m optibench.api.server --port 8765

# 终端 2：启动前端
cd apps/desktop
npm install
npm run dev
```

#### 构建桌面生产版本

```bash
cd optibench
uv run scripts/build-desktop.py
```

该脚本会先使用 PyInstaller 构建当前平台的 sidecar，再调用 Tauri 打包桌面应用。

### 项目结构

```
optibench/
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
│   └── optibench/              # Python 后端引擎
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

OptiBench is an optical engineering workbench for optical engineers and system integrators, formerly known as LensFit. Its core is intelligent lens-sensor matching: based on rigorous calculations from physical and geometric optics, it helps users quickly find optimal lens-sensor combinations across various application domains (industrial vision, photography, microscopy, infrared imaging). It also ships with an interactive Self-Study Lab and an optics knowledge base, covering the full workflow from selection decisions to learning the underlying principles.

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

> Note: Python version is 3.12+ to match `pyproject.toml`.

#### Prerequisites

- Node.js 20+
- Python 3.12+
- Rust 1.75+ (for Tauri builds)
- [uv](https://docs.astral.sh/uv/) (optional but strongly recommended for faster venv and dependency management)

#### One-Command Development Launcher (Recommended)

OptiBench provides a cross-platform launch script that automatically creates the Python virtual environment, installs dependencies, initializes the database, and starts both the backend and frontend. **The same command works on Windows, macOS, and Linux**:

```bash
cd optibench
uv run scripts/dev.py
```

> Without [uv](https://docs.astral.sh/uv/), run the same path with any Python 3.12+ on your PATH: `python3 scripts/dev.py`.

The script will:
1. Create `engine/.venv` and install Python dependencies in editable mode
   - If [uv](https://docs.astral.sh/uv/) is installed, it uses `uv venv` + `uv pip install`
   - Otherwise falls back to standard `venv` + `pip`
   - A virtual environment created on another OS is detected and recreated automatically
2. Install frontend `node_modules` (reinstalled automatically if the tree came from another OS)
3. Run Alembic database migrations
4. Import seed data (if the database does not exist)
5. Start the FastAPI backend (`http://127.0.0.1:8765`)
6. Start the Vite frontend dev server (`http://localhost:5173`)

#### Manual Start

If you prefer to start the backend and frontend separately:

```bash
# Terminal 1: Start backend
cd engine

# Create virtual environment (choose one)
uv venv .venv
# python -m venv .venv

.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

# Install dependencies (choose one)
uv pip install -e ".[dev]"
# pip install -e ".[dev]"

alembic upgrade head
python database/import_scripts/import_seed.py
python -m optibench.api.server --port 8765

# Terminal 2: Start frontend
cd apps/desktop
npm install
npm run dev
```

#### Build Desktop Production Bundle

```bash
cd optibench
uv run scripts/build-desktop.py
```

This script first builds the platform-specific sidecar with PyInstaller, then invokes Tauri to bundle the desktop application.

### Project Structure

```
optibench/
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
│   └── optibench/              # Python backend engine
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
