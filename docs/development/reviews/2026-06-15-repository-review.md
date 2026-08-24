# OptiBench 仓库审查报告

> 审查日期：2026-06-15  
> P1 修复复核日期：2026-06-15  
> 审查范围：Python 引擎、FastAPI、数据库与迁移、React 前端、Tauri 桌面壳、构建脚本、CI、测试、设计文档和本地数据  
> 审查方式：静态代码审阅、设计与实现对照、测试和构建验证、数据库检查、PyInstaller 归档检查  
> 本次审查未修改业务代码

## 1. 结论

OptiBench 已经具备完整工程原型的基本形态，不是停留在界面或算法演示阶段。四个应用领域的匹配流程、器件目录、项目快照、报告导出、知识推理、可视化和 Tauri sidecar 均有实际实现，后端测试、前端构建和 Rust 静态检查也能通过。

当前版本适合继续做内部试用和领域验证，但不建议直接作为稳定桌面产品发布。主要风险集中在三处：

1. 打包后的 sidecar 与源码能力不完全一致，现有产物缺少最新数据库迁移。
2. 异步匹配、任务进度和取消机制只有基础实现，无法支撑并发任务和真实渐进反馈。
3. 算法与数据缺少系统化的可信度验证，现有测试更偏向代码行为正确，尚不足以证明选型结果可靠。

建议先完成一个稳定化周期，再继续扩展功能。短期工作应放在发布链、任务模型、数据库生命周期和回归测试上。

## 2. 仓库现状

### 2.1 技术结构

仓库采用单仓结构：

| 层次 | 主要技术 | 当前职责 |
|---|---|---|
| 桌面界面 | React 19、TypeScript、Vite、Tailwind CSS | 参数输入、结果展示、对比、项目与器件库管理 |
| 桌面壳 | Tauri 2、Rust | 启动 Python sidecar、随机端口、健康检查、API 密钥传递 |
| 服务层 | FastAPI、Pydantic | 匹配、目录、知识库、可视化、项目和导出 API |
| 计算层 | Python、NumPy、SciPy | 光学计算、领域约束、评分和 TOPSIS 排序 |
| 数据层 | SQLAlchemy、Alembic、SQLite | 厂商、镜头、探测器、项目快照和兼容性缓存模型 |
| 打包 | PyInstaller、Tauri CLI | Python 单文件 sidecar 和桌面安装包 |

代码已经覆盖工业视觉、摄影、显微镜和红外成像四个领域。当前本地数据库包含：

| 数据 | 数量 |
|---|---:|
| 厂商 | 19 |
| 镜头 | 91 |
| 探测器 | 48 |
| 项目 | 0 |
| 项目方案 | 0 |
| 兼容性缓存 | 0 |

镜头和探测器目录中没有发现相同厂商与型号的重复记录。

### 2.2 Git 状态

审查时工作区状态如下：

- 当前分支：`master`
- 相对 `origin/master`：领先 16 个提交
- 已修改：`engine/optibench/api/catalog_router.py`
- 已修改：`engine/optibench/api/server.py`
- 未跟踪：`log_config.json`

这些改动被视为当前开发状态的一部分，本次审查未覆盖或回退它们。

### 2.3 代码规模

后端较大的模块：

| 文件 | 行数 |
|---|---:|
| `engine/optibench/matching/engine.py` | 1085 |
| `engine/optibench/api/server.py` | 873 |
| `engine/optibench/knowledge/presets.py` | 639 |
| `engine/optibench/api/catalog_router.py` | 574 |

前端较大的模块：

| 文件 | 行数 |
|---|---:|
| `apps/desktop/src/pages/MicroscopePage.tsx` | 736 |
| `apps/desktop/src/pages/ProjectsPage.tsx` | 708 |
| `apps/desktop/src/pages/IndustrialPage.tsx` | 706 |
| `apps/desktop/src/pages/InfraredPage.tsx` | 672 |
| `apps/desktop/src/pages/PhotographyPage.tsx` | 657 |
| `apps/desktop/src/components/KnowledgePanel.tsx` | 645 |
| `apps/desktop/src/utils/api.ts` | 610 |

