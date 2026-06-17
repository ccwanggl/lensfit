# 数据库建设方案

## 1. 设计原则

1. **可扩展性**：新器件类型、新参数字段通过配置添加，不改表结构
2. **标准化**：物理单位统一（mm, μm, nm, °C），避免"英寸/毫米"混用
3. **版本化**：器件参数支持多版本（厂商更新规格书后可追溯）
4. **多语言**：型号名、厂商名为原文，描述字段支持 i18n
5. **关系完整性**：镜头-探测器-适配器的兼容关系通过约束表表达，不硬编码

---

## 2. 核心实体关系图 (ERD)

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   Manufacturer  │       │  LensCatalog    │       │ DetectorCatalog │
│   厂商表         │◄──────│  镜头目录       │       │  探测器目录      │
│                 │       │                 │       │                 │
│ - id (PK)       │       │ - id (PK)       │       │ - id (PK)       │
│ - name          │       │ - manufacturer_id│      │ - manufacturer_id│
│ - country       │       │ - model         │       │ - model         │
│ - website       │       │ - category      │       │ - category      │
│ - is_verified   │       │ - mount_type    │       │ - sensor_format │
└─────────────────┘       │ - focal_length  │       │ - resolution_w  │
                          │ - max_aperture  │       │ - resolution_h  │
                          │ - image_circle  │       │ - pixel_size_um │
                          │ - min_wd        │       │ - sensor_w_mm   │
                          │ - max_wd        │       │ - sensor_h_mm   │
                          │ - price_usd     │       │ - mount_type    │
                          └────────┬────────┘       │ - price_usd     │
                                   │                └────────┬────────┘
                                   │                         │
                    ┌──────────────┴──────────────┐          │
                    │    LensSpectralResponse     │          │
                    │    镜头光谱响应              │          │
                    │  (λ, transmission%)         │          │
                    └─────────────────────────────┘          │
                                                             │
                    ┌───────────────────────────────────────┴─────────────┐
                    │              CompatibilityMatrix                       │
                    │              兼容性矩阵                                 │
                    │  - lens_id  →  detector_id  →  adapter_id            │
                    │  - compatibility_score                                │
                    │  - needs_adapter                                      │
                    │  - verified_by_test                                   │
                    └───────────────────────────────────────────────────────┘
