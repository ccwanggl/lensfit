# 光学面包板阶段 4 评审报告

> 评审日期：2026-06-25  
> 评审范围：`docs/development/plans/active/2026-06-optical-breadboard-development-plan.md` 阶段 4：ray-optics 只读探针  
> 评审方式：代码走查、合同测试运行、与 ADR-002 架构边界对照

## 1. 结论

**阶段 4 验收通过。**

`ray-optics` 已作为只读 sidecar 探针接入，但未进入任何用户路径。`RayOpticsSidecar` 对超时、非零退出、坏 JSON、缺 Node、输出超限、文件路径等风险都做了归一化错误处理。`SceneGraph v1` 仍保持 solver-neutral，未出现 ray-optics 类型名。

## 2. 实现概览

新增文件：

```text
engine/optibench/lab/workbench/ray_optics_sidecar.py
engine/tests/test_ray_optics_contract.py
docs/development/research/optics-engine-landscape.md
engine/third_party/ray-optics/{README.md,LICENSE,runner.js,rayOptics.js,example_*.py,.gitignore}
```

修改文件：

```text
docs/development/plans/active/2026-06-optical-breadboard-development-plan.md
```

## 3. 逐项检查

### 3.1 退出条件

| active plan 要求 | 实现 | 状态 |
|---|---|---|
| 固定 ray-optics 版本 | `engine/third_party/ray-optics/README.md` 声明 `Version: 5.3.2`；版本锁定测试覆盖 | ✅ |
| 最小几何 scene 可得到稳定输出 | `test_minimal_detector_scene_runs` 使用 SingleRay + Detector，断言 power/normal/shear/irradianceMap | ✅ |
| 超时、非零退出、坏 JSON、缺 Node 都有归一化错误 | 分别映射到 `RayOpticsTimeoutError`、`RayOpticsRuntimeError`、`RayOpticsOutputError`、`RayOpticsNotAvailableError` | ✅ |
| stdout/stderr 有大小上限 | `max_stdout_bytes` / `max_stderr_bytes` 在输出解析前检查 | ✅ |
| scene payload 不允许任意文件路径或外部资源 | `_validate_payload` 递归拒绝含 `/`、`\`、`://` 的字符串 | ✅ |
| `SceneGraph v1` fixture 不出现 ray-optics 类型名 | `test_scenegraph_fixture_has_no_ray_optics_types` 扫描序列化 JSON | ✅ |

### 3.2 架构边界

- `SceneGraph` 模型未修改，未引入 ray-optics 字段。
- `RayOpticsSidecar` 位于独立模块，native workbench 完全不依赖 Node。
- `SolverDispatcher` 尚未接入 ray-optics，保持 native 路径不变。
- 第三方 JS 仅作为 vendored 副本存在，未污染 Python 依赖。

### 3.3 构建与测试

| 检查项 | 命令 | 结果 |
|---|---|---|
| ray-optics 合同测试 | `pytest tests/test_ray_optics_contract.py -q` | **13 passed** |
| 后端全量回归 | `pytest -q` | **150 passed, 4 warnings** |
| 代码风格 | `ruff check ...` | **通过** |

### 3.4 风险缓解

| ADR-002 风险 | 阶段 4 处理 |
|---|---|
| `node-canvas` 原生依赖失败 | 测试仅使用 Detector，未启用 CropBox / PNG 输出；`node-canvas` 不是必需依赖 |
| ray-optics JSON 格式随版本变化 | 版本锁定 `5.3.2`；README 版本断言测试 |
| 每请求启动 Node 开销 | 尚未测量，但 sidecar 为无状态 subprocess；long-lived sidecar 不在本阶段 |
| OptiBench 域模型耦合到 ray-optics JSON | `SceneGraph` 拒绝 ray-optics spec_id；adapter 未写入，保持隔离 |

## 4. 发现与建议

### 4.1 已确认的设计选择

1. **Vendored 副本优于 npm install**

   将 `integrations-build.zip` 解压到 `engine/third_party/ray-optics/` 后，测试无需网络即可运行，满足 active plan 的“不需要未锁定网络下载”回滚条件。

2. **仅使用 Detector 读取能力**

   合同测试不启用 CropBox，因此 `node-canvas` 不是阶段 4 的必需依赖。这降低了 Windows/CI 不稳定风险。

3. **异常家族化**

   `RayOpticsError` 子类让调用层可以区分“环境不可用”与“运行时错误”，便于未来 UI 降级到 native workbench。

### 4.2 建议改进（非阶段 4 阻塞项）

1. **增加 SceneGraph → ray-optics adapter 测试**

   当前只验证了 runner 合同。下一阶段若要让 `WorkbenchSolver` 分发几何追迹，需要新增 adapter 模块及其测试。

2. **测量 Node 启动开销**

   在接入用户路径前，应测量单次 `subprocess.run` 的延迟，以决定是否引入 long-lived sidecar。

3. **完善路径/URL 校验**

   当前正则仅检查 `/`、`\`、`://`。后续可引入更严格的 JSON schema 校验，拒绝更多可疑字段（如 `import`、模块 URL 等）。

4. **考虑 NOTICE 文件 placement**

   `third_party/ray-optics/LICENSE` 已保留。若未来打包 sidecar，需在分发产物中保留 Apache-2.0 所需的 NOTICE。

## 5. 阶段 4 退出条件对照

| 退出条件 | 状态 |
|---|---|
| 固定 ray-optics 版本 | ✅ |
| 最小几何 scene 稳定输出 | ✅ |
| 超时、非零退出、坏 JSON、缺 Node 归一化错误 | ✅ |
| stdout/stderr 大小上限 | ✅ |
| scene payload 不允许文件路径/外部资源 | ✅ |
| `SceneGraph v1` fixture 不出现 ray-optics 类型名 | ✅ |
| 不影响 native workbench | ✅ |
| 不接入用户路径 | ✅ |

## 6. 进入阶段 5 的前提

阶段 4 已满足进入阶段 5 的全部条件。建议在阶段 5 开始前：

1. 提交阶段 4 改动（已取得用户确认后再执行 `git commit`）。
2. 阶段 5 目标是在前四个 checkpoint 全部通过后，评估是否开放少量场景编辑能力。应保持 `SceneGraph` 稳定，避免引入通用自由画布。

## 7. 参考

- `docs/development/plans/active/2026-06-optical-breadboard-development-plan.md`
- `docs/development/decisions/ADR-002-optical-breadboard-strategy.md`
- `docs/development/research/optics-engine-landscape.md`
- `engine/optibench/lab/workbench/ray_optics_sidecar.py`
- `engine/tests/test_ray_optics_contract.py`
- `engine/third_party/ray-optics/README.md`