这些模块已经承担过多职责。继续直接添加功能，会增加领域间规则漂移和回归风险。

## 3. 验证结果

### 3.1 已通过的检查

| 检查 | 命令 | 结果 |
|---|---|---|
| 后端测试 | `python -m pytest -q` | 47 项通过，1 条依赖弃用警告 |
| 后端静态检查 | `python -m ruff check .` | 通过 |
| 后端覆盖率 | `pytest --cov=optibench` | 总覆盖率约 70% |
| 前端构建 | `npm run build` | TypeScript 和 Vite 构建通过 |
| Rust 检查 | `cargo check` | 通过 |
| Alembic | `alembic heads` | 唯一 head：`0ac6c641b5d7` |
| 数据检查 | SQLite 查询 | 表结构可用，无目录重复记录 |

### 3.2 覆盖率薄弱区域

| 模块 | 覆盖率 |
|---|---:|
| `visualization/coverage.py` | 0% |
| `knowledge/constraints.py` | 22% |
| `export/excel_exporter.py` | 29% |
| `export/pdf_exporter.py` | 40% |
| `core/utils.py` | 41% |
| `knowledge/engine.py` | 49% |
| `api/import_pipe.py` | 58% |
| `api/server.py` | 61% |

测试运行期间出现多次 SQLite 连接未关闭警告。现有用例虽然通过，但连接生命周期仍需要处理。

## 4. 主要发现

### 4.1 P1：打包产物缺少最新迁移

> **复核批注：未关闭。** 修复代码已改为通过 PyInstaller 的 `--collect-submodules optibench.db.migrations` 收集全部迁移模块。重新构建后，归档中可以找到 `0ac6c641b5d7_add_data_source_and_manufacturer_indexes`，说明迁移 Python 模块已进入 sidecar。  
> 真实二进制冒烟测试仍然失败。sidecar 在空目录启动时，Alembic 无法找到解包目录中的 `optibench/db/migrations/env.py`，应用启动中止：
>
> ```text
> ImportError: Can't find Python file ...\optibench\db\migrations\env.py
> ```
>
> `--collect-submodules` 只处理可导入模块，Alembic 还需要以磁盘文件形式读取 `env.py` 和迁移脚本目录。应把整个迁移目录作为 PyInstaller data 收集，并继续保留真实 sidecar 空库启动测试。只检查归档中是否存在 revision 模块不足以关闭此项。

`engine/build_sidecar.py` 通过手工清单声明数据库迁移：

```python
"optibench.db.migrations.versions.001_init",
"optibench.db.migrations.versions.002_add_match_snapshot",
"optibench.db.migrations.versions.c53e30ed595b_add_catalog_indexes",
"optibench.db.migrations.versions.003_merge_heads",
```

清单没有包含当前 Alembic head：

```text
0ac6c641b5d7_add_data_source_and_manufacturer_indexes
```

对现有 Windows sidecar 的 PyInstaller 归档检查也确认，该迁移没有被打入产物。

可能造成的影响：

- 新安装数据库只能迁移到旧版本，缺少新增索引。
- 已经迁移到 `0ac6c641b5d7` 的数据库，在旧 sidecar 中找不到对应 revision。
- 开发环境测试通过，但安装包启动失败，问题只能在发布后暴露。

建议：

- 不再逐个维护迁移模块清单，改为收集完整的 `optibench.db.migrations` 包。
- CI 构建 sidecar 后，使用临时目录启动真实二进制。
- 验证空数据库能够升级到当前 head。
- 再用当前版本数据库启动一次，确认 revision 可识别。

### 4.2 P1：异步匹配没有真实阶段进度

> **复核批注：部分完成。** 轮询任务的候选计数已改为使用阶段输入输出数量，原先统计诊断记录条数的问题已修正。匹配器也增加了 `index_pre_filter`、`quick_hard_filter`、`domain_constraints`、`score` 和 `rank` 阶段事件。  
> SSE 仍不是实时推送。`match_progressive()` 先把回调事件存入 `stage_events`，等待 `_match_one_pass()` 完成后再依次 `yield`。模拟单轮计算耗时 0.8 秒时，首个阶段事件在 0.801 秒后才到达，用户仍会在整轮计算期间看不到更新。阶段事件需要在计算进行时直接进入流，而不是在单轮结束后回放。