```

---

## 3. 详细表结构设计

### 3.1 厂商表 (manufacturers)

```sql
CREATE TABLE manufacturers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,              -- 厂商名称 (如 "Edmund Optics")
    name_en         TEXT,                       -- 英文名称
    name_cn         TEXT,                       -- 中文名称
    country         TEXT,                       -- 国家代码 (ISO 3166-1 alpha-2)
    website         TEXT,
    logo_url        TEXT,
    is_verified     BOOLEAN DEFAULT 0,          -- 是否已验证的正规厂商
    data_source     TEXT,                       -- 数据来源: manual/crawler/api/user
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_mfr_name ON manufacturers(name);
CREATE INDEX idx_mfr_verified ON manufacturers(is_verified);
```

### 3.2 镜头目录表 (lens_catalog)

支持工业镜头、显微镜物镜、红外镜头等所有镜头类型。

```sql
CREATE TABLE lens_catalog (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id     INTEGER NOT NULL REFERENCES manufacturers(id),
    
    -- 基础标识
    model               TEXT NOT NULL,          -- 型号 (如 "MVL-HF0828M-6MPE")
    sku                 TEXT,                   -- SKU/订货号
    category            TEXT NOT NULL,          -- 镜头类型:
                                                -- 'fa' | 'telecentric' | 'macro' | 
                                                -- 'microscope_objective' | 'eyepiece' |
                                                -- 'c_mount_adapter' | 'ir_lens' | 
                                                -- 'swir_lens' | 'linescan_lens' | 'zoom'
    status              TEXT DEFAULT 'active',  -- 'active' | 'discontinued' | 'preview'
    
    -- 光学参数
    focal_length_mm     REAL,                   -- 焦距 (mm)，∞表示无穷远
    focal_length_min    REAL,                   -- 变焦镜头最小焦距
    focal_length_max    REAL,                   -- 变焦镜头最大焦距
    max_aperture        REAL,                   -- 最大光圈 F数 (如 1.4, 2.8)
    min_aperture        REAL,                   -- 最小光圈 F数
    image_circle_mm     REAL,                   -- 像圆直径 (mm)，决定最大兼容传感器
    
    -- 工作距离参数
    min_working_distance_mm REAL,               -- 最小工作距离
    max_working_distance_mm REAL,               -- 最大工作距离 (NULL表示∞)
    nominal_wd_mm       REAL,                   -- 标称工作距离（远心镜头等固定WD）
    
    -- 机械参数
    mount_type          TEXT,                   -- 'C' | 'CS' | 'F' | 'M42' | 'M58' | 
                                                -- 'M72' | 'M95' | 'RMS' | 'M25' | 'M27' |
                                                -- ' proprietary_X' | 'eyepiece_23.2mm' | ...
    mount_flange_mm     REAL,                   -- 法兰距 (mm)
    filter_thread_mm    REAL,                   -- 滤镜螺纹尺寸
    outer_diameter_mm   REAL,                   -- 外径
    length_mm           REAL,                   -- 镜头长度
    weight_g            REAL,                   -- 重量 (g)
    
    -- 性能参数
    mtf50_lpmm          REAL,                   -- MTF50 (线对/mm)
    distortion_percent  REAL,                   -- 最大畸变 (%)
    telecentricity_deg  REAL,                   -- 远心度 (°)，远心镜头专用
    na                  REAL,                   -- 数值孔径，显微镜物镜专用
    working_f_number    REAL,                   -- 工作F数 (微距/近摄时)
    
    -- 光谱参数
    wavelength_min_nm   INTEGER,                -- 最小透过波长 (nm)
    wavelength_max_nm   INTEGER,                -- 最大透过波长 (nm)
    coating_type        TEXT,                   -- 镀膜类型
    
    -- 商业参数
    price_usd           REAL,                   -- 参考价格 (USD)
    price_currency      TEXT DEFAULT 'USD',
    price_date          DATE,                   -- 价格更新时间
    datasheet_url       TEXT,                   -- 规格书链接
    product_url         TEXT,                   -- 产品页面
    
    -- 元数据
    data_source         TEXT,                   -- manual / crawler / api / user_contrib
    data_quality_score  REAL DEFAULT 0,         -- 数据完整度评分 (0-1)
    verified            BOOLEAN DEFAULT 0,      -- 是否人工核验
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(manufacturer_id, model)
);

