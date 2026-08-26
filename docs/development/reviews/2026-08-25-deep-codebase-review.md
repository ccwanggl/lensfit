# 2026-08-25 代码库深度评审报告

> 评审范围：OptiBench 全仓（engine / apps/desktop / scripts / CI / docs）
> 触发背景：产品更名 LensFit → OptiBench 落地后，对代码库做一次全面体检。
> 方法：静态扫描 + 实际运行验证（pytest / vitest / tsc / ruff / alembic），非纯文档推断。

## 1. 总体结论

代码库处于**健康偏良**状态：改名执行质量高，测试体系真实有效，核心链路全部验证通过。主要债务集中在三处：CI lint 门禁红、架构文档滞后于学习优先转向、前端大组件。

## 2. 验证结果（实际运行）

| 检查项 | 结果 | 备注 |
|---|---|---|
| 后端 pytest | ✅ 388 passed / 37s | 23 个测试文件，含 lifecycle/migrations/ray-optics contract |
| 前端 vitest | ✅ 59 passed (9 files) | LearningHub/PathView/QuizPanel/TutorialView/workbenchTypes 均有测试 |
| 前端 tsc --noEmit | ✅ 通过 | strict 类型检查干净 |
| 后端 ruff check | ❌ 42 errors | 见 §4-H1 |
| Alembic | ✅ 单 head `004`，7 个迁移 | script_location = optibench/db/migrations |
| 版本一致性 | ✅ 全部 1.1.0 | pyproject / package.json / tauri.conf / VERSION / server.py，另有 sync-version.py 维持 |

## 3. 改名（LensFit → OptiBench）落地评估

### 3.1 已完成且质量良好

- Python 包 `lensfit` → `optibench`；PyPI 名 `optibench-engine`；Tauri identifier `com.optibench.app`；sidecar 二进制 `optibengin-engine-*` 全链路更新。
- 数据库迁移：`server.py::_migrate_legacy_db` 启动时自动把旧 `lensfit.db` 重命名为 `optibench.db`（含 `-wal`/`-shm` 伴生文件）。
- localStorage 旧键兼容回退：`labStore.ts`（`lensfit-lab-store`）、`useTheme.ts`、`useLearningProgress.ts` 均保留 legacy key fallback。
- 环境变量 `LENSFIT_API_KEY` → `OPTIBENCH_API_KEY`。
- CHANGELOG 完整记载改名事项；README 中"原名 LensFit"为有意的历史记载，应保留。

### 3.2 残留物（建议清理）

**git 追踪的 stale 文件（会随仓库继续扩散）：**

| 文件 | 性质 |
|---|---|
| `engine/lensfit-engine-x86_64-unknown-linux-gnu.spec` | 旧 PyInstaller spec，当前 build_sidecar.py 动态生成 optibench 命名的 spec，此文件已死 |
| `apps/desktop/src-tauri/lensfit-engine-x86_64-unknown-linux-gnu` | 旧 sidecar 占位二进制（位于 src-tauri 根而非 binaries/），无引用 |

**仅存在于本机、未被 git 追踪：**

- `engine/lensfit-engine-amd64-pc-windows-msvc.exe.spec`
- `engine/lensfit-engine-x86_64-pc-windows-msvc.exe.spec`
- `engine/lensfit.db`（旧开发库，新库 `optibench.db` 已在使用）

清理以上文件不影响任何构建路径（tauri.conf.json externalBin 已指向 `binaries/optibench-engine`，binaries/ 未被 git 追踪，按平台现场构建）。

## 4. 问题清单（按严重度）

### H1（High）：CI lint 门禁红

`ruff check optibench/` 报 42 errors：

| 规则 | 数量 | 可自动修复 |
|---|---|---|
| E501 line-too-long | 30 | 否 |
| F401 unused-import | 6 | 是 |
| E741 ambiguous-variable-name | 3 | 否 |
| F841 unused-variable | 2 | 是(部分) |
| I001 unsorted-imports | 1 | 是 |