`MatchingEngine.match_progressive()` 名义上提供 SSE 渐进式匹配，但当前实现先执行完整的 `_match_one_pass()`，完成后只发送一次 `completed` 消息。

前端能够建立流式连接，但用户看不到候选查询、约束过滤、评分和排序的中间状态。当前 SSE 更接近通过流返回最终结果。

轮询任务也存在计数错误：

```python
total_candidates=sum(
    1 for d in diagnostics if d.stage == "index_pre_filter"
)
```

这里统计的是诊断记录数量，不是候选组合数量，结果通常只有 0 或 1。`filtered_candidates` 也没有在各阶段稳定更新。

建议让匹配流水线返回统一的阶段结果：

```python
StageResult(
    stage="quick_filter",
    input_count=1200,
    output_count=180,
    progress=0.35,
)
```

轮询任务和 SSE 共用同一套阶段事件，避免维护两条行为不同的执行路径。

### 4.3 P1：任务线程没有并发上限

> **复核批注：部分完成。** 无上限创建 daemon 线程的问题已修正，当前使用 `ThreadPoolExecutor(max_workers=4)`，并在引擎 shutdown 时关闭执行器。  
> 取消机制仍只在 `_update()` 中检查 `cancel_event`，候选查询、组合生成、领域过滤和评分循环内部没有中断点。实测任务取消后状态立即变为 `cancelled`，工作线程仍继续运行约 0.9 秒，直到模拟中的整轮计算结束。等待队列也没有设置容量，线程并发受限，但任务仍可无限排队。  
> 关闭此项还需要在耗时阶段内部检查取消信号，并为等待队列设置容量或提交限流。

每次调用 `match_async()` 都会创建一个 daemon 线程，没有队列容量、并发限制或背压机制。快速重复点击或批量调用可能同时创建大量线程和数据库会话。

取消任务只修改状态：

```python
task.status = "cancelled"
```

正在进行的查询、组合生成和评分不会立即中止，只会在下一次 `_update()` 时发现取消状态。单个阶段耗时较长时，用户已经取消的任务仍会继续占用 CPU 和数据库连接。

建议：

- 使用固定容量的 `ThreadPoolExecutor`。
- 给任务增加取消事件，在每个阶段以及大循环中检查。
- 限制等待队列长度，超出后返回明确错误。
- 记录任务耗时、候选数量和取消点。
- 应用退出时停止接收新任务并等待或取消现有任务。

### 4.4 P1：SQLite 连接生命周期不完整

> **复核批注：未关闭。** 文件 SQLite 已改用 `NullPool`，增加 WAL 和 5 秒 busy timeout，数据库引擎也保存到 `app.state` 并在 lifespan 结束时调用 `dispose()`，这些改动方向正确。  
> 完整测试在启用资源警告后仍报告 28 条未关闭 SQLite 连接警告。测试 fixture 创建的引擎没有统一释放，连接问题仍可复现。  
> 服务生命周期还存在二次启动回归：shutdown 后 `_engine` 被重置，但 `_session_maker` 保留。相同进程中的第二次 lifespan 因 `_session_maker is not None` 直接跳过初始化，`/api/v1/domains` 返回 503。应在 shutdown 时同步重置 `_session_maker` 和相关 `app.state`，并增加同进程重复启动测试。

服务初始化对所有 SQLite 场景使用 `StaticPool`：

```python
db_engine = create_engine(
    db_url,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
```

`StaticPool` 更适合测试中的内存 SQLite。文件数据库长期复用同一连接，会放大线程竞争和事务状态问题。lifespan 结束时只重置 `_engine`，没有调用数据库引擎的 `dispose()`。

覆盖率测试中出现多次未关闭 SQLite 连接警告，与这一生命周期设计一致。

建议：

- 内存数据库使用 `StaticPool`。
- 文件 SQLite 使用默认池或 `NullPool`，按桌面单机负载选择。
- 将数据库引擎保存在 `app.state.db_engine`。
- lifespan 退出时调用 `db_engine.dispose()`。
- 测试 fixture 在结束后显式释放引擎。
- 桌面数据库启用 WAL，并设置合理的 busy timeout。

