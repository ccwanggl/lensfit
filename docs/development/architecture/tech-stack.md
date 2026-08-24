# 技术栈与实现路径

## 1. 技术选型总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        技术栈全景图                              │
├─────────────────┬─────────────────┬─────────────────────────────┤
│   前端 (UI)      │   桌面封装       │      后端/核心引擎           │
├─────────────────┼─────────────────┼─────────────────────────────┤
│ React 19        │ Tauri v2        │ Python 3.12+                │
│ TypeScript      │ (Rust内核)       │  └─ 光学计算引擎             │
│ Tailwind CSS    │                 │  └─ 约束求解器               │
│ Recharts        │                 │  └─ 数据访问层               │
│ Fabric.js       │                 │                             │
│ (Canvas可视化)   │                 │ SQLite (本地)               │
│                 │                 │ SQLAlchemy 2.0              │
│                 │                 │ Alembic                     │
├─────────────────┴─────────────────┴─────────────────────────────┤
│                      构建与交付                                  │
│  Vite (前端构建)  │  GitHub Actions (CI/CD)  │  自动更新(Tauri)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. 各层技术选型详解

### 2.1 前端框架

| 候选方案 | 优点 | 缺点 | 结论 |
|---------|------|------|------|
| **React + TypeScript** | 生态最大、组件丰富、招聘容易 | 包体积较大 | ✅ **选用** |
| Vue 3 | 学习曲线低、中文社区强 | 大型项目类型系统不如React | 备选 |
| Svelte | 编译时优化、体积小 | 生态相对小 | 未来考虑 |
| 纯原生 + Canvas | 最小体积 | 开发效率低 | 不考虑 |

**选型理由**：
- React的生态系统对数据可视化（Recharts, D3）支持最好
- TypeScript的强类型对光学公式这种"参数多、易出错"的场景非常必要
- 前端团队招聘/社区支持最广泛

### 2.2 桌面应用框架

| 候选方案 | 体积 | 性能 | 系统访问 | 结论 |
|---------|:----:|:----:|:--------:|------|
| **Tauri v2** | ~3MB | 原生 | 完整 | ✅ **选用** |
| Electron | ~150MB | 一般 | 完整 | 体积太大 |
| Flutter Desktop | ~20MB | 好 | 受限 | UI与Web不统一 |
| 纯PyQt/PySide | ~30MB | 好 | 完整 | 前端技术栈割裂 |

**选型理由**：
- Tauri用Rust写内核，前端用Web技术，体积仅Electron的1/50
- 可以调用本地Python引擎（通过sidecar或HTTP本地服务）
- 支持Windows/macOS/Linux，一套代码三端运行
- 自动更新机制内置

### 2.3 核心引擎语言

| 候选方案 | 计算性能 | 开发效率 | 生态 | 结论 |
|---------|:-------:|:-------:|:----:|------|
| **Python** | 中（够用的） | 极高 | 科学计算无敌 | ✅ **选用** |
| Rust | 极高 | 中 | 增长快 | 未来迁移性能瓶颈模块 |
| C++ | 极高 | 低 | 光学库多但复杂 | 除非必要不用 |
| Go | 高 | 高 | 科学计算弱 | 不适合 |

**选型理由**：
- Python在科学计算、数据处理、公式表达上的开发效率无可替代
- NumPy/SciPy可加速矩阵运算
- 光学工程师容易理解和贡献Python代码（开源社区重要）
- 性能瓶颈部分（如大规模候选组合遍历）可用Rust重写为Python扩展

### 2.4 数据库

| 场景 | 选型 | 理由 |
|------|------|------|
| **MVP单机版** | SQLite | 零配置、单文件、Python内置支持 |
| 服务端版 | PostgreSQL | 复杂查询、并发、JSON字段 |
| ORM | SQLAlchemy 2.0 | 跨数据库兼容、类型提示完善 |
| 迁移 | Alembic | 数据库版本管理行业标准 |

### 2.5 可视化库

