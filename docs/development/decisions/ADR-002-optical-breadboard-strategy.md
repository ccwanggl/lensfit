# ADR-002：光学面包板 / 数字孪生策略

**状态**：提议  
**日期**：2026-06-12  
**作者**：OptiBench 架构团队  
**范围**：确定 Self-Study Optics Lab 向“设备化光学面包板（数字孪生）”演进的架构方向。具体执行计划见 `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`。

## 1. 背景

用户希望把 OptiBench 扩展成一个**物理光学实验室的数字孪生**：

1. 具备器材库（激光器、透镜、光阑、光栅、探测器等）。
2. 能在二维光学平板/面包板上摆放并连接这些器材。
3. 可运行基础实验，例如**单缝衍射光强分布**。

这是一个长期、多阶段的大型功能。核心架构问题是：几何光学模拟部分应该自研、嵌入第三方应用，还是通过适配器复用成熟引擎。

## 2. 决策

**采用混合架构（D 方案）：**

- **几何光学面包板**：复用开源的 **[ray-optics](https://github.com/ricktu288/ray-optics)**（Apache-2.0），通过其 Node 集成工具以侧车（sidecar）方式接入。
- **波动/干涉/衍射实验**：保留 OptiBench 原生 Python 求解器，避免把波动光学硬塞进几何追迹引擎导致物理失真。
- **领域模型隔离**：OptiBench 的 `SceneGraph` 是稳定的产品域模型；`ray-optics` 的 JSON 只作为适配器内部表示，不允许泄漏到保存场景或前端载荷中。

## 3. 主要候选方案对比

| 维度 | A. 嵌入 ray-optics 网页（iframe） | B. ray-optics Node 侧车 | C. 自研 Python 追迹器 | D. 混合架构（推荐） |
|---|---|---|---|---|
| 功能覆盖 | 完整网页功能，但难以控制界面 | 几何追迹 + 探测器/PNG 输出 | 取决于实现，成本高 | 几何侧车 + 波动原生 |
| 面包板 UX 可控性 | 低 | 高 | 高 | 高 |
| 波动光学支持 | 不支持 | 不支持 | 自研 | Python 原生 |
| 集成成本 | 快但脆弱 | 中等 | 高 | 中等，可增量 |
| 许可证 | Apache-2.0 需保留 NOTICE | Apache-2.0 需保留 NOTICE | 自有 | Apache-2.0 + 自有 |
| 中文本地化 | 部分 | 完整（UI 由 OptiBench 提供） | 完整 | 完整 |
| 设备目录集成 | 无 | 目录生成场景 JSON | 全部自建 | 目录生成场景图 |

## 4. 架构边界

依赖方向必须是：

```text
OptiBench SceneGraph -> Solver Adapter -> 第三方/原生引擎
```

禁止反向依赖：

```text
ray-optics scene JSON -> OptiBench 域模型
```

即使未来替换 `ray-optics`，已保存的 OptiBench 场景和前端载荷也应只需修改适配器即可继续生效。

## 5. 高层架构

```text
┌─────────────────────────────────────────────┐
│              apps/desktop（React/Vite）       │
│        BreadboardCanvas / ParameterPanel     │
└─────────────────────┬───────────────────────┘
                      │ SceneGraph JSON
┌─────────────────────▼───────────────────────┐
│        engine/optibench/lab/workbench/         │
│  OpticalWorkbench -> SolverDispatcher        │
│     ├─ RayOpticsSidecar（几何追迹）          │
│     └─ WaveSolver（波动光学）                │
└─────────────────────┬───────────────────────┘
                      │ {data, svg, warnings}
┌─────────────────────▼───────────────────────┐
│     FastAPI /api/v1/lab/workbench/run        │
└─────────────────────────────────────────────┘
```

## 6. 关键约束

- `SceneGraph` 必须是无状态、solver-neutral 的，当前版本为 `v1`。
- `SceneGraph` 中只能出现 OptiBench 语义字段（如 `laser-monochrome`、`single-slit`、`screen`），不能出现 `SingleRay`、`SphericalLens`、`Detector` 等第三方对象名。
- 设备目录（`EquipmentSpec`）与求解器映射（`SolverMapping`）分离，避免目录模型被第三方字段污染。
- 波动光学可观测值（如 `fraunhofer_intensity`）由 OptiBench 原生计算；几何布局可由 `ray-optics` 渲染；两者通过 `composer` 分层叠加，并明确标注“几何光线”与“波动强度”。

## 7. ray-optics 集成要点

- 使用 `dist-integrations/runner.js` 作为侧车入口；Python 后端通过 stdin 传入场景 JSON，stdout 获取结果 JSON。
- 必须固定 `ray-optics` 版本，并建立合同测试覆盖最小几何场景。
- 生产包装器必须包含：超时、进程清理、非零退出处理、stdout/stderr 大小上限、JSON schema 校验、禁止任意文件路径。
- `node-canvas` 仅用于 PNG 输出；如平台不支持，应降级为 SVG-only。

## 8. 风险与缓解

| 风险 | 影响 | 缓解 |
|---|---|---|
| `node-canvas` 原生依赖在某些平台失败 | 高 | SVG-only 降级；CI 预构建侧车 |
| `ray-optics` JSON 格式随版本变化 | 中 | 固定版本；版本门控测试 |
| 每请求启动 Node 开销过大 | 中 | 先测量，必要时再引入 long-lived sidecar |
| OptiBench 域模型耦合到 ray-optics JSON | 高 | 映射表隔离；测试保存场景不含第三方类型名 |
| 几何与波动可视化不一致 | 中 | 明确分层标注 |

## 9. 与当前执行计划的关系

本 ADR 只记录**战略决策**。第一阶段不直接进入 ray-optics 用户路径，而是按 `plans/active/2026-06-optical-breadboard-development-plan.md` 执行：

1. 阶段 0：发布链与 Lab 基线。
2. 阶段 1：`SceneGraph v1` 无状态合同。
3. 阶段 2：`/api/v1/lab/workbench/run` native 单缝 preset。
4. 阶段 3：前端单缝面包板 preset。
5. 阶段 4：ray-optics 只读探针（合同验证，不接入用户路径）。
6. 阶段 5 及以后：重新评审。

## 10. 参考

- [ricktu288/ray-optics](https://github.com/ricktu288/ray-optics)
- [Ray Optics 文档](https://phydemo.app/ray-optics/docs/index.html)
- [Ray Optics 集成工具](https://github.com/ricktu288/ray-optics/tree/dist-integrations)
- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/architecture/optics-lab/self-study-lab-architecture.md`