-- 核心查询索引
CREATE INDEX idx_lens_category ON lens_catalog(category);
CREATE INDEX idx_lens_focal ON lens_catalog(focal_length_mm);
CREATE INDEX idx_lens_mount ON lens_catalog(mount_type);
CREATE INDEX idx_lens_image_circle ON lens_catalog(image_circle_mm);
CREATE INDEX idx_lens_wavelength ON lens_catalog(wavelength_min_nm, wavelength_max_nm);
CREATE INDEX idx_lens_price ON lens_catalog(price_usd);
CREATE INDEX idx_lens_wd ON lens_catalog(min_working_distance_mm, max_working_distance_mm);
CREATE INDEX idx_lens_composite ON lens_catalog(category, mount_type, focal_length_mm);
```

### 3.3 探测器目录表 (detector_catalog)

覆盖CCD/CMOS相机、红外探测器、科学级探测器等。

```sql
CREATE TABLE detector_catalog (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id     INTEGER NOT NULL REFERENCES manufacturers(id),
    
    -- 基础标识
    model               TEXT NOT NULL,          -- 型号 (如 "MER2-2000-19U3M-L")
    category            TEXT NOT NULL,          -- 'area_scan_cmos' | 'area_scan_ccd' |
                                                -- 'linescan_cmos' | 'linescan_ccd' |
                                                -- 'lwir_microbolometer' | 'swir_ingaas' |
                                                -- 'mwir_mct' | 'emccd' | 'iccd' | 'sCMOS'
    
    -- 传感器物理参数
    sensor_format_inch  TEXT,                   -- 名义尺寸: '1/4' | '1/3' | '1/2' | '2/3' | '1' | 'APS-C' | 'Full Frame' | NULL
    sensor_w_mm         REAL,                   -- 传感器水平尺寸 (mm)
    sensor_h_mm         REAL,                   -- 传感器垂直尺寸 (mm)
    sensor_diag_mm      REAL,                   -- 传感器对角线 (mm)
    
    -- 分辨率参数
    resolution_w        INTEGER,                -- 水平像素
    resolution_h        INTEGER,                -- 垂直像素
    pixel_size_um       REAL,                   -- 像元尺寸 (μm)
    pixel_pitch_um      REAL,                   -- 像元中心距 (μm)
    
    -- 性能参数 (EMVA 1288 标准)
    quantum_efficiency_peak REAL,               -- 峰值QE (%)
    quantum_efficiency_530nm REAL,              -- 530nm处QE (%)
    read_noise_e        REAL,                   -- 读出噪声 (e-)
    dark_current_e_s    REAL,                   -- 暗电流 (e-/s)
    full_well_e         REAL,                   -- 满阱容量 (e-)
    dynamic_range_db    REAL,                   -- 动态范围 (dB)
    snr_max_db          REAL,                   -- 最大信噪比 (dB)
    
    -- 红外探测器专用参数
    netd_mk             REAL,                   -- NETD (mK)
    spectral_range_min_um REAL,                 -- 光谱范围最小值 (μm)
    spectral_range_max_um REAL,                 -- 光谱范围最大值 (μm)
    pixel_pitch_um_ir   REAL,                   -- 红外像元中心距 (μm，可能不同于光学)
    
    -- 接口与数据
    mount_type          TEXT,                   -- 'C' | 'CS' | 'F' | 'M42' | 'proprietary'
    data_interface      TEXT,                   -- 'USB3.0' | 'GigE' | 'CameraLink' | 'CoaXPress'
    max_fps_full        REAL,                   -- 全分辨率最大帧率
    
    -- 商业参数
    price_usd           REAL,
    datasheet_url       TEXT,
    
    -- 元数据
    data_source         TEXT,
    data_quality_score  REAL DEFAULT 0,
    verified            BOOLEAN DEFAULT 0,
    
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(manufacturer_id, model)
);

-- 索引
CREATE INDEX idx_det_category ON detector_catalog(category);
CREATE INDEX idx_det_sensor_size ON detector_catalog(sensor_diag_mm);
CREATE INDEX idx_det_pixel_size ON detector_catalog(pixel_size_um);
CREATE INDEX idx_det_mount ON detector_catalog(mount_type);
CREATE INDEX idx_det_spectral ON detector_catalog(spectral_range_min_um, spectral_range_max_um);
CREATE INDEX idx_det_composite ON detector_catalog(category, mount_type, sensor_diag_mm);
```

### 3.4 适配器/转接环表 (adapter_catalog) — **尚未实现**

> 当前代码中没有 `AdapterCatalog` 模型，也没有对应的 Alembic 迁移。以下设计保留为参考。


```sql
CREATE TABLE adapter_catalog (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    manufacturer_id     INTEGER NOT NULL REFERENCES manufacturers(id),
    
    model               TEXT NOT NULL,
    category            TEXT NOT NULL,          -- 'reducer' | 'extender' | 'mount_adapter' | 'tube_lens'
    
    -- 机械接口
    mount_from          TEXT NOT NULL,          -- 输入端接口
    mount_to            TEXT NOT NULL,          -- 输出端接口
    
    -- 光学参数
    magnification       REAL DEFAULT 1.0,       -- 放大/缩小倍率
    flange_distance_mm  REAL,                   -- 法兰距贡献 (mm)
    image_circle_mm     REAL,                   -- 支持的像圆直径
    
    -- 专用参数
    tube_length_mm      REAL,                   -- 镜筒长度（tube lens）
    extension_mm        REAL,                   -- 延长长度（extension tube）
    
    price_usd           REAL,
    
    UNIQUE(manufacturer_id, model)
);
```

### 3.5 光谱响应曲线表 (spectral_responses) — **尚未实现**

> 当前数据库中不存在该表，光谱匹配逻辑暂未依赖离散光谱数据。以下设计保留为参考。


存储镜头透过率、探测器QE、光源光谱等离散光谱数据。

```sql
CREATE TABLE spectral_responses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL,              -- 'lens' | 'detector' | 'filter' | 'source'
    entity_id       INTEGER NOT NULL,           -- 对应表的外键
    entity_model    TEXT,                       -- 冗余存储，方便查询
    
    wavelength_nm   INTEGER NOT NULL,           -- 波长 (nm)
    value_percent   REAL NOT NULL,              -- 透过率/QE/强度 (%)
    
    UNIQUE(entity_type, entity_id, wavelength_nm)
);