| 用途 | 选型 | 理由 |
|------|------|------|
| 传感器覆盖图 | **Fabric.js** / HTML5 Canvas | 精确绘制矩形/圆形/裁剪区 |
| 图表（MTF/柱状图） | **Recharts** | React生态最友好的图表库 |
| 雷达图对比 | Recharts Radar | 多维度方案对比 |
| 光谱曲线 | D3.js 或 Chart.js | 精细控制坐标轴和曲线样式 |
| 3D光路（远期） | Three.js | WebGL 3D渲染标准 |

---

## 3. 项目目录结构

```
optibench/
├── apps/
│   ├── desktop/                    # Tauri 桌面应用
│   │   ├── src/
│   │   │   ├── main.tsx            # 入口
│   │   │   ├── components/         # 通用组件
│   │   │   ├── pages/              # 页面
│   │   │   │   ├── IndustrialPage.tsx
│   │   │   │   ├── MicroscopePage.tsx
│   │   │   │   ├── InfraredPage.tsx
│   │   │   │   └── ProjectPage.tsx
│   │   │   ├── stores/             # Zustand 状态管理
│   │   │   └── utils/              # 前端工具函数
│   │   ├── src-tauri/              # Rust 后端（Tauri内核）
│   │   │   ├── Cargo.toml
│   │   │   ├── src/
│   │   │   │   └── main.rs
│   │   │   └── tauri.conf.json
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── web/                        # (未来) Web版
│
├── engine/                         # Python 核心引擎
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── build_sidecar.py            # PyInstaller 打包脚本
│   ├── optibench/
│   │   ├── __init__.py
│   │   ├── __main__.py             # 命令行入口
│   │   ├── core/                   # 基础光学计算
│   │   │   ├── __init__.py
│   │   │   ├── thin_lens.py        # 薄透镜公式 + 景深计算
│   │   │   ├── sensor.py           # 传感器标准化
│   │   │   ├── types.py            # 共享数据类型
│   │   │   └── utils.py            # 通用工具
│   │   ├── matching/               # 匹配引擎
│   │   │   ├── __init__.py
│   │   │   ├── engine.py           # 主匹配引擎 + 流水线
│   │   │   └── scoring.py          # 评分与 TOPSIS 排序
│   │   ├── domains/                # 领域模块
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # DomainModule 接口
│   │   │   ├── industrial.py
│   │   │   ├── microscope.py
│   │   │   ├── infrared.py
│   │   │   └── photography.py      # 摄影领域（已加入）
│   │   ├── db/                     # 数据访问层
│   │   │   ├── __init__.py
│   │   │   ├── models.py           # SQLAlchemy 模型
│   │   │   ├── catalog.py          # 目录查询（参数化）
│   │   │   └── migrations/         # Alembic 迁移
│   │   ├── visualization/          # 可视化数据生成
│   │   │   ├── __init__.py
│   │   │   ├── coverage.py         # 传感器覆盖图数据
│   │   │   ├── coc.py              # 弥散圆/景深图数据
│   │   │   └── mtf.py              # MTF 曲线数据
│   │   ├── export/                 # 报告导出
│   │   │   ├── csv_exporter.py
│   │   │   ├── excel_exporter.py
│   │   │   ├── pdf_exporter.py
│   │   │   └── sanitize.py
│   │   ├── knowledge/              # 知识推理与预设
│   │   │   ├── base.py
│   │   │   ├── constraints.py
│   │   │   ├── engine.py
│   │   │   ├── formulas.py
│   │   │   └── presets.py
│   │   ├── physics/                # 物理常数
│   │   │   ├── __init__.py
│   │   │   └── constants.py
│   │   └── api/                    # 对外 API（FastAPI）
│   │       ├── __init__.py
│   │       ├── server.py           # 路由、生命周期、认证（待拆分）
│   │       ├── catalog_router.py   # 器件目录 CRUD + 导入
│   │       └── import_pipe.py      # CSV/Excel 导入管道
│   └── tests/                      # 单元/集成测试
│       ├── test_api.py
│       ├── test_matching.py
│       ├── test_migrations.py
│       ├── test_lifecycle.py
│       └── test_catalog_import.py
│
├── database/                       # 数据库与数据
│   ├── seed_data/                  # 种子数据
│   │   ├── import_scripts/
│   │   └── ...
│   └── import_scripts/             # 数据导入脚本
│       └── ...
> **注意**：Schema 由 Alembic 迁移管理，不存在单独的 `schema.sql`。
│
├── docs/                           # 研发文档
│   └── development/
│       ├── product/
│       ├── architecture/
│       ├── decisions/
│       ├── plans/
│       ├── reviews/
│       └── guides/
│
├── modules/                        # 光学知识库（v4.0 起，取代原 Obsidian vault）
│   ├── 10-foundations/             # 光学基础
│   ├── 20-geometric-optics/        # 几何光学
│   ├── 30-wave-optics/             # 波动光学
│   ├── 40-spectroscopy/            # 光谱学
│   └── 50-optical-design/          # 光学设计
│
├── scripts/                        # 构建与发布脚本
│   ├── dev.py                      # 开发环境启动（跨平台）
│   └── build-desktop.py            # 桌面版构建（跨平台）
│
├── README.md
├── LICENSE
└── .github/
    └── workflows/
        ├── ci.yml
        └── release.yml
```

