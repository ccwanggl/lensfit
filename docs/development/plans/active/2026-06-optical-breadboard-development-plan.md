# 光学面包板开发计划与 Checkpoint

> **状态**：草案
> **日期**：2026-06-25
> **适用范围**：LensFit Self-Study Lab 的光学面包板能力，不替代镜头-传感器选型主线。
> **多 Agent 输入**：产品路线、后端/发布、前端/Lab、文档信息架构、面包板技术切片五个只读 agent 已完成评审。

## 1. 项目定位

LensFit 的主线仍是面向光学工程师和系统集成商的镜头-传感器智能匹配与工程决策工具。光学面包板不是近期主产品主线，而是 Self-Study Lab 的高级交互形态，用于把少数高价值实验从“参数滑块”升级为“场景化操作”。

本计划只推进最小可落地切片：

- 先做发布链和现有 Lab 能力一致性。
- 再做 `SceneGraph v1` 的无状态合同。
- 第一版面包板只做 `single-slit-diffraction` 的 preset 场景。
- 第一版不接真实 `ray-optics` 用户路径。
- 第一版不做通用自由画布、不做保存/加载、不做数据库迁移。

## 2. 非目标

以下内容不进入本计划第一阶段：

- 完整拖拽式光学面包板。
- 任意组件连接图求解。
- 场景持久化、分享、Undo/Redo。
- 厂商设备 catalog、库存、采购字段。
- 真实 `ray-optics` sidecar 用户路径。
- long-lived Node JSON-RPC sidecar。
- PNG / Canvas 输出链路。
- 3D / VR / CAD / FreeCAD 集成。
- 双缝、光栅、偏振、Fresnel 近场的面包板版。
- NSGA-II、通用优化器、插件市场、云同步、多用户协作。

## 3. 文档落位

本计划放在：

```text
docs/development/plans/active/2026-06-optical-breadboard-development-plan.md
```

后续建议拆分出的正式文档位置：

```text
docs/development/decisions/ADR-002-optical-breadboard-strategy.md
docs/development/research/optics-engine-landscape.md
docs/development/architecture/optics-lab/optical-breadboard-hybrid-solver.md
docs/development/specifications/lab/scene-graph-v1.md
docs/development/specifications/lab/workbench-api.md
docs/development/specifications/lab/experiment-catalog.md
```

文档规则：

- ADR 只记录决策，不放任务清单。
- research 放外部项目调研。
- architecture 放系统边界和依赖方向。
- specifications 放 API、Schema、实验合同。
- plans/active 放可执行任务和 checkpoint。

## 4. 开发路线总览

```text
阶段 0：发布链与 Lab 基线
  -> 证明当前 Python sidecar、SQLite、Lab 实验在源码和打包产物中一致

阶段 1：SceneGraph v1 合同
  -> 定义无状态场景模型，不依赖数据库，不含 ray-optics 字段

阶段 2：Workbench Native Run API
  -> 新增 /api/v1/lab/workbench/run，用 SceneGraph 运行单缝 preset

阶段 3：前端单缝面包板 preset
  -> 在 LearningHub 内展示锁定布局的 laser -> slit -> screen 场景

阶段 4：ray-optics 只读探针
  -> 验证第三方 runner 契约，但不接入用户路径

阶段 5：有限编辑与扩展评审
  -> 只有前面 checkpoint 全部通过后，才开放少量编辑能力
```

## 5. 阶段 0：发布链与 Lab 基线

### 目标

确保当前已实现的 Lab 实验、API、Python sidecar 和数据库生命周期在开发环境与打包产物中一致。没有这个基线，不进入面包板开发。

### 主要风险

- `engine/lensfit/lab/registry.py` 动态发现实验，但 `engine/build_sidecar.py` 可能只显式收集部分实验。
- PyInstaller 产物可能缺少 Alembic migration 文件。
- SQLite 生命周期和二次 lifespan 启动仍有历史风险。
- CI 未覆盖真实 sidecar 冒烟测试。

### 涉及文件

