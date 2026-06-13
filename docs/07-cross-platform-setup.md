# 跨平台开发与构建指南

LensFit 采用 **Tauri v2 + React 前端 + Python FastAPI 后端引擎** 的架构。本文档说明如何在 Windows、macOS 和 Linux 上一致地搭建开发环境、运行调试以及构建桌面发布包。

---

## 1. 依赖环境

| 组件 | 最低版本 | 说明 |
|---|---|---|
| Python | 3.12 | 后端引擎与脚本 |
| Node.js | 20 | 前端构建工具链 |
| npm | 10 | 随 Node.js 安装 |
| Rust | 1.75 | Tauri 桌面壳编译 |
| Git | 任意 | 克隆仓库 |

> 提示：Windows 用户请确保 Python 与 Node.js 已加入系统 `PATH`。

---

## 2. 仓库结构与约定

```
lensfit/
├── apps/desktop/          # React + Tauri 桌面应用
├── database/              # 种子数据与导入脚本
├── docs/                  # 项目文档
├── engine/                # Python 引擎
│   ├── .venv/             # Python 虚拟环境（由脚本自动创建）
│   ├── alembic.ini        # 迁移配置
│   └── lensfit/           # 引擎源码
├── scripts/               # 跨平台启动与构建脚本
│   ├── dev.py             # 主启动脚本（跨平台）
│   ├── dev.sh             # Unix 包装器
│   ├── dev.bat            # Windows 包装器
│   ├── build-desktop.py   # 主构建脚本（跨平台）
│   ├── build-desktop.sh   # Unix 包装器
│   └── build-desktop.bat  # Windows 包装器
└── README.md
```

---

## 3. 开发环境一键启动

### 3.1 推荐方式：`scripts/dev.py`

`scripts/dev.py` 是跨平台的主启动脚本，使用 Python 标准库实现，不依赖 `curl`、`source` 等 Unix 命令。

```bash
# Windows
cd lensfit
python scripts/dev.py

# macOS / Linux
cd lensfit
python3 scripts/dev.py
```

脚本行为：

1. 检测 `engine/.venv`；不存在则创建并安装 `pip install -e ".[dev]"`
2. 检测 `apps/desktop/node_modules`；不存在则执行 `npm install`
3. 运行 `alembic upgrade head` 应用数据库迁移
4. 若 `lensfit.db` 不存在，执行种子数据导入
5. 启动 FastAPI 后端（默认 `127.0.0.1:8765`）
6. 等待 `/health` 就绪
7. 启动 Vite 前端开发服务器（默认 `http://localhost:5173`）
8. 捕获 `Ctrl+C` 后优雅停止两个子进程

### 3.2 包装器脚本

如果你更习惯 shell/batch：

```bash
# macOS / Linux
./scripts/dev.sh

# Windows CMD
scripts\dev.bat
```

它们最终都调用 `scripts/dev.py`。

### 3.3 常用选项

```bash
# 只启动后端（前端自行启动或调试 API）
python scripts/dev.py --backend-only

# 强制重新导入种子数据
python scripts/dev.py --reseed

# 自定义后端端口
python scripts/dev.py --port 9876
```

---

## 4. 手动启动（可选）

当需要独立调试前后端时，可按以下步骤手动启动。

### 4.1 后端

```bash
cd engine

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# 安装依赖
pip install -e ".[dev]"

# 应用数据库迁移
alembic upgrade head

# 导入种子数据
python ../database/import_scripts/import_seed.py

# 启动服务
python -m lensfit.api.server --port 8765 --host 127.0.0.1
```

后端 API 文档：`http://127.0.0.1:8765/docs`

### 4.2 前端

```bash
cd apps/desktop
npm install
npm run dev
```

前端地址：`http://localhost:5173`

---

## 5. 数据库迁移

项目使用 Alembic 管理 SQLite schema。