---

## 4. 核心依赖清单

### 4.1 Python 依赖 (engine/pyproject.toml)

> 以下清单与 `engine/pyproject.toml` 一致。标注“未使用”的依赖已在代码中确认无引用，计划清理或启用。

```toml
[project]
name = "optibench-engine"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    # 数据库
    "sqlalchemy>=2.0",
    "alembic>=1.13",
    
    # 科学计算
    "numpy>=1.26",
    "scipy>=1.11",
    
    # 约束求解
    "python-constraint>=1.4",  # 已引入但未在代码中使用
    
    # 安全表达式引擎（formula_registry L1级别）
    "asteval>=1.0",              # 已引入但未在代码中使用（formula_registry 尚未实现）
    
    # 缓存
    
    # API服务（桌面版通过HTTP本地调用）
    "fastapi>=0.109",
    "uvicorn>=0.27",
    
    # 数据处理
    "pydantic>=2.5",
    "python-multipart>=0.0.9",
    
    # 报告生成
    "openpyxl>=3.1",      # Excel导出
    "reportlab>=4.0",     # PDF导出
    "matplotlib>=3.8",    # 图表渲染（PDF内嵌）
    
    # 测试
    "pytest>=8.0",
    "pytest-cov>=4.1",
]
```

### 4.2 前端依赖 (apps/desktop/package.json)

```json
{
  "name": "optibench-desktop",
  "private": true,
  "version": "0.1.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "tauri": "tauri"
  },
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "zustand": "^5.0.0",
    "@tanstack/react-query": "^5.0.0",
    "recharts": "^2.12",
    "fabric": "^6.0",
    "clsx": "^2.1",
    "tailwind-merge": "^2.2"
  },
  "devDependencies": {
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "@vitejs/plugin-react": "^4.2",
    "typescript": "^5.3",
    "vite": "^6.0",
    "tailwindcss": "^4.0",
    "@tauri-apps/cli": "^2.0"
  }
}
```

---

## 5. 前后端通信架构

### 5.1 单机版通信方案（Sidecar + Supervisor）