- `engine/build_sidecar.py`
- `scripts/build-desktop.py`
- `engine/lensfit/lab/registry.py`
- `engine/lensfit/api/routers/lab.py`
- `engine/tests/test_lab.py`
- `engine/tests/test_api_lab.py`
- `.github/workflows/ci.yml`

### Checkpoint 0

进入条件：

- 当前源码下 `engine/tests/test_lab.py` 和 `engine/tests/test_api_lab.py` 可运行。
- `/api/v1/lab/experiments` 能列出现有实验。

退出条件：

- 打包产物能列出与源码一致的 Lab 实验集合。
- 空 SQLite 目录启动 sidecar 后能自动迁移到当前 Alembic head。
- 真实 sidecar `/health`、`/api/v1/lab/experiments`、`/api/v1/lab/experiments/single-slit-diffraction/run` 冒烟通过。
- 连续启动/退出不残留 sidecar 进程。

验证命令：

```powershell
cd "E:/DevSpace/lensfit/engine"
python -m pytest tests/test_lab.py tests/test_api_lab.py -q
python build_sidecar.py
```

回滚条件：

- 打包产物实验缺失。
- migration 在真实二进制中不可读。
- `/health` 不通。
- 打包修复需要大规模改动 Tauri 或 Python 生命周期。

## 6. 阶段 1：SceneGraph v1 合同

### 目标

定义 LensFit 自有、solver-neutral 的 `SceneGraph v1`。它只服务无状态运行，不保存到数据库。

### 最小模型

```json
{
  "version": 1,
  "units": {
    "length": "mm",
    "angle": "deg",
    "wavelength": "nm"
  },
  "components": [
    {
      "id": "laser-1",
      "spec_id": "laser-monochrome",
      "category": "source",
      "transform": { "x_mm": 0, "y_mm": 0, "rotation_deg": 0 },
      "params": { "wavelength_nm": 550.0 }
    },
    {
      "id": "slit-1",
      "spec_id": "single-slit",
      "category": "aperture",
      "transform": { "x_mm": 100, "y_mm": 0, "rotation_deg": 0 },
      "params": { "slit_width_um": 50.0 }
    },
    {
      "id": "screen-1",
      "spec_id": "screen",
      "category": "screen",
      "transform": { "x_mm": 1100, "y_mm": 0, "rotation_deg": 0 },
      "params": {}
    }
  ],
  "observables": [
    {
      "type": "fraunhofer_intensity",
      "source_id": "laser-1",
      "aperture_id": "slit-1",
      "screen_id": "screen-1"
    }
  ]
}
```

### 涉及文件

新增：

- `engine/lensfit/lab/workbench/__init__.py`
- `engine/lensfit/lab/workbench/scene.py`
- `engine/lensfit/lab/workbench/equipment.py`
- `engine/tests/test_workbench_scene.py`

### Checkpoint 1

进入条件：

- Checkpoint 0 通过。
- 明确第一版只支持 `laser -> single_slit -> screen`。

退出条件：

- `SceneGraph.version == 1` 必填。
- `components[].id` 场景内唯一。
- `spec_id` 使用 LensFit 语义，不出现 `SingleRay`、`Detector`、`SphericalLens` 等第三方对象名。
- 缺少 source/aperture/screen 任一组件会校验失败。
- screen 与 slit 的 x 距离可推导为 `screen_distance_m`。
- `rotation_deg` 第一阶段只允许 `0`；其他值给 warning 或校验失败。

验证命令：

```powershell
cd "E:/DevSpace/lensfit/engine"
python -m pytest tests/test_workbench_scene.py -q
```

回滚条件：

- `SceneGraph` 模型泄漏 ray-optics JSON 字段。
- 第一版需要数据库才能运行。
- 模型试图覆盖通用光路编辑，导致校验规则膨胀。

## 7. 阶段 2：Workbench Native Run API

### 目标

新增无状态 API：

```text
POST /api/v1/lab/workbench/run
```

第一版只接受单缝面包板 preset，并映射到现有 `SingleSlitDiffractionExperiment.run()`。

### 涉及文件

新增：

- `engine/lensfit/lab/workbench/native_interpreter.py`
- `engine/lensfit/lab/workbench/solver.py`
- `engine/tests/test_api_workbench.py`

修改：

