# LensFit

自动匹配镜头和探测器参数的开源软件。

## 功能

- **跨领域统一选型**：工业视觉、显微镜、红外成像三大领域一站式解决
- **智能匹配引擎**：四级流水线（索引预筛选 → 快速硬约束 → 领域约束 → 全量评分）
- **传感器覆盖可视化**：实时绘制传感器矩形与镜头像圆的覆盖关系
- **多厂商中立数据库**：不绑定任何品牌，支持用户自定义器件
- **多目标优化**：TOPSIS 排序 + Pareto 前沿，展示权衡关系

## 技术栈

| 层 | 技术 |
|---|---|
| 前端 | React 19 + TypeScript + Tailwind CSS + Fabric.js |
| 桌面 | Tauri v2 (Rust) |
| 引擎 | Python 3.12 + FastAPI |
| 数据库 | SQLite (MVP) / PostgreSQL (企业版) |
| ORM | SQLAlchemy 2.0 |

## 快速开始

### 前置依赖

- Python 3.12+
- Node.js 20+
- Rust (Tauri 桌面端需要)

### 1. 安装引擎

```bash
cd engine
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. 初始化数据库

```bash
# 方法 A：通过 Alembic 迁移
alembic upgrade head

# 方法 B：通过 init_db() 自动创建表
python -c "from lensfit.db.models import init_db; init_db()"

# 导入种子数据
python ../database/import_scripts/import_seed.py
```

### 3. 启动引擎（开发模式）

```bash
python -m lensfit.api.server --port 8765 --db sqlite:///lensfit.db
```

### 4. 启动前端（开发模式）

```bash
cd apps/desktop
npm install
npm run dev
```

前端将在 `http://localhost:5173` 运行，通过 API 与引擎通信。

### 5. 构建桌面应用（生产模式）

```bash
# 构建 Python sidecar 二进制
cd engine
python build_sidecar.py

# 构建 Tauri 桌面应用
cd ../apps/desktop
npm run tauri build
```

## 项目结构

```
lensfit/
├── apps/desktop/      # Tauri + React 桌面应用
│   ├── src/           # React 源码
│   ├── src-tauri/     # Rust Tauri 壳
│   └── dist/          # 前端构建输出
├── engine/            # Python 核心引擎
│   ├── lensfit/
│   │   ├── core/      # 基础光学计算
│   │   ├── matching/  # 匹配引擎
│   │   ├── domains/   # 领域模块
│   │   ├── db/        # 数据模型
│   │   ├── visualization/  # 可视化数据生成
│   │   └── api/       # FastAPI 服务
│   └── tests/         # 单元测试
├── database/          # 种子数据 & 导入脚本
└── docs/              # 设计文档
```

## 运行测试

```bash
cd engine
source .venv/bin/activate
pytest tests/ -v
```

## API 端点

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/health` | 健康检查 |
| POST | `/api/v1/calculate` | 薄透镜公式计算 |
| POST | `/api/v1/match/async` | 启动异步匹配 |
| GET | `/api/v1/match/async/{task_id}` | 查询任务状态 |
| GET | `/api/v1/match/async/{task_id}/result` | 获取匹配结果 |
| POST | `/api/v1/visualize/coverage` | 生成覆盖图数据 |
| GET | `/api/v1/catalog/lenses` | 查询镜头目录 |
| GET | `/api/v1/catalog/detectors` | 查询探测器目录 |

## 开发计划

| 阶段 | 时间 | 目标 |
|---|---|---|
| Phase 0 | Week 1-2 | 架构加固、技术预研 |
| Phase 1 | Week 3-10 | MVP 核心（工业视觉模块） |
| Phase 2 | Week 11-18 | 功能扩展（显微镜 + 红外） |
| Phase 3 | Week 19-24 | 商业化准备 |

## 文档

- [竞品分析](docs/01-competitor-analysis.md)
- [软件架构](docs/02-software-architecture.md)
- [核心算法](docs/03-core-algorithms.md)
- [数据库设计](docs/04-database-design.md)
- [功能与MVP](docs/05-features-and-mvp.md)
- [技术栈](docs/06-tech-stack.md)

## License

MIT