Tauri 桌面应用启动时，由 **Sidecar Supervisor**（Rust）管理 Python 引擎进程的生命周期：

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Desktop App (Tauri)                          │
│  ┌──────────────┐  ┌──────────────────────────────────────────┐   │
│  │  React 前端   │  │      Sidecar Supervisor (Rust)          │   │
│  │              │  │  ┌─────────┐ ┌─────────┐ ┌───────────┐ │   │
│  │ 1.用户输入   │  │  │ Start   │ │ Health  │ │ Kill      │ │   │
│  │ 2.进度轮询   │  │  │ 启动    │ │ 检查    │ │ 终止      │ │   │
│  │ 3.显示结果   │  │  │ 随机端口│ │ 心跳10s │ │ 防僵尸   │ │   │
│  │              │  │  └────┬────┘ └────┬────┘ └─────┬─────┘ │   │
│  └──────┬───────┘  └───────┼──────────┼────────────┼───────┘   │
│         │                  │          │            │           │
│         │ HTTP/WebSocket   │          │            │           │
│         └──────────────────┘          │            │           │
│                                       ▼            ▼           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Python Engine (FastAPI + Uvicorn)            │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐ │   │
│  │  │ Core Engine│  │ SQLite DB  │  │ File Cache         │ │   │
│  │  │ 光学计算   │  │ 本地数据库 │  │ 兼容性缓存         │ │   │
│  │  └────────────┘  └────────────┘  └────────────────────┘ │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

**Sidecar Supervisor 核心职责**：

```rust
// Tauri src-tauri/src/supervisor.rs
use std::process::{Child, Command};
use std::sync::{Arc, Mutex};
use portpicker::pick_unused_port;

pub struct EngineSupervisor {
    process: Arc<Mutex<Option<Child>>>,
    pub port: u16,
    pub endpoint: String,
}

impl EngineSupervisor {
    pub fn start() -> Result<Self, String> {
        // 1. 随机选择可用端口，避免多实例冲突
        let port = pick_unused_port().ok_or("No available port")?;
        let endpoint = format!("http://127.0.0.1:{}", port);
        
        // 2. 启动 Python sidecar，传入端口参数
        let child = tauri::api::process::Command::new_sidecar("optibench-engine")
            .map_err(|e| format!("Sidecar not found: {}", e))?
            .args(&["--port", &port.to_string(), "--mode", "desktop"])
            .spawn()
            .map_err(|e| format!("Failed to start engine: {}", e))?;
        
        // 3. 等待健康检查通过（最多10秒，每100ms轮询）
        let health_url = format!("{}/health", endpoint);
        for _ in 0..100 {
            if reqwest::blocking::get(&health_url).is_ok() {
                break;
            }
            std::thread::sleep(std::time::Duration::from_millis(100));
        }
        
        Ok(Self {
            process: Arc::new(Mutex::new(Some(child))),
            port,
            endpoint,
        })
    }
    
    pub fn shutdown(&self) {
        // Tauri 关闭时确保 Python 进程也被终止，防止僵尸进程
        if let Ok(mut guard) = self.process.lock() {
            if let Some(mut child) = guard.take() {
                let _ = child.kill();
            }
        }
    }
    
    pub fn restart(&self) -> Result<(), String> {
        self.shutdown();
        std::thread::sleep(std::time::Duration::from_millis(500));
        // 重新启动...
    }
}

// Tauri 命令：前端获取引擎地址
#[tauri::command]
fn get_engine_endpoint(state: tauri::State<'_, EngineSupervisor>) -> String {
    state.endpoint.clone()
}
```

**风险备案**：
| 风险 | 应对 |
|------|------|
| Windows 路径含空格/中文导致 sidecar 启动失败 | 使用 `std::process::Command` 的 `raw_arg` 或短路径 |
| macOS Gatekeeper 拦截 sidecar | 对 Python 引擎也做代码签名（企业版） |
| 端口被占用 | 随机端口 + 启动前检测 |
| sidecar 崩溃 | Supervisor 监控 + 自动重启（最多3次） |
| 多实例冲突 | 每个实例独立随机端口 + 独立 SQLite 文件 |

### 5.2 API 核心端点设计（异步任务模型）

**耗时操作（匹配、报告导出）走异步**，轻量操作（计算、可视化、目录查询）走同步。