- `engine/lensfit/api/routers/lab.py`
- `engine/lensfit/lab/schemas.py`

### Checkpoint 2

进入条件：

- Checkpoint 1 通过。
- `SingleSlitDiffractionExperiment` 的现有测试保持通过。

退出条件：

- API 响应复用 Lab 风格：`data`、`svg`、`warnings`、`learning_hints`。
- 默认 SceneGraph 输出的 `central_max_width_mm` 与直接调用 `SingleSlitDiffractionExperiment.run({})` 一致。
- `slit_width_um` 从 20 增到 100 时中央亮纹宽度下降。
- `wavelength_nm` 从 450 增到 650 时中央亮纹宽度上升。
- screen 与 slit 距离翻倍时 `first_min_position_mm` 近似翻倍。
- Fraunhofer 条件不足时返回 warning，不伪装成精确结果。
- 现有 `/api/v1/lab/experiments/{id}/run` 无回归。

验证命令：

```powershell
cd "E:/DevSpace/lensfit/engine"
python -m pytest tests/test_lab.py tests/test_api_lab.py tests/test_api_workbench.py -q
```

回滚条件：

- 修改现有 experiment API 响应格式。
- workbench API 访问数据库、启动 Node 或读写文件。
- 单缝物理结果与现有实验出现不可解释差异。

## 8. 阶段 3：前端单缝面包板 Preset

### 目标

在现有 `LearningHub` 中承载 `single-slit-breadboard`，不启用独立通用 `BreadboardPage`。

### 涉及文件

新增：

- `apps/desktop/src/lab/BreadboardPresetRunner.tsx`
- `apps/desktop/src/lab/workbenchTypes.ts`

修改：

- `apps/desktop/src/lab/LearningHub.tsx`
- `apps/desktop/src/lab/ExperimentCatalog.tsx`
- `apps/desktop/src/lab/ParameterControl.tsx`
- `apps/desktop/src/stores/labStore.ts`
- `apps/desktop/src/utils/api.ts`

### UI 原则

- 左侧继续使用参数控件。
- 中间显示锁定布局：激光、单缝、屏幕、强度曲线。
- 右侧继续使用知识侧栏。
- 第一版不做拖拽，不做自由放置。
- 几何布局层和波动强度层必须明确标注。

### Checkpoint 3

进入条件：

- Checkpoint 2 通过。
- `LearningHub` 当前实验列表、参数运行、SVG 展示无回归。

退出条件：

- 用户能打开 `single-slit-breadboard` preset。
- 调大缝宽，中央亮纹变窄。
- 调大屏距，条纹间距变大。
- 参数变化有 loading/error 状态。
- 错误信息不暴露 ray-optics 或内部 adapter 字段。
- 移动端不出现主要内容遮挡。

验证命令：

```powershell
cd "E:/DevSpace/lensfit/apps/desktop"
npm run build
```

手动验证：

- 启动开发环境。
- 打开学习中心。
- 运行普通实验，确认无回归。
- 打开单缝面包板 preset。
- 修改波长、缝宽、屏距，确认图形和关键数据同步变化。

回滚条件：

- `LearningHub` 与旧 `LabPage` 形成双入口分叉。
- 参数面板、场景位置和结果不同步。
- 用户能摆出无法求解的系统。
- 几何阴影和衍射强度未分层，造成物理误导。

## 9. 阶段 4：ray-optics 只读探针

### 目标

验证 `ray-optics` Node runner 的最低可行集，但不接入用户路径，不影响 native workbench。

### 涉及文件

新增：

- `engine/lensfit/lab/workbench/ray_optics_sidecar.py`
- `engine/tests/test_ray_optics_contract.py`
- `docs/development/research/optics-engine-landscape.md`

### Checkpoint 4

进入条件：

- Checkpoint 0-3 通过。
- 已确认 native workbench 不依赖 Node。

退出条件：

- 固定 ray-optics 版本。
- 一个最小几何 scene 可通过 Node runner 得到稳定输出。
- 超时、非零退出、坏 JSON、缺 Node 都有归一化错误。
- stdout/stderr 有大小上限。
- scene payload 不允许任意文件路径或外部资源。
- `SceneGraph v1` fixture 不出现 ray-optics 类型名。