CI（`.github/workflows/ci.yml::test-engine`）在每次 push 都会因此失败。7 处可 `ruff check --fix`，E501/E741 需手工小改。集中出现于 ray 追迹类可视化代码（如 SVG 生成处的长行）。

### H2（High）：架构文档滞后于 2026-08 学习优先转向

`docs/development/architecture/` 下没有任何文档提及转向后落地的模块：

- 后端：`optibench/content/`、`optibench/curriculum/`、`optibench/practice/`、`learning_records` 表（migration 004）、`api/routers/{content,curriculum,learning}.py`
- 前端：`LearningHub.tsx`、`PathView.tsx`、`TutorialView.tsx`、`QuizPanel.tsx`

关键词全文检索命中数为 0。违反 AGENTS.md「architecture 只描述已经落地或明确标为目标状态的设计」的双向约定——已落地却未描述。注意存在 `scripts/update_arch_docs.py`，可能只需运行即可部分修复。

另：`2026-08-learning-first-repositioning-plan.md` 的阶段 0–3 按 git 历史与 README 描述均已落地，但计划文档未像面包板计划那样标注完成状态，属于 active plan 文档债。

### M1（Medium）：前端巨型组件与四域重复编排

- `lab/LearningHub.tsx` 33KB（约千行级），承载路径/沙盘/教程多视图调度。
- 四个实践域页面高度同构：IndustrialPage 694 行 / MicroscopePage ~695 / PhotographyPage ~620 / InfraredPage ~627，另有配套 `*LearningHub.tsx` 各 20–27KB。
- 缓解因素：已共享 `useMatching`、`DomainForm`、`SensorCoveragePlot` 等核心，并非纯复制粘贴；重复的是各域的编排层。
- 建议（需另行立项进 active plan，不在本次执行）：抽取 DomainPageShell/配置驱动表单，LearningHub 按视图拆分。

### M2（Medium）：发布链的隐性手工同步点

`engine/build_sidecar.py` 的 hidden_imports 为 40+ 条硬编码清单（实验部分已有 autodiscovery，其余模块靠人工维护）。本次改名与新包（content/practice/curriculum）都已正确加入，但后续每个新包都要记得同步，漏掉只在打包产物中暴露。可考虑对一级子包统一 `--collect-submodules`。

### L1（Low）：杂项卫生

- `server.py` lifespan 关闭时 `except Exception: pass` 吞异常；全局 `_engine/_session_maker` 单例为测试兼容而保留（代码内已注释说明）。可接受，记录在案。
- pytest warnings：alembic `path_separator` deprecation 提示（alembic.ini 已设 `version_path_separator`，新版本 alembic 期望键名不同，升级时一并处理）。
- 仓库根存在 `middleware_error.log`、`server_error.log`，建议确认是否该入库并补充 .gitignore。

## 5. 与 active plan 的关系

本报告只陈述事实与风险，不构成执行计划。若要处置上述问题，按 AGENTS.md 约定应：

1. H1/H3.2（lint 修复 + stale 文件清理）：体量小，可作为 quick fix 征得确认后直接执行；
2. H2（架构文档补写）：先确认 `scripts/update_arch_docs.py` 能力边界，再决定手工补写或脚本生成；
3. M1（前端重构）：必须先立 active plan 再动工。

## 6. 评审证据命令复现

```powershell
cd E:\OpticHackerSpace\OptiBench\engine
& ..\.venv\Scripts\python.exe -m pytest -q            # 388 passed
& ..\.venv\Scripts\ruff.exe check optibench/          # 42 errors

cd ..\apps\desktop
npx tsc --noEmit                                       # pass
npx vitest run                                         # 59 passed

cd ..
& .venv\Scripts\python.exe -m alembic heads   # 在 engine 目录下执行 → 004 (head)
```