```yaml
paths:
  # === 健康检查 ===
  /api/v1/health:
    get:
      summary: 健康检查（Sidecar Supervisor 启动时轮询）

  # === 同步操作：基础计算（<100ms）===
  /api/v1/calculate:
    post:
      summary: 基础光学计算（薄透镜公式互推）
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                working_distance: { type: number }
                focal_length: { type: number }
                sensor_width: { type: number }
                fov_width: { type: number }
      responses:
        200:
          description: 计算结果
          content:
            application/json:
              schema:
                properties:
                  focal_length: { type: number }
                  fov_width: { type: number }
                  working_distance: { type: number }

  # === 同步操作：可视化数据生成（<100ms）===
  /api/v1/visualize/coverage:
    post:
      summary: 生成传感器覆盖图几何数据（纯JSON，不含渲染）
      requestBody:
        content:
          application/json:
            schema:
              properties:
                lens_id: { type: integer }
                detector_id: { type: integer }
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  sensor_rect: { type: object }
                  image_circle: { type: object }
                  vignetting_regions: { type: array }
                  coverage_ratio: { type: number }

  # === 异步操作：匹配（可能耗时 1~10s）===
  /api/v1/match/async:
    post:
      summary: 启动异步匹配任务
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                domain: { type: string, enum: [industrial, microscope, infrared] }
                requirements: { type: object }
                top_k: { type: integer, default: 20 }
      responses:
        202:
          description: 任务已创建
          content:
            application/json:
              schema:
                properties:
                  task_id: { type: string }
                  status: { type: string, enum: [pending, running] }
                  created_at: { type: string, format: date-time }

  /api/v1/match/async/{task_id}:
    get:
      summary: 查询匹配任务状态（前端轮询进度）
      parameters:
        - name: task_id
          in: path
          required: true
          schema: { type: string }
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  task_id: { type: string }
                  status: { type: string, enum: [pending, running, completed, failed, cancelled] }
                  progress: { type: number, description: "0.0 ~ 1.0" }
                  stage: { type: string, enum: [index_filter, quick_filter, domain_filter, scoring, ranking] }
                  total_candidates: { type: integer }
                  filtered_candidates: { type: integer }
                  error: { type: string }

  /api/v1/match/async/{task_id}/result:
    get:
      summary: 获取已完成任务的匹配结果
      parameters:
        - name: task_id
          in: path
          required: true
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  top_matches: { type: array }
                  pareto_front: { type: array }
                  stage_counts: { type: object }

  /api/v1/match/async/{task_id}:
    delete:
      summary: 取消正在执行的任务
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  cancelled: { type: boolean }

  # === 异步操作：报告导出（可能耗时 2~5s）===
  /api/v1/export/pdf/async:
    post:
      summary: 启动PDF报告导出
      requestBody:
        content:
          application/json:
            schema:
              properties:
                project_id: { type: integer }
                setup_ids: { type: array, items: { type: integer } }
      responses:
        202:
          content:
            application/json:
              schema:
                properties:
                  task_id: { type: string }

  /api/v1/export/pdf/async/{task_id}:
    get:
      summary: 查询导出状态
      responses:
        200:
          content:
            application/json:
              schema:
                properties:
                  status: { type: string }
                  download_url: { type: string }

  # === 目录查询（同步，索引覆盖）===
  /api/v1/catalog/lenses:
    get:
      summary: 查询镜头目录
      parameters:
        - name: category
        - name: mount
        - name: focal_min
        - name: focal_max
        - name: image_circle_min
        - name: wd_min
        - name: wd_max
        - name: limit
          schema: { type: integer, default: 100 }

  # === 项目管理 ===
  /api/v1/projects:
    get: { summary: 列出项目 }
    post: { summary: 创建项目 }

  /api/v1/projects/{id}/setups:
    get: { summary: 列出方案 }
    post: { summary: 保存方案 }
```

**前端异步调用示例**：

