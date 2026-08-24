# 光学面包板阶段 2 评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 2：Workbench Native Run API  
> 评审方式：代码走查、API 测试、全量回归测试

## 1. 结论

**阶段 2 验收通过。**

`POST /api/v1/lab/workbench/run` 已实现为无状态 API，可将 `SceneGraph v1` 映射到现有 `SingleSlitDiffractionExperiment.run()`，返回与现有实验 API 一致的 `data`/`svg`/`warnings`/`learning_hints`。新增 6 个 API 测试全部通过，全量测试无回归。

## 2. 实现概览

新增文件：

```text
engine/optibench/lab/workbench/native_interpreter.py
engine/optibench/lab/workbench/solver.py
engine/tests/test_api_workbench.py
```

修改文件：

```text
engine/optibench/lab/schemas.py
engine/optibench/api/routers/lab.py
```

## 3. 逐项检查

### 3.1 API 契约

| active plan 要求 | 实现 | 状态 |
|---|---|---|
| `POST /api/v1/lab/workbench/run` | 已注册在 `lab.py` | ✅ |
| 响应复用 Lab 风格：`data`、`svg`、`warnings`、`learning_hints` | 返回 `ExperimentRunResponse` | ✅ |
| 不访问数据库、不启动 Node、不读写文件 | `WorkbenchSolver` 只调用 `registry.run()` | ✅ |
| 现有 `/api/v1/lab/experiments/{id}/run` 无回归 | 原端点未改动，测试通过 | ✅ |

### 3.2 物理正确性

| 退出条件 | 测试 | 状态 |
|---|---|---|
| 默认 SceneGraph 的 `central_max_width_mm` 与直接调用 `SingleSlitDiffractionExperiment.run({})` 一致 | `test_workbench_run_default_scene` | ✅ |
| `slit_width_um` 从 20 增到 100 时中央亮纹宽度下降 | `test_workbench_slit_width_decreases_central_max` | ✅ |
| `wavelength_nm` 从 450 增到 650 时中央亮纹宽度上升 | `test_workbench_wavelength_increases_central_max` | ✅ |
| screen 与 slit 距离翻倍时 `first_min_position_mm` 近似翻倍 | `test_workbench_distance_doubles_first_min` | ✅ |
| Fraunhofer 条件不足时返回 warning | `test_workbench_fraunhofer_warning` | ✅ |

### 3.3 校验与错误处理

| 检查项 | 实现 | 状态 |
|---|---|---|
| 非法 SceneGraph 返回 422 | `test_workbench_invalid_scene_returns_422` | ✅ |
| 使用 Pydantic `SceneGraph` 自动校验请求体 | `WorkbenchRunRequest.scene: SceneGraph` | ✅ |
| solver 捕获 `ValueError` 并返回 422 | `lab.py` 异常处理 | ✅ |

### 3.4 测试与静态检查

| 检查项 | 命令 | 结果 |
|---|---|---|
| Workbench API 测试 | `pytest tests/test_api_workbench.py -q` | **6 passed** |
| 全量回归测试 | `pytest -q` | **137 passed, 4 warnings** |
| 静态检查 | `ruff check optibench/lab/workbench optibench/api/routers/lab.py optibench/lab/schemas.py tests/test_api_workbench.py` | 通过 |

## 4. 实现细节

### 4.1 `native_interpreter.py`

负责将 SceneGraph 翻译为实验参数：

```python
params = {
    "wavelength_nm": source.params["wavelength_nm"],
    "slit_width_um": aperture.params["slit_width_um"],
    "screen_distance_m": scene.screen_distance_m(),
}
```

同时检查 Fraunhofer 远场条件：

```python
far_field_m = a_m**2 / lambda_m
if screen_distance_m < 10 * far_field_m:
    warnings.append("...")
```

### 4.2 `solver.py`

`WorkbenchSolver.solve(scene)` 是 SceneGraph 到实验运行的统一入口。当前只支持 `fraunhofer_intensity` observable；未来添加 ray-optics 适配器时，可在此处扩展分发逻辑，而不影响 SceneGraph 模型。

### 4.3 `lab.py` 路由

新增端点：

```python
@router.post("/workbench/run", response_model=ExperimentRunResponse)
def run_workbench(req: WorkbenchRunRequest):
    ...
```

复用 `ExperimentRunResponse`，保持前后端契约一致。

## 5. 发现与建议

### 5.1 已确认的设计选择

1. ** Fraunhofer 阈值取 `10 * a² / λ`**

   这是一个教学级的启发式阈值，不是严格物理判据，但足够提示用户进入近场。后续可根据教研反馈调整。

2. **`WorkbenchRunRequest.scene` 直接使用 `SceneGraph` 模型**

   这样 FastAPI 可自动生成请求体验证和 OpenAPI 文档，也保证 SceneGraph 校验规则自动生效。

### 5.2 建议改进（非阶段 2 阻塞项）

1. **统一错误信息本地化**

   当前 `ValueError` 消息是英文。阶段 3 前端接入时，可能需要将 `detail` 映射为中文提示。

2. **提取可复用的 `client` fixture**

   `test_api_lab.py` 和 `test_api_workbench.py` 中各有几乎相同的 `client` fixture。建议后续将通用 fixture 移入 `tests/conftest.py`。

3. **补充 OpenAPI/契约文档**

   阶段 3 完成后，建议把 `/api/v1/lab/workbench/run` 的示例请求和响应写入 `docs/development/specifications/lab/workbench-api.md`。

## 6. 阶段 2 退出条件对照

| 退出条件 | 状态 |
|---|---|
| API 响应复用 Lab 风格 | ✅ |
| 默认 SceneGraph 输出与直接调用实验一致 | ✅ |
| 缝宽增加中央亮纹变窄 | ✅ |
| 波长增加中央亮纹变宽 | ✅ |
| 距离翻倍第一极小翻倍 | ✅ |
| Fraunhofer 不足返回 warning | ✅ |
| 现有实验 API 无回归 | ✅ |
| 不访问数据库/Node/文件 | ✅ |

## 7. 进入阶段 3 的前提

阶段 2 已满足进入阶段 3 的全部条件。建议在阶段 3 开始前：

1. 提交阶段 2 改动（已取得用户确认后再执行 `git commit`）。
2. 确认 `LearningHub` 当前实验列表、参数运行、SVG 展示无回归。
3. 设计 `single-slit-breadboard` preset 的 UI：锁定布局（激光、单缝、屏幕、强度曲线），左侧参数，右侧知识栏。

## 8. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `engine/optibench/api/routers/lab.py`
- `engine/optibench/lab/schemas.py`
- `engine/optibench/lab/workbench/native_interpreter.py`
- `engine/optibench/lab/workbench/solver.py`
- `engine/tests/test_api_workbench.py`