### 4.5 P2：领域插件接口没有覆盖候选查询

设计文档要求 `MatchingEngine` 不包含领域知识，新增领域只需实现 `DomainModule`。实际代码中，`index_pre_filter()` 直接判断四个领域，并包含焦距范围、传感器格式、卡口、波段和显微镜类型等领域规则。

结果是新增领域仍需修改匹配器，且严格模式、宽松模式和排序逻辑散落在引擎内部。

建议逐步把以下职责移入领域模块：

- 构建目录查询条件。
- 估算目标焦距或放大倍率。
- 定义宽松匹配策略。
- 对候选集合进行领域预排序。
- 提供领域诊断建议。

匹配器只保留流程编排：

```text
候选查询 -> 通用约束 -> 领域约束 -> 派生计算 -> 评分 -> 排序
```

这项重构应分阶段完成，不建议一次改写整个匹配器。

### 4.6 P2：API 服务承担过多职责

`server.py` 同时处理：

- 应用生命周期和认证。
- 领域元数据。
- 光学计算。
- 异步和流式匹配。
- 知识库。
- 三类可视化。
- 项目和方案管理。
- PDF、Excel、CSV 导出。
- 命令行启动。

目录 API 已经拆成独立 router，其他功能仍集中在单文件中。建议按业务边界继续拆分：

```text
api/
  app.py
  dependencies.py
  matching_router.py
  knowledge_router.py
  visualization_router.py
  project_router.py
  export_router.py
```

数据库会话、匹配引擎和认证逻辑通过依赖注入统一提供。这样可以减少模块全局变量和测试中的手工替换。

### 4.7 P2：前端领域页面重复较多

四个领域页面都包含相似的状态和流程：

- 加载目录。
- 构建匹配请求。
- 启动任务。
- 选择结果。
- 加载 MTF、覆盖或 CoC 数据。
- Pareto 过滤。
- 对比模式。
- 项目保存和导出。

仓库已经有 `DomainPageShell`、`DomainFormPanel`、`DomainResultsPanel` 和全局匹配 store，但领域页面仍保留大量重复编排代码。

建议抽取领域页面控制 hook：

```typescript
useDomainWorkspace({
  domain,
  buildRequirements,
  visualizationKinds,
})
```

页面只负责领域表单、字段格式和特有可视化。抽取时应保留领域差异，不应为了复用建立过度通用的动态页面系统。

### 4.8 P2：存在未使用的第二套匹配路径

`apps/desktop/src/hooks/useLensMatching.ts` 在前端获取镜头和探测器目录，并在浏览器中执行笛卡尔积和评分。当前仓库没有页面引用该 hook。

它与后端匹配器构成两套潜在规则来源。即使目前未使用，后续开发者也可能误用并产生评分差异。

建议删除该 hook，或明确标记为独立的离线实验代码并补充测试。按当前产品结构，删除更符合 KISS 和 YAGNI。

### 4.9 P2：导入接口没有资源限制

目录导入通过 `await file.read()` 一次性读取完整文件。Excel 解析又把所有单元格复制到 Python 列表后再处理。

桌面应用通常只接受本地可信文件，但损坏文件或大文件仍可能造成长时间占用和内存增长。

建议增加：

- 上传大小限制。
- 最大行数和列数。
- 允许的文件扩展名和 MIME 类型检查。
- Excel 只读模式。
- 分批校验和插入。
- 单次导入事务与失败回滚。
- 导入预览和错误行下载。

### 4.10 P2：API 错误信息没有传递给前端

前端通用请求方法只使用 HTTP 状态：

```typescript
throw new Error(`API error: ${res.status} ${res.statusText}`);
```

后端返回的 `detail` 没有被解析。重复型号、参数不合法和数据缺失等错误在界面上会变成笼统的 Bad Request 或 Unprocessable Entity。

建议建立统一的 `ApiError`：

```typescript
class ApiError extends Error {
  status: number;
  detail: string;
}
```

所有 JSON、文件上传和 Blob 下载请求应共用同一错误解析逻辑。

