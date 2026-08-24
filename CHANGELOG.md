# Changelog

## [Unreleased]

### Changed
- **项目改名**：LensFit → OptiBench（光学工程工作台）
  - Python 包 `lensfit` → `optibench`，PyPI 包名 `lensfit-engine` → `optibench-engine`
  - 数据库文件 `lensfit.db` → `optibench.db`（启动时自动迁移旧库文件）
  - Tauri 标识符 `com.lensfit.app` → `com.optibench.app`，sidecar 二进制 `lensfit-engine` → `optibench-engine`
  - API key 环境变量 `LENSFIT_API_KEY` → `OPTIBENCH_API_KEY`
  - 前端 localStorage 键迁移（主题、学习进度、Lab 草稿自动保留）
- **运行方式全平台统一**：开发启动与桌面构建统一为 `uv run scripts/dev.py` / `uv run scripts/build-desktop.py`，删除 `dev.sh`/`dev.bat`/`build-desktop.sh`/`build-desktop.bat` 平台包装脚本
  - `dev.py` 自动识别并重建其他操作系统创建的 `.venv`（仓库根目录）与 `node_modules`

## [1.1.0] - 2026-06-02

### Added
- **红外成像选型模块**：完整支持 SWIR / MWIR / LWIR 波段的红外镜头与探测器匹配
  - 13 款红外镜头（Lightpath、Ophir、Umicore 等品牌，含变焦与定焦）
  - 13 款红外探测器（FLIR、iRay、HikMicro、Guide、ULIS、SCD 等品牌，制冷/非制冷）
  - 8 家红外制造商数据
  - 关键指标：IFOV、空间分辨率、波段重叠率、NETD 评分
- **显微镜选型模块**：支持复式显微镜与体视显微镜双模式
  - 26 款复式物镜（Olympus、Nikon、Zeiss、Leica、Mitutoyo）
  - 14 款体视变焦主体
  - 奈奎斯特采样比分析、瑞利分辨率计算
- **摄影选型模块**：25 支摄影镜头 + 8 款相机机身
  - 支持画幅、焦距、光圈、用途、品牌、卡口多维度筛选
  - 真机产品图（Wikimedia Commons）
- **红外领域后端模块**：`InfraredModule` 插件化领域匹配引擎
- **显微镜领域后端模块**：`MicroscopyModule` 支持 compound/stereo 双模式
- **探测器目录 API 扩展**：支持 `category` 过滤，返回 NETD、光谱范围等字段
- **镜头目录 API 扩展**：返回波长范围、变焦范围等红外相关字段

### Fixed
- **暗色模式**：系统性修复所有组件和页面的暗色模式支持
  - Card、Input、Button、Badge、Skeleton 组件添加 `dark:` 变体
  - 工业视觉、摄影、显微镜、红外四大页面全面适配
- **导航栏**：移除显微镜和红外模块的「新功能」标记

## [1.0.0] - 2025-05-28

### Added
- **工业视觉选型模块**：完整的 FA 镜头、远心镜头、线扫镜头、变焦镜头选型工作流
- **四级匹配流水线**：IndexPreFilter → QuickHardFilter → DomainHardFilter → FullScoring → Ranking
- **TOPSIS 多目标排序**：支持覆盖裕量、奈奎斯特匹配、接口兼容性、成本效益等多维度评分
- **传感器覆盖可视化**：Canvas 实时绘制传感器矩形、像圆、渐晕区域
- **异步任务系统**：前端轮询进度条，支持任务取消
- **项目与方案管理**：支持创建项目、保存选型方案（含快照防漂移）
- **PDF/Excel 导出**：一键导出 Top-N 匹配结果报告
- **种子数据库**：10 家厂商、56 款镜头、31 款探测器
- **PyInstaller Sidecar**：Python 引擎打包为 36MB 单文件二进制，供 Tauri 调用
- **Tauri v2 桌面壳**：Rust 实现的 Sidecar Supervisor，随机端口分配、健康检查、崩溃重启
- **完整 API**：health、calculate、match/async、visualize/coverage、catalog、projects、setups、export

### Fixed
- 修复 `data_source` 字段缺失导致的种子数据导入失败
- 修复 `depth_of_field` 模块级 `@staticmethod` 语法错误
- 修复 `match_async` SQLAlchemy Session 线程安全问题
- 修复 Tauri v2 `Command::new_sidecar` API 兼容性
- 修复前端 API base URL 硬编码问题，支持动态端点发现
- 修复 `CatalogQuery` 大小写敏感匹配问题
- 修复工业领域约束对 `None` 字段的兼容性
- 修复奈奎斯特采样在 MTF 数据缺失时的异常
- 修复 `datetime.utcnow()` 弃用警告

### Technical
- SQLAlchemy 2.0 + Alembic 迁移
- FastAPI + Uvicorn 异步服务
- React 19 + TypeScript + Tailwind CSS
- NumPy + SciPy 数值计算
- ReportLab + OpenPyXL 报告生成
