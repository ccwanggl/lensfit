# 光学面包板阶段 0 评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 0：发布链与 Lab 基线  
> 评审方式：源码测试、PyInstaller 构建、真实 sidecar 空库冒烟测试、进程残留检查

## 1. 结论

**阶段 0 验收通过。**

当前源码测试、PyInstaller sidecar 构建、Alembic 空库迁移、Lab 实验列表和单缝衍射冒烟测试均已通过。阶段 0 发现的唯一发布链缺陷（sidecar 二进制遗漏 15 个实验模块）已修复。

但阶段 0 仍留下两个**可重复性缺口**需要阶段 1 之前补齐：

1. 缺少自动化的 sidecar 冒烟测试脚本/用例；当前依赖人工命令行验证。
2. PyInstaller onefile 侧车在 Windows 下可能残留子进程，需要更可靠的清理机制。

## 2. 逐项检查

### 2.1 源码 Lab 测试

| 检查项 | 命令 | 结果 |
|---|---|---|
| 全量测试 | `cd engine && .venv/Scripts/python -m pytest -q` | **120 passed, 4 warnings** |
| Lab 专项测试 | `pytest tests/test_lab.py tests/test_api_lab.py -q` | **63 passed, 1 warning** |
| 静态检查 | `ruff check build_sidecar.py` | 通过 |

说明：

- 120 个测试覆盖注册表、API、生命周期、迁移、匹配、导出等路径。
- 4 条 warning 均为已知：`fastapi.testclient` 的 `httpx` 弃用警告，以及 Alembic `prepend_sys_path` 的 `path_separator` 弃用警告，不影响功能。

### 2.2 Sidecar 构建

| 检查项 | 结果 |
|---|---|
| `python build_sidecar.py` | 成功生成 `apps/desktop/src-tauri/binaries/lensfit-engine-x86_64-pc-windows-msvc.exe` |
| Alembic `env.py` 与迁移脚本 | 已作为 data 文件打入产物（日志显示 `lensfit.db.migrations.env` 及 5 个 revision 被分析） |
| 实验模块 | 修复后，19 个实验模块全部作为 hidden import 被打包 |

### 2.3 迁移完整性

使用临时空目录启动真实 sidecar：

```text
INFO  [alembic.runtime.migration] Running upgrade  -> 001, init
INFO  [alembic.runtime.migration] Running upgrade 001 -> c53e30ed595b, add_catalog_indexes
INFO  [alembic.runtime.migration] Running upgrade 001 -> 002, add match_result_snapshot to project_setups
INFO  [alembic.runtime.migration] Running upgrade 002, c53e30ed595b -> 003, merge migration heads 002 and c53e30ed595b
INFO  [alembic.runtime.migration] Running upgrade 003 -> 0ac6c641b5d7, add_data_source_and_manufacturer_indexes
```

数据库 `alembic_version` 表最终写入 `0ac6c641b5d7`，与源码 Alembic head 一致。

### 2.4 Lab API 冒烟测试

| 端点 | 结果 |
|---|---|
| `GET /health` | `{"status": "ok", "version": "1.1.0"}` |
| `GET /api/v1/lab/experiments` | 返回 19 个实验，包含 `single-slit-diffraction` |
| `POST /api/v1/lab/experiments/single-slit-diffraction/run` | 返回 `data`、`svg`（6826 字节）、`warnings`、`learning_hints` |

完整实验列表：

```text
aberration-spot, angle-of-view, blackbody, chromatic-aberration, color-mixing,
depth-of-field, diffraction, double-slit, grating, illumination-geometry,
magnification-scale, mtf-explorer, nyquist-sampling, polarization-malus,
sensor-coverage, single-slit-diffraction, snell-refraction, thermal-ifov-netd,
thin-lens
```

### 2.5 版本一致性

| 位置 | 版本 |
|---|---|
| `engine/pyproject.toml` | 1.1.0 |
| `apps/desktop/package.json` | 1.1.0 |
| `apps/desktop/src-tauri/tauri.conf.json` | 1.1.0 |
| `engine/lensfit/api/server.py` metadata | 1.1.0 |
| `CHANGELOG.md` | 1.1.0 |

版本号已统一。

### 2.6 进程残留

- 冒烟测试后，首次检查发现一个残留 sidecar 进程（PID 76368）。
- 使用 `taskkill //F //IM lensfit-engine-x86_64-pc-windows-msvc.exe` 清理后，进程列表干净。
- 该残留与 PyInstaller onefile 启动 uvicorn 的子进程结构有关，`subprocess.Popen.terminate()` 不一定能完全终止。