### 4.11 P2：桌面安全配置仍是开发态

Tauri 配置中 CSP 为 `null`，同时启用了 shell 插件执行权限。当前 capability 将执行范围限制为 `optibench-engine` sidecar，这是合理的，但生产版本仍应设置 CSP。

建议：

- 限制脚本、样式、图片和网络连接来源。
- `connect-src` 只允许本地引擎地址和明确需要的图片域名。
- 检查远程镜头图片是否需要经过缓存代理。
- 发布前执行一次 Tauri 权限审计。

### 4.12 P2：CI 没有覆盖桌面发布链

当前 CI 覆盖 Python 3.12/3.13、Ruff、TypeScript 和 Vite 构建，但没有检查：

- Rust `cargo check`。
- Alembic 空库迁移。
- 模型和迁移一致性。
- PyInstaller sidecar 构建。
- sidecar 启动与健康检查。
- Tauri 安装包构建。
- Windows、macOS、Linux 平台差异。

桌面应用最容易出错的部分正是源码检查之后的打包环节。建议增加分层 CI：

| 层次 | 检查 |
|---|---|
| 每次提交 | Python 测试、Ruff、TypeScript、Vite、Rust |
| 主分支 | Alembic、sidecar 构建、sidecar 冒烟测试 |
| 发布标签 | 三平台 Tauri 构建、安装包签名和产物上传 |

### 4.13 P2：版本号不一致

审查时发现：

| 位置 | 版本 |
|---|---|
| `CHANGELOG.md` | 1.1.0 |
| `engine/pyproject.toml` | 0.1.0 |
| `apps/desktop/package.json` | 0.1.0 |
| `tauri.conf.json` | 0.1.0 |
| API health 和 FastAPI metadata | 1.0.0 |

版本不一致会影响安装包升级、问题定位和报告追踪。建议保留一个版本源，通过脚本同步 Python、npm、Tauri 和 API 版本。

### 4.14 P3：设计文档与实现边界不清

架构文档描述了 TaskQueue、AuditLogger、CompatibilityCache、PluginReg、NSGA-II 和 WebSocket 等能力。当前实现中：

- 任务系统是进程内字典和临时线程。
- `CompatibilityCache` 只有数据库模型，没有读写路径。
- `diskcache` 已声明依赖，但没有实际使用。
- Pareto 前沿在前端计算，没有 NSGA-II。
- 领域注册仍是服务启动时手工注册。
- 通信方式以 HTTP、轮询和 SSE 为主，没有 WebSocket。

建议把文档拆成两部分：

- 当前架构：只写已经存在并经过验证的实现。
- 演进设计：标明候选方案、触发条件和暂不实施的原因。

这样可以避免开发计划被误读为已交付能力。

### 4.15 P3：数据质量字段没有进入匹配决策

模型包含 `verified`、`data_quality_score` 和 `data_source`，但当前匹配排序基本不考虑数据可信度。用户导入数据默认质量分为 1.0，却同时标记为未验证，两者含义冲突。

建议定义明确的数据质量模型：

| 维度 | 示例 |
|---|---|
| 来源 | 厂商数据表、代理商页面、用户录入、推算 |
| 完整度 | 必填参数和可选参数的覆盖率 |
| 新鲜度 | 最近确认日期 |
| 验证状态 | 未验证、人工核验、厂商确认 |
| 推算字段 | 原始值、推算值、默认值 |

匹配结果和报告应展示数据来源与缺失字段，避免用户把默认值或估算值理解为厂商规格。

## 5. 工程原则评估

### 5.1 KISS

做得较好的部分：

- 本地 FastAPI sidecar 便于复用 Python 光学计算生态。
- SQLite 适合当前单机数据规模。
- 目录查询和领域模块接口总体直观。

需要改进的部分：

- 同时维护轮询和伪渐进 SSE 两条路径。
- 迁移靠手工隐式导入清单。
- 大型页面和匹配器集中处理过多分支。

### 5.2 YAGNI

数据库中预留的兼容性缓存、文档中的 NSGA-II、插件注册和审计系统尚未形成真实使用场景。应先处理发布可靠性和算法验证，再决定是否实现这些能力。