验证命令：

```powershell
cd "E:/DevSpace/lensfit/engine"
python -m pytest tests/test_ray_optics_contract.py -q
```

回滚条件：

- 需要未锁定网络下载。
- Windows 或 CI 无法稳定运行。
- `node-canvas` 成为必需依赖。
- 为了适配 ray-optics 修改 `SceneGraph v1`。

## 10. 阶段 5：有限编辑与扩展评审

### 目标

在前四个 checkpoint 全部通过后，评估是否开放少量场景编辑能力。

### 可考虑能力

- 只允许移动屏幕。
- 只允许切换激光波长 preset。
- 只允许编辑白名单参数。
- 一键重置默认布局。
- `labStore.sceneDrafts[presetId]` 本地草稿，不入数据库。

### Checkpoint 5

进入条件：

- Checkpoint 0-4 全部通过。
- 用户测试证明 preset 比普通滑块实验更有理解价值。

退出条件：

- 刷新后草稿可恢复。
- 重置能回到教学默认布局。
- 非法移动有明确提示。
- 序列化 SceneGraph 不包含第三方类型。
- 不引入数据库 migration。

回滚条件：

- 拖动导致参数、场景和结果不同步。
- 用户能构造不可求解拓扑。
- 需要 Undo/Redo、保存、分享才能解释交互。

## 11. 多 Agent 协同执行方式

后续执行推荐使用 subagent-driven 开发，每个任务拥有独立写入范围。

### Agent 分工

| Agent | 责任 | 写入范围 |
|---|---|---|
| 发布链 Agent | 修复 sidecar 实验收集、migration data、真实二进制冒烟 | `engine/build_sidecar.py`、CI、发布脚本、相关测试 |
| 后端 SceneGraph Agent | 实现 SceneGraph v1、校验、native interpreter | `engine/lensfit/lab/workbench/`、`engine/tests/test_workbench_scene.py` |
| API Agent | 实现 `/api/v1/lab/workbench/run` 和 API 测试 | `engine/lensfit/api/routers/lab.py`、`engine/lensfit/lab/schemas.py`、`engine/tests/test_api_workbench.py` |
| 前端 Preset Agent | 实现 `single-slit-breadboard` preset UI | `apps/desktop/src/lab/`、`apps/desktop/src/utils/api.ts`、`apps/desktop/src/stores/labStore.ts` |
| 文档 Agent | 拆分 ADR、research、architecture、specification、active plan | `docs/development/` |
| 验证 Agent | 运行测试、构建和手动验收清单 | 不改业务代码，只提交验证报告 |

### 协同规则

- 同一轮内不同 agent 不修改同一文件。
- 每个 agent 返回：修改文件、测试命令、通过/失败、风险。
- 主 agent 只做集成、冲突处理和最终验收。
- 任何阶段失败，不进入下一阶段。
- 不执行 git commit，除非用户明确要求。

## 12. 总体验收门禁

进入面包板 MVP 的最低门槛：

- 发布链 checkpoint 通过。
- `SceneGraph v1` 不依赖第三方对象名。
- workbench API 是 stateless。
- 单缝物理结果与现有实验一致。
- 前端只做 preset，不做自由画布。

进入 ray-optics adapter 的最低门槛：

- native workbench 已稳定。
- Node runner 合同测试可在目标平台通过。
- adapter 失败不会影响现有 Lab。
- 许可证、版本 pin、NOTICE 策略明确。

进入通用画布的最低门槛：

- 至少两个 preset 证明场景式交互比参数实验更有价值。
- SceneGraph migration 策略明确。
- 后端校验能拒绝不可求解拓扑。
- 前端状态、选择、属性、运行结果同步机制稳定。

## 13. 当前结论

本计划建议立即执行阶段 0。阶段 1-3 可以在阶段 0 通过后作为一个小版本完成。阶段 4 只能作为独立探针，不能阻塞 native 面包板。阶段 5 以后需要重新评审。

核心原则：先让 LensFit 成为可信的选型工具，再让 Lab 成为可信的解释层，最后才让面包板成为可信的场景化实验环境。