```bash
cd engine
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux

# 查看当前 head
alembic heads

# 升级到最新版本
alembic upgrade head

# 回滚一级
alembic downgrade -1

# 生成新的迁移（修改 models.py 后）
alembic revision --autogenerate -m "描述"
```

> 注意：数据库文件 `lensfit.db` 已加入 `.gitignore`，不会提交到仓库。

---

## 6. 构建桌面发布包

### 6.1 推荐方式：`scripts/build-desktop.py`

```bash
# Windows
cd lensfit
python scripts/build-desktop.py

# macOS / Linux
cd lensfit
python3 scripts/build-desktop.py
```

脚本行为：

1. 确保 `engine/.venv` 与依赖已安装
2. 调用 `engine/build_sidecar.py` 生成当前平台的 sidecar 二进制
3. 安装前端依赖
4. 调用 `npm run tauri build` 打包桌面应用

构建产物位于：

```
apps/desktop/src-tauri/target/release/bundle/
```

### 6.2 sidecar 说明

- `build_sidecar.py` 会按当前平台生成带 target triple 的二进制，例如：
  - Windows: `lensfit-engine-x86_64-pc-windows-msvc.exe`
  - Linux: `lensfit-engine-x86_64-unknown-linux-gnu`
  - macOS: `lensfit-engine-aarch64-apple-darwin` 或 `lensfit-engine-x86_64-apple-darwin`
- 同时会拷贝一份为 `lensfit-engine`（Windows 下为 `lensfit-engine.exe`），便于本地开发直接运行
- `apps/desktop/src-tauri/binaries/` 目录已在 `.gitignore` 中，sidecar 二进制不应提交到仓库

### 6.3 手动构建

```bash
cd engine
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux
python build_sidecar.py

cd ../apps/desktop
npm install
npm run tauri build
```

---

## 7. 测试

### 7.1 后端测试

```bash
cd engine
.venv\Scripts\activate      # Windows
# source .venv/bin/activate # macOS / Linux
pytest tests/ -v
```

### 7.2 代码风格

```bash
cd engine
ruff check .
ruff format .
```

### 7.3 前端类型检查与构建

```bash
cd apps/desktop
npm run build
```

---

## 8. 常见问题

### 8.1 `alembic upgrade head` 报告多个 head

如果历史迁移出现分支（例如 `002` 与 `c53e30ed595b` 都基于 `001`），项目已提供合并迁移 `003_merge_heads.py`。直接运行 `alembic upgrade head` 即可。

### 8.2 Windows 下 `curl` 不可用

`scripts/dev.py` 使用 Python 标准库 `urllib` 检测后端健康，不依赖 `curl`。

### 8.3 sidecar 无法启动

- 检查 `apps/desktop/src-tauri/binaries/` 下是否存在与当前平台匹配的二进制
- 删除旧的异平台二进制后重新运行 `scripts/build-desktop.py`
- 确保 Rust 工具链已安装并可用

### 8.4 前端无法连接后端

- 确认后端运行在 `http://127.0.0.1:8765`
- 确认 `apps/desktop/src/utils/api.ts` 中的 fallback endpoint 与后端一致
- 检查浏览器控制台是否有 CORS 错误

---

## 9. 平台差异速查

| 操作 | Windows | macOS / Linux |
|---|---|---|
| 激活虚拟环境 | `.venv\Scripts\activate` | `source .venv/bin/activate` |
| 启动开发环境 | `python scripts/dev.py` | `python3 scripts/dev.py` 或 `./scripts/dev.sh` |
| 构建桌面包 | `python scripts/build-desktop.py` | `python3 scripts/build-desktop.py` 或 `./scripts/build-desktop.sh` |
| Python 解释器调用 | `python` | `python3` |
| 路径分隔符 | `\` 或 `/` | `/` |

---

## 10. 相关文档

- [软件架构](02-software-architecture.md)
- [数据库设计](04-database-design.md)
- [技术栈](06-tech-stack.md)