未使用的 `useLensMatching.ts` 和 `diskcache` 依赖可以清理。

### 5.3 DRY

前端四个领域页面在匹配、结果选择、可视化加载和对比流程上存在重复。后端同步匹配、异步匹配和流式匹配也重复编排严格与宽松两轮执行。

建议共享流程对象和阶段事件，不要仅抽取零散工具函数。

### 5.4 SOLID

- 单一职责：`server.py`、`engine.py` 和领域页面职责过多。
- 开闭原则：新增领域仍需修改 `index_pre_filter()`。
- 接口隔离：`DomainModule` 没有覆盖候选查询和宽松策略，接口能力不足。
- 依赖倒置：部分目录 API 已使用 `app.state`，其他 API 仍直接依赖模块全局变量。

## 6. 改进计划

### 6.1 P0：发布阻断项

建议在下一个可发布版本前完成：

1. 修复 sidecar 迁移打包，验证空库和已有数据库升级。
2. 增加 sidecar 冒烟测试，覆盖 health、目录查询、匹配和导出。
3. 统一所有版本号。
4. 处理 SQLite 引擎释放和测试连接警告。
5. 在 CI 中加入 `cargo check` 和 Alembic 检查。

验收标准：

- 从全新目录启动桌面包，数据库自动迁移到当前 head。
- 关闭应用后没有残留 sidecar 进程。
- 连续启动和退出 20 次，不出现数据库锁和迁移错误。
- 安装包内版本、API 版本和报告版本一致。

### 6.2 P1：稳定性治理

建议用一个迭代完成：

1. 用固定线程池替换每任务创建线程。
2. 建立统一阶段事件，修正任务进度和候选计数。
3. 实现可检查的取消事件。
4. 限制目录导入大小和行数。
5. 统一前端 API 错误处理。
6. 给导出、知识约束和覆盖图补测试。

验收标准：

- 并发提交超过容量时有明确反馈。
- 任务取消后能在当前阶段内及时停止。
- SSE 至少推送候选查询、过滤、评分、排序和完成事件。
- 覆盖率达到 80% 左右，关键算法和导出路径不低于 70%。

### 6.3 P2：架构收敛

建议分两到三个小迭代处理：

1. 拆分 API router 和依赖模块。
2. 把领域候选查询和宽松策略移入 `DomainModule`。
3. 抽取前端领域页面控制 hook。
4. 删除未使用的匹配 hook 和依赖。
5. 将文档区分为当前实现与演进设计。

重构期间应保持 API 响应格式不变，并用黄金测试锁定四个领域的结果。

### 6.4 P3：产品可信度

工程稳定后，建议优先建设以下能力：

1. 为每个领域建立 20 至 50 个经过人工确认的选型样例。
2. 给所有计算字段标明单位、来源和推算方式。
3. 报告中展示算法版本、目录版本、数据质量和假设。
4. 增加灵敏度分析，说明参数变化对排名的影响。
5. 将硬性不可用条件和偏好评分明确分开。
6. 建立回归阈值，算法变更不能无提示地大幅改变历史结果。

## 7. 未来发展方向

### 7.1 近期：做深工业视觉

工业视觉的参数结构、数据来源和用户工作流最适合形成完整闭环。建议优先完善：

- 目标精度、视场、工作距离到镜头和相机的完整推导。
- 远心镜头、线扫和面阵的差异化约束。
- 景深、曝光、运动模糊和接口带宽估算。
- 厂商目录导入模板和数据核验。
- 可交付的选型报告和物料清单。

先在一个领域形成可验证的工程价值，再把成熟模型推广到其他领域。

### 7.2 中期：从推荐结果转向决策解释

目前产品已经能展示推导链、诊断和 Pareto 前沿，可以继续发展为决策辅助工具：

- 展示每个候选被淘汰的具体原因。
- 允许用户调整权重并观察排名变化。
- 给出参数容差和风险区间。
- 对缺失规格给出明确提示，不静默使用默认值。
- 比较方案时展示成本、性能和数据可信度的权衡。

### 7.3 中期：建立器件数据治理