```typescript
// React + TanStack Query 风格的异步匹配
async function startMatching(requirements: MatchRequirements) {
  // 1. 提交任务
  const { task_id } = await api.post('/api/v1/match/async', requirements);
  
  // 2. 轮询进度
  const poll = setInterval(async () => {
    const status = await api.get(`/api/v1/match/async/${task_id}`);
    
    updateProgressBar(status.progress);
    updateStageLabel(status.stage);  // "正在筛选... (3,240/12,000)"
    
    if (status.status === 'completed') {
      clearInterval(poll);
      const result = await api.get(`/api/v1/match/async/${task_id}/result`);
      displayResults(result.top_matches);
    }
    
    if (status.status === 'failed') {
      clearInterval(poll);
      showError(status.error);
    }
  }, 200);  // 每200ms轮询一次
  
  // 3. 提供取消按钮
  return {
    cancel: () => api.delete(`/api/v1/match/async/${task_id}`)
  };
}
```

---

## 6. 开发环境搭建

### 6.1 前置依赖

```bash
# 1. 安装 Rust (Tauri需要)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. 安装 Node.js 20+
# https://nodejs.org/

# 3. 安装 Python 3.12+
# https://python.org/

# 4. 安装 Tauri系统依赖 (Linux示例)
# https://tauri.app/start/prerequisites/
```

### 6.2 项目初始化

```bash
# 克隆仓库
git clone https://github.com/your-org/optibench.git
cd optibench

# 初始化Python引擎
cd engine
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

# 初始化数据库
alembic upgrade head
python -m optibench.db.seed  # 导入种子数据

# 启动引擎API
python -m optibench.api.server

# --- 新开终端 ---
# 初始化前端
cd apps/desktop
npm install

# 开发模式（同时启动Vite前端和Tauri桌面壳）
npm run tauri dev
```

---

## 7. 构建与发布流程

### 7.1 CI/CD 流水线

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        platform: [ubuntu-latest, windows-latest, macos-latest]
    runs-on: ${{ matrix.platform }}
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      
      - name: Setup Node
        uses: actions/setup-node@v4
        with: { node-version: 20 }
      
      - name: Setup Rust
        uses: dtolnay/rust-action@stable
      
      - name: Build Engine
        run: |
          cd engine
          pip install pyinstaller
          pyinstaller --onefile --name optibench-engine optibench/api/server.py
      
      - name: Build Desktop
        run: |
          cd apps/desktop
          npm install
          npm run tauri build
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: optibench-${{ matrix.platform }}
          path: apps/desktop/src-tauri/target/release/bundle/
```

> **注意**：当前仓库中 `.github/workflows/release.yml` 尚未创建，仅有 `ci.yml`。
> 上述 release 流水线为目标设计，需在后续迭代中落地。

### 7.2 发布产物

| 平台 | 产物 | 预估大小 |
|------|------|:-------:|
| Windows | `OptiBench_0.1.0_x64_en-US.msi` | ~25MB |
| macOS | `OptiBench_0.1.0_x64.dmg` | ~20MB |
| Linux | `optibench_0.1.0_amd64.AppImage` | ~22MB |

---

## 8. 性能预算

| 指标 | 目标 | 说明 |
|------|------|------|
| 应用冷启动 | <3秒 | 从双击图标到可操作 |
| 匹配查询 | <500ms | 从点击"匹配"到结果显示 |
| 数据库查询 | <50ms | 单条件目录查询 |
| 覆盖图渲染 | <100ms | Canvas绘制传感器+像圆 |
| 安装包体积 | <30MB | 含引擎+前端+数据库 |
| 内存占用 | <200MB | 运行时峰值 |

---

## 9. 技术风险与备案

| 风险 | 影响 | 备案方案 |
|------|------|---------|
| Tauri与Python sidecar通信不稳定 | 高 | 降级为Python直接启动HTTP服务，Tauri只作为浏览器壳 |
| SQLite并发写入冲突 | 中 | 使用WAL模式；未来迁移到PostgreSQL |
| 前端Canvas性能差（大数据量） | 中 | 光谱数据>1000点时改用WebGL或数据降采样 |
| Python打包体积过大 | 中 | 使用uv/pex代替PyInstaller；或用Rust重写引擎 |
| 跨平台字体/显示差异 | 低 | Tailwind统一样式；测试覆盖三大平台 |