-- 按实体查询光谱
CREATE INDEX idx_spectral_entity ON spectral_responses(entity_type, entity_id);
CREATE INDEX idx_spectral_wl ON spectral_responses(wavelength_nm);
```

### 3.6 兼容性缓存表 (compatibility_cache)

> **当前状态**：表和索引已创建，但**没有任何运行时代码读写该表**。匹配引擎尚未接入缓存。

**按需计算 + 结果缓存**，替代预计算的 compatibility_matrix 大表。避免 5000镜头 × 2000探测器 = 10M 行预计算。

```sql
CREATE TABLE compatibility_cache (
    cache_key           TEXT PRIMARY KEY,       -- hash(lens_id + detector_id + adapter_id + algorithm_version)
    
    -- 关联器件
    lens_id             INTEGER NOT NULL,
    detector_id         INTEGER NOT NULL,
    adapter_id          INTEGER,
    
    -- 计算结果（JSON 存储完整评分向量）
    result_json         TEXT NOT NULL,
    
    -- 关键指标（冗余存储，便于直接查询）
    is_compatible       BOOLEAN DEFAULT 1,
    compatibility_score REAL,
    coverage_ratio      REAL,
    nyquist_ratio       REAL,
    vignetting_risk     BOOLEAN,
    
    -- 缓存元数据
    algorithm_version   TEXT NOT NULL,          -- 算法版本号（算法更新后缓存失效）
    computed_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_count        INTEGER DEFAULT 1,      -- 访问次数（LRU淘汰依据）
    last_accessed       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 核心查询索引
CREATE INDEX idx_compat_cache_lookup ON compatibility_cache(lens_id, detector_id, adapter_id);
CREATE INDEX idx_compat_cache_lru ON compatibility_cache(last_accessed);
CREATE INDEX idx_compat_cache_score ON compatibility_cache(compatibility_score);

-- LRU 清理：删除 90 天未访问的冷缓存
-- 定期执行: DELETE FROM compatibility_cache WHERE last_accessed < datetime('now', '-90 days');
```

**运行时逻辑**：
1. 查询时先查缓存：`SELECT result_json FROM compatibility_cache WHERE cache_key = ?`
2. 命中：返回结果，更新 `access_count` 和 `last_accessed`
3. 未命中：实时计算 → 写入缓存 → 返回结果
4. 算法版本变更时，清除旧版本缓存：`DELETE FROM compatibility_cache WHERE algorithm_version != ?`

### 3.7 用户项目表 (user_projects)

```sql
CREATE TABLE user_projects (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    description     TEXT,
    domain          TEXT,                       -- 'industrial' | 'microscope' | 'infrared'
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE project_setups (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id      INTEGER NOT NULL REFERENCES user_projects(id),
    name            TEXT NOT NULL,
    
    -- 模式 A：引用目录（跟踪最新数据）
    lens_id         INTEGER REFERENCES lens_catalog(id),
    detector_id     INTEGER REFERENCES detector_catalog(id),
    adapter_id      INTEGER REFERENCES adapter_catalog(id),
    
    -- 模式 B：快照（保存时的完整参数，防止数据漂移）
    lens_snapshot       TEXT,                   -- JSON: 保存时刻的镜头完整参数
    detector_snapshot   TEXT,                   -- JSON: 保存时刻的探测器完整参数
    adapter_snapshot    TEXT,                   -- JSON: 保存时刻的适配器参数
    
    -- 一致性标记
    snapshot_version    INTEGER,                -- 主库数据版本号
    snapshot_date       TIMESTAMP,              -- 快照时间
    drift_detected      BOOLEAN DEFAULT 0,      -- 是否检测到参数漂移
    drift_details       TEXT,                   -- 漂移详情（哪些字段变了）
    
    -- 自定义参数（当不使用目录器件时，与引用互斥）
    custom_lens_params      TEXT,               -- JSON
    custom_detector_params  TEXT,               -- JSON
    
    -- 计算结果缓存
    calculated_params       TEXT,               -- JSON: FOV, WD, magnification等
    
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.8 公式注册表 (formula_registry) — **尚未实现**

> 当前公式以内建 Python 函数为主（`core/thin_lens.py`、`matching/scoring.py` 等），
> L1/L2/L3 分级表达式系统尚未落地。以下设计保留为参考。


分级公式系统：L0（内建代码）→ L1（安全表达式）→ L2（受限DSL）→ L3（沙箱脚本）。避免全量 `eval()` 的安全风险。

```sql
CREATE TABLE formula_registry (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    formula_id      TEXT NOT NULL UNIQUE,       -- 唯一标识符
    name            TEXT NOT NULL,
    category        TEXT,                       -- 'geometry' | 'physical' | 'mechanical'
    
    -- 公式分级
    level           TEXT NOT NULL DEFAULT 'L1', -- 'L0' | 'L1' | 'L2' | 'L3'
                                                -- L0: 内建Python函数（最安全，需代码部署）
                                                -- L1: asteval安全表达式（数学运算 only）
                                                -- L2: NumExpr受限DSL（数组运算）
                                                -- L3: RestrictedPython沙箱脚本（最灵活，需审核）
    
    -- 公式定义（根据 level 使用不同字段）
    inputs          TEXT NOT NULL,              -- JSON: ["focal_length", "sensor_w", ...]
    outputs         TEXT NOT NULL,              -- JSON: ["fov_w", "afov_h"]
    formula_expr    TEXT,                       -- L1/L2: 数学表达式字符串
    python_func     TEXT,                       -- L0: Python函数名（代码库中实现）
    script_body     TEXT,                       -- L3: 受限Python脚本体
    
    -- 元数据
    description     TEXT,
    domain          TEXT,                       -- 'universal' | 'industrial' | 'microscope' | 'infrared'
    version         INTEGER DEFAULT 1,
    active          BOOLEAN DEFAULT 1,
    verified        BOOLEAN DEFAULT 0           -- L3脚本是否经过人工审核
);
```

**分级运行时策略**：

| 级别 | 运行时 | 适用场景 | 热更新 |
|------|--------|---------|:------:|
| **L0** | 直接调用 Python 函数 | 核心光学公式（薄透镜、景深、传感器换算） | ❌ 需代码部署 |
| **L1** | `asteval` 安全表达式引擎 | 参数化公式（带系数的线性组合、幂运算） | ✅ 改DB即生效 |
| **L2** | `numexpr` 受限DSL | 数组级批量运算（光谱数据处理） | ✅ 改DB即生效 |
| **L3** | `RestrictedPython` 沙箱 | 复杂领域算法（自定义评分函数） | ⚠️ 需审核后生效 |

**L1 示例**：
```python
from asteval import Interpreter
aeval = Interpreter()
safe_symbols = {'sin': math.sin, 'cos': math.cos, 'sqrt': math.sqrt, 'pi': math.pi}
aeval.symtable.update(safe_symbols)

# 从数据库加载 L1 表达式
expr = "focal * sensor / (fov + sensor)"  -- from formula_registry
result = aeval.eval(expr, focal=25, sensor=8.8, fov=50)
```

---

## 4. 数据初始化策略

### 4.1 种子数据来源

| 数据类型 | 来源 | 获取方式 | 预估数量 |
|---------|------|---------|---------|
| 工业镜头 | Basler, Edmund Optics, Computar, Kowa, VST | 官网爬取 / 规格书PDF解析 | 2,000+ |
| 工业相机 | Basler, FLIR (BFS系列), Hikrobotics, Daheng | 官网爬取 | 1,500+ |
| 显微镜物镜 | Olympus, Nikon, Leica, Zeiss, Motic | 官网爬取 + 公开目录 | 800+ |
| 红外探测器 | FLIR, Lynred, SCD, Xenics | 部分公开数据 | 200+ |
| 红外镜头 | Lightpath, Janos, Ophir | 官网爬取 | 300+ |
| C-Mount适配器 | 各显微镜厂商 | 官网爬取 | 400+ |

### 4.2 数据爬取/录入管道

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Data Source │───►│  Crawler /  │───►│  Parser /   │───►│  Validator  │
│  (网站/PDF)  │    │  PDF Extract│    │  Normalizer │    │  (人工+自动) │
└─────────────┘    └─────────────┘    └─────────────┘    └──────┬──────┘
                                                                  │
┌─────────────────────────────────────────────────────────────────▼──────┐
│                         Staging DB (临时库)                            │
│  - raw_data: 原始爬取内容                                              │
│  - parsed_data: 解析后的结构化数据                                      │
│  - validation_queue: 待核验队列                                        │
└─────────────────────────────────────────────────────────────────┬──────┘
                                                                  │
┌─────────────────────────────────────────────────────────────────▼──────┐
│                         Master DB (主数据库)                           │
│  - 经核验的正式数据                                                    │
│  - 版本控制                                                            │
└────────────────────────────────────────────────────────────────────────┘
```

### 4.3 种子数据优先级

按**MVP需要的最小数据集**排序：

**Phase 1（MVP必备）**：
- Top 10 工业镜头厂商的主流FA镜头（~200款）
- Top 10 工业相机厂商的主流面阵相机（~150款）
- 常用C/CS/F/M42接口定义数据
- 标准传感器尺寸换算表

**Phase 2**：
- 远心镜头数据（Opto Engineering, Moritex等）
- 显微镜物镜+适配器数据
- 红外镜头和探测器基础数据

**Phase 3**：
- 线扫相机/镜头
- SWIR/MWIR器件
- 用户贡献数据入口

---

## 5. 数据库技术选型

### 5.1 单机版 (MVP)

| 组件 | 选型 | 理由 |
|------|------|------|
| 主数据库 | SQLite | 零配置、单文件、Python原生支持 |
| 数据访问 | SQLAlchemy ORM | 跨数据库兼容、类型安全 |
|  migrations | Alembic | 数据库版本管理 |
| 缓存 | 内存dict + LRU | 简单高效 |

### 5.2 服务端版

| 组件 | 选型 | 理由 |
|------|------|------|
| 主数据库 | PostgreSQL | 复杂查询、JSON字段、全文检索 |
| 缓存 | Redis | 热点数据缓存、会话管理 |
| 搜索 | PostgreSQL GIN索引 / Meilisearch | 型号模糊搜索 |
| 对象存储 | MinIO / S3 | 规格书PDF、图片存储 |

---

## 6. 数据质量与治理

### 6.1 数据质量评分模型

```python
def calculate_data_quality_score(record: dict) -> float:
    """
    计算单条记录的数据完整度评分 (0-1)。
    **当前状态**：该函数尚未实现；模型中 `data_quality_score` 字段默认 0，仅作占位。
    """
    required_fields = {
        'lens': ['model', 'focal_length_mm', 'max_aperture', 'image_circle_mm', 'mount_type'],
        'detector': ['model', 'sensor_w_mm', 'sensor_h_mm', 'resolution_w', 'resolution_h', 'pixel_size_um']
    }
    
    category = record.get('category', 'lens')
    fields = required_fields.get(category, [])
    
    if not fields:
        return 0.0
    
    filled = sum(1 for f in fields if record.get(f) is not None)
    base_score = filled / len(fields)
    
    # 加分项
    bonus = 0.0
    if record.get('price_usd'): bonus += 0.05
    if record.get('datasheet_url'): bonus += 0.05
    if record.get('verified'): bonus += 0.1
    
    return min(1.0, base_score + bonus)
```

### 6.2 数据版本管理

```sql
-- 镜头参数历史版本表
CREATE TABLE lens_catalog_history (
    history_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    lens_id         INTEGER NOT NULL,
    changed_fields  TEXT NOT NULL,              -- JSON: {"focal_length_mm": {"old": 25, "new": 25.2}}
    changed_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by      TEXT                        -- 'crawler_v2.1' | 'user_admin' | 'manual_review'
);
```