器件库会逐渐成为比算法更难维护的资产。需要考虑：

- 厂商和型号的稳定标识。
- 数据来源、抓取日期和规格表版本。
- 同型号不同地区或版本的差异。
- 参数单位和字段映射。
- 失效型号、替代型号和生命周期。
- 用户数据与官方数据的合并策略。

建议先建立可追踪的数据模型，再考虑自动抓取厂商目录。

### 7.4 长期：团队协作和云端目录

云端能力适合在单机版稳定、数据模型成熟后推进：

- 团队共享器件库和项目。
- 企业自定义约束与评分模板。
- 历史方案审计和审批。
- 云端目录更新与本地缓存。
- 供应链价格和可用性信息。

桌面计算引擎仍可保留离线模式，云端负责协作、数据分发和授权。

### 7.5 暂不建议投入

现阶段不建议优先投入：

- 用 Rust 重写整个光学引擎。
- 通用第三方插件市场。
- NSGA-II 等更复杂优化算法。
- 分布式任务系统。
- 微服务拆分。
- 大规模实时 WebSocket 架构。

当前数据规模和单机使用方式不需要这些复杂度。

## 8. 建议的目标架构

在不改变 Python 引擎和 Tauri 主体方案的前提下，可以逐步调整为：

```text
Desktop UI
  |
  | HTTP / SSE
  v
FastAPI Application
  |- Matching Router
  |- Catalog Router
  |- Project Router
  |- Knowledge Router
  |- Export Router
  |
  v
Application Services
  |- Matching Service
  |- Catalog Service
  |- Project Service
  |- Export Service
  |
  v
Matching Pipeline
  |- Domain Candidate Provider
  |- Common Constraints
  |- Domain Constraints
  |- Derived Calculations
  |- Scoring
  |- Ranking
  |
  v
SQLite + Alembic
```

这一路线保留现有技术栈，只调整职责边界，迁移风险相对可控。

## 9. 风险清单

| 编号 | 风险 | 等级 | 当前状态 | 建议处理时间 |
|---|---|---|---|---|
| R1 | sidecar 缺少最新 Alembic migration | P1 | 修复未完成：revision 已入归档，真实 sidecar 因缺少 `env.py` 启动失败 | 发布前 |
| R2 | 异步任务线程无上限 | P1 | 部分关闭：固定 4 个工作线程，等待队列仍无上限 | 下一迭代 |
| R3 | 取消无法及时终止计算 | P1 | 未关闭：状态可取消，工作线程仍执行至当前整轮结束 | 下一迭代 |
| R4 | 任务候选计数错误 | P1 | 已关闭：改用阶段输入输出数量 | 已完成 |
| R5 | SSE 没有阶段事件 | P1 | 部分关闭：已有阶段事件，但整轮结束后才集中发送 | 下一迭代 |
| R6 | SQLite 连接未完整释放 | P1 | 未关闭：仍有 28 条资源警告，二次 lifespan 返回 503 | 发布前 |
| R7 | 关键导出和知识模块覆盖率不足 | P2 | 已确认 | 两个迭代内 |
| R8 | API 和匹配器文件过大 | P2 | 已确认 | 分阶段处理 |
| R9 | 导入文件没有大小限制 | P2 | 已确认 | 下一迭代 |
| R10 | 前端丢失后端错误详情 | P2 | 已确认 | 下一迭代 |
| R11 | CSP 未配置 | P2 | 已确认 | 发布前 |
| R12 | 版本号不一致 | P2 | 已确认 | 发布前 |
| R13 | 文档描述未实现能力 | P3 | 已确认 | 文档更新时 |
| R14 | 数据质量没有进入结果解释 | P3 | 已确认 | 产品深化阶段 |

## 10. 审查结语

OptiBench 当前最大的优势是产品链路已经连通：用户能够输入需求、运行匹配、理解结果、对比候选、保存方案并导出报告。下一阶段不需要继续扩大功能面，应把已经存在的链路做稳，并证明结果可信。

建议以打包产物可重复、数据库可升级、任务可控、结果可回归作为下一个版本的完成标准。完成这些工作后，项目才适合进入更广泛的试用和真实工程场景验证。