## 3. 发现的问题与修复

### 3.1 Sidecar 二进制遗漏实验模块（已修复）

**现象：**

首次构建的 sidecar 只列出 4 个实验，缺少 `single-slit-diffraction` 等 15 个实验。

**根因：**

`engine/build_sidecar.py` 的 `hidden_imports` 只硬编码了 4 个 MVP 实验：

```python
"lensfit.lab.experiments.thin_lens",
"lensfit.lab.experiments.diffraction",
"lensfit.lab.experiments.color_mixing",
"lensfit.lab.experiments.sensor_coverage",
```

而 `lensfit/lab/registry.py` 是动态发现 `experiments/` 目录下所有子类的。源码与打包产物因此不一致。

**修复：**

在 `build_sidecar.py` 中自动发现所有实验模块：

```python
experiments_dir = engine_dir / "lensfit" / "lab" / "experiments"
for exp_file in sorted(experiments_dir.glob("*.py")):
    if exp_file.name == "__init__.py":
        continue
    module_name = f"lensfit.lab.experiments.{exp_file.stem}"
    hidden_imports.append(module_name)
```

修复后重新构建，sidecar 列出全部 19 个实验。

### 3.2 构建时二进制被占用（已处理）

**现象：**

第一次重新构建时，PyInstaller 报告无法覆盖旧二进制：

```text
PermissionError: [WinError 5] Access is denied: '...\lensfit-engine-x86_64-pc-windows-msvc.exe'
```

**根因：**

之前的冒烟测试侧车子进程未完全退出，锁定了二进制文件。

**处理：**

使用 `taskkill //F //IM lensfit-engine-x86_64-pc-windows-msvc.exe` 强制终止残留进程后，构建成功。

**建议：**

在 CI 或本地构建脚本中加入前置清理步骤，确保没有运行的 sidecar 进程；或者为冒烟测试使用临时复制一份二进制的方式，避免锁定产物。

### 3.3 缺少可重复冒烟测试（未修复）

**现象：**

阶段 0 的冒烟测试是通过一次性 Python 内联脚本手工运行的，未纳入 `engine/tests/` 或 CI。

**风险：**

- 后续新增实验后，可能再次漏打包。
- 发布前回归测试依赖人工执行。

**建议：**

增加一个 pytest 用例或独立脚本 `engine/scripts/smoke_sidecar_lab.py`：

- 自动查找对应平台的 sidecar 二进制。
- 在临时目录启动 sidecar，空库运行迁移。
- 调用 `/health`、`/api/v1/lab/experiments`、`/api/v1/lab/experiments/single-slit-diffraction/run`。
- 验证返回包含 `svg` 与 `data`。
- 测试结束后强制清理 onefile 子进程（Windows 用 `taskkill`，Linux/macOS 用 `pkill -f`）。

该测试可标记为 `@pytest.mark.slow` 或仅在 CI 发布步骤运行，避免拖慢日常 `pytest`。

## 4. 阶段 0 退出条件对照

| 退出条件 | 状态 | 备注 |
|---|---|---|
| 打包产物能列出与源码一致的 Lab 实验集合 | ✅ 通过 | 19/19 个实验 |
| 空 SQLite 目录启动 sidecar 后能自动迁移到当前 Alembic head | ✅ 通过 | head 为 `0ac6c641b5d7` |
| 真实 sidecar `/health` 冒烟通过 | ✅ 通过 | `{"status": "ok", "version": "1.1.0"}` |
| 真实 sidecar `/api/v1/lab/experiments` 冒烟通过 | ✅ 通过 | 19 个实验 |
| 真实 sidecar `/api/v1/lab/experiments/single-slit-diffraction/run` 冒烟通过 | ✅ 通过 | SVG 6826 字节 |
| 连续启动/退出不残留 sidecar 进程 | ⚠️ 部分通过 | 需要 `taskkill` 辅助清理，建议后续改进 |

## 5. 进入阶段 1 的前提

阶段 0 已满足进入阶段 1 的条件。建议在阶段 1 开始前：

1. 把本次修复提交到 git（已取得用户确认后再执行 `git commit`）。
2. 补充一个 sidecar 冒烟测试脚本，作为阶段 0 的收尾。
3. 更新 `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 0 状态为已完成。

## 6. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `engine/build_sidecar.py`
- `engine/lensfit/lab/registry.py`
- `engine/lensfit/api/routers/lab.py`
