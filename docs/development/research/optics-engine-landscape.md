# 光学引擎选型调研

> 调研日期：2026-06-25  
> 范围：几何光学追迹引擎与波动光学求解方案  
> 目标：为 LensFit 光学面包板阶段 4 及后续扩展提供决策依据

## 1. 选型结论

LensFit 采用**混合架构**：

- **几何光学 / 面包板布局**：复用开源 **[ray-optics](https://github.com/ricktu288/ray-optics)**（Apache-2.0），通过其 Node 集成工具以 sidecar 形式接入。
- **波动 / 干涉 / 衍射**：保留 LensFit 原生 Python 求解器，避免把波动现象硬塞进几何追迹引擎。
- **域模型隔离**：`SceneGraph v1` 是 LensFit 自有语义；`ray-optics` JSON 仅在 adapter 内部使用，不泄漏到前端载荷或持久化场景。

## 2. 候选方案对比

| 方案 | 几何追迹 | 波动光学 | 集成方式 | 许可证 | 主要缺点 |
|---|---|---|---|---|---|
| **A. ray-optics iframe 嵌入** | 完整 | 无 | iframe | Apache-2.0 | UI 不可控、难以与设备目录/参数面板联动 |
| **B. ray-optics Node sidecar** | 完整 | 无 | stdin/stdout JSON | Apache-2.0 | 每请求启动 Node；`node-canvas` 原生依赖 |
| **C. 自研 Python 追迹器** | 按需 | 按需 | 内嵌 | 自有 | 开发成本高、几何元件生态需自建 |
| **D. 混合架构（选中）** | ray-optics sidecar | Python 原生 | adapter | Apache-2.0 + 自有 | 需要维护两套 runtime 与 adapter 映射 |

## 3. ray-optics 关键信息

- **仓库**：https://github.com/ricktu288/ray-optics
- **许可证**：Apache-2.0，需保留 `NOTICE`/`LICENSE`。
- **当前固定版本**：`5.3.2`（vendored 于 `engine/third_party/ray-optics`）。
- **集成入口**：`dist-integrations/runner.js`，通过 stdin 接收场景 JSON，stdout 返回结果 JSON。
- **Node 依赖**：
  - 基础探测器读取：仅需 Node.js，无需 `canvas`。
  - 图像 / CropBox 输出：需要 `node-canvas`（平台原生依赖）。
- **输出字段**：
  - `detectors[]`：能量流 `power`、法向动量流 `normal`、切向动量流 `shear`，可选 `irradianceMap`/`binPositions`。
  - `images[]`：base64 PNG data URL（需 canvas）。
  - `error` / `warning`：场景级错误/警告。
  - `totalTruncation` / `processedRayCount` / `brightnessScale`：统计信息。

## 4. 集成边界

```text
LensFit SceneGraph v1
        |
        v
  SolverDispatcher
   /           \
  v             v
RayOpticsSidecar   NativeExperimentSolver
  |                     |
  v                     v
node runner.js     Python experiments
  |                     |
  v                     v
{detectors, images}   {data, svg, warnings}
```

- 禁止反向依赖：`ray-optics` 的 JSON 类型名（`SingleRay`、`Detector`、`CropBox`、`SphericalLens` 等）不得出现在 `SceneGraph v1` 中。
- Adapter 负责把 LensFit 语义组件（`laser-monochrome`、`thin-lens`、`screen` 等）翻译成 ray-optics 场景 JSON。
- 若未来替换几何引擎，只需重写 adapter；已保存的 `SceneGraph` 仍然有效。

## 5. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| `node-canvas` 在某些平台构建失败 | 高 | 第一版仅使用探测器读取；图像输出降级为 SVG-only |
| `ray-optics` JSON 格式随版本变化 | 中 | 固定版本 `5.3.2`；版本锁定文件；合同测试覆盖最小场景 |
| 每请求启动 Node 开销大 | 中 | 先测量，必要时引入 long-lived sidecar，但不在阶段 4 引入 |
| 几何与波动可视化不一致 | 中 | UI 分层标注“几何光线 / 波动强度” |

## 6. 备选方案简述

- **Python `rayoptics` 包**（https://github.com/mjhoptics/rayoptics）：序列光学设计，API 面向镜头设计而非交互式面包板；与 LensFit 的场景化学习路径不匹配。
- **自研 Python 追迹器**：可控但开发周期长，需实现透镜、反射镜、光阑、探测器等完整元件集。
- **其他 Web 模拟器（如 GeoGebra、PhET）**：多为教育演示，缺乏可编程接口与许可证兼容性。

## 7. 参考

- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `engine/third_party/ray-optics/README.md`
- `engine/third_party/ray-optics/LICENSE`
- https://phydemo.app/ray-optics/docs/index.html
