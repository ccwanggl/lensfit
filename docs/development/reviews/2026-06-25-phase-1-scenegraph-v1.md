# 光学面包板阶段 1 评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 1：SceneGraph v1 合同  
> 评审方式：代码走查、测试运行、与 active plan 退出条件逐项对照

## 1. 结论

**阶段 1 验收通过。**

`SceneGraph v1` 已实现为 solver-neutral、无状态、不依赖数据库的 Pydantic 模型，满足 active plan 的所有退出条件。代码通过 Ruff 检查，新增 11 个测试全部通过，全量测试无回归。

## 2. 实现概览

新增 `engine/lensfit/lab/workbench/` 包：

```text
engine/lensfit/lab/workbench/
  __init__.py     # 公共导出
  scene.py        # SceneGraph v1 模型与校验
  equipment.py    # 最小内存设备目录
```

新增测试：

```text
engine/tests/test_workbench_scene.py
```

## 3. 逐项检查

### 3.1 模型结构

| active plan 要求 | 实现 | 状态 |
|---|---|---|
| `version == 1` 必填 | `version: Literal[1]` | ✅ |
| 单位：`mm`、`deg`、`nm` | `Units` 模型，固定字面量 | ✅ |
| 组件：`id`、`spec_id`、`category`、`transform`、`params` | `Component` 模型 | ✅ |
| 可观测：`fraunhofer_intensity` | `Observable` 模型 | ✅ |
| `transform` 含 `x_mm`、`y_mm`、`rotation_deg` | `Transform` 模型 | ✅ |

### 3.2 校验规则

| 退出条件 | 实现 | 测试覆盖 | 状态 |
|---|---|---|---|
| `components[].id` 场景内唯一 | `_unique_component_ids` | `test_duplicate_id_fails` | ✅ |
| `spec_id` 使用 LensFit 语义，无第三方对象名 | `Literal["laser-monochrome", "single-slit", "screen"]` | `test_unknown_spec_id_fails` | ✅ |
| 缺少 source/aperture/screen 任一组件会校验失败 | `_validate_scene` 统计各类别数量 | `test_missing_component_fails` | ✅ |
| screen 与 slit 的 x 距离可推导为 `screen_distance_m` | `screen_distance_m()` | `test_screen_distance_derived_from_x_positions` | ✅ |
| `rotation_deg` 第一阶段只允许 `0` | `_validate_scene` 检查 | `test_rotation_nonzero_fails` | ✅ |
| observable 引用存在 | `_validate_scene` 检查 | `test_unknown_observable_reference_fails` | ✅ |

### 3.3 测试与静态检查

| 检查项 | 命令 | 结果 |
|---|---|---|
| SceneGraph 专项测试 | `pytest tests/test_workbench_scene.py -q` | **11 passed** |
| 全量回归测试 | `pytest -q` | **131 passed, 4 warnings** |
| 静态检查 | `ruff check lensfit/lab/workbench tests/test_workbench_scene.py` | 通过 |

### 3.4 与现有代码的隔离

- `workbench` 包不导入任何 FastAPI、数据库或第三方光学引擎模块。
- `SceneGraph` 不访问文件系统、环境变量或网络。
- `equipment.py` 仅包含内存中的 `EquipmentSpec` 定义，无 Alembic 或持久化逻辑。
- `scene.py` 中的 `params_for` 在方法内部导入 `CATALOG`，避免循环依赖风险，同时保持模块边界清晰。

## 4. 发现与建议

### 4.1 已确认的设计选择

1. **严格解释“缺少组件”为“必须且只能有一个”**

   active plan 的退出条件原文是“缺少 source/aperture/screen 任一组件会校验失败”。当前实现要求**恰好一个** source、aperture 和 screen。这在 SceneGraph v1 的 `laser -> single_slit -> screen` 预设场景下是合理的，也防止了未来过度扩展。

2. **`rotation_deg != 0` 直接报错**

   active plan 允许“warning 或校验失败”。当前实现选择校验失败，使前端可以在提交前就发现不支持旋转，符合“先读后写”的严格模型。

3. **距离推导只考虑 x 轴**

   `screen_distance_m()` 使用 `screen.x_mm - aperture.x_mm`，忽略 y 轴偏移。这与 v1 的直线光轴预设一致，已在注释中说明。

### 4.2 建议改进（非阶段 1 阻塞项）

1. **错误信息本地化/产品化**

   当前校验错误是英文，例如 `"component ids must be unique within a scene"`。未来前端展示时可能需要映射为中文用户提示。

2. **`params_for` 可改为顶层导入**

   目前 `params_for` 在方法内部 `from lensfit.lab.workbench.equipment import CATALOG`。虽然能避免循环依赖，但顶层导入更清晰。当前包内没有循环依赖风险，可以考虑重构。

3. **扩展设备目录时避免 Literal 硬编码**

   `spec_id` 当前使用 `Literal`。当 Phase 5 引入更多设备时，可能需要改为动态校验（例如从 `CATALOG` 键集合中验证），否则每次新增设备都要修改 `scene.py`。

4. **补充 `SceneGraph` 序列化/反序列化示例文档**

   建议把 active plan 中的最小 JSON 示例复制到 `docs/development/specifications/lab/scene-graph-v1.md`，作为正式 API 契约。可在阶段 2 完成后一并补充。

## 5. 阶段 1 退出条件对照

| 退出条件 | 状态 | 备注 |
|---|---|---|
| `SceneGraph.version == 1` 必填 | ✅ | `Literal[1]` |
| `components[].id` 场景内唯一 | ✅ | 已测试 |
| `spec_id` 使用 LensFit 语义，无第三方对象名 | ✅ | `Literal` 限制 |
| 缺少 source/aperture/screen 任一组件会校验失败 | ✅ | 严格为恰好一个 |
| screen 与 slit 的 x 距离可推导为 `screen_distance_m` | ✅ | 已测试 |
| `rotation_deg` 第一阶段只允许 `0` | ✅ | 已测试 |
| 不依赖数据库 | ✅ | 纯内存模型 |
| 无 ray-optics 字段泄漏 | ✅ | 无第三方字段 |

## 6. 进入阶段 2 的前提

阶段 1 已满足进入阶段 2 的全部条件。建议在阶段 2 开始前：

1. 提交阶段 1 改动（已取得用户确认后再执行 `git commit`）。
2. 在阶段 2 中实现 `POST /api/v1/lab/workbench/run`，将上述 `SceneGraph` 映射到 `SingleSlitDiffractionExperiment.run()`。
3. 在阶段 2 完成后再补充 `docs/development/specifications/lab/scene-graph-v1.md` 正式契约文档。

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `engine/lensfit/lab/workbench/scene.py`
- `engine/lensfit/lab/workbench/equipment.py`
- `engine/tests/test_workbench_scene.py`
