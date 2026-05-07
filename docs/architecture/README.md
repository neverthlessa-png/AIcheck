# 架构设计文档

本文档详细描述 AI Check 的系统架构设计，帮助开发者理解系统整体结构。

---

## 架构概览

### 分层架构

系统采用经典的分层架构，从上到下依次为：

```
┌─────────────────────────────────────────────────────────────────┐
│                      Presentation Layer                         │
│                      (GUI Layer - PyQt6)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Main Window │ │ Detection   │ │ Result      │              │
│  │             │ │ Panel       │ │ Viewer      │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                      Application Layer                          │
│                      (Service Layer)                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Pipeline    │ │ TaskManager │ │ ReportService│              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
├─────────────────────────────────────────────────────────────────┤
│                      Domain Layer                               │
│                      (Business Logic)                           │
│  ┌──────────────────────────────────────────────────────┐     │
│  │                  Detector Layer                       │     │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │     │
│  │  │Forgery │ │Duplicate│ │Document│ │Content │        │     │
│  │  │Detector│ │Detector │ │Detector│ │Detector│        │     │
│  │  └────────┘ └────────┘ └────────┘ └────────┘        │     │
│  └──────────────────────────────────────────────────────┘     │
├─────────────────────────────────────────────────────────────────┤
│                      Infrastructure Layer                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │ Model       │ │ Storage     │ │ Utils       │              │
│  │ Manager     │ │ (DB/Cache)  │ │             │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### 架构原则

1. **单一职责原则**：每个模块只负责一个功能
2. **依赖倒置原则**：高层模块不依赖低层模块，都依赖抽象
3. **开闭原则**：对扩展开放，对修改关闭
4. **接口隔离原则**：使用小接口而非大接口

---

## 核心模块详解

### 1. 检测器层 (Detector Layer)

这是系统的核心，负责执行具体的检测逻辑。

#### 1.1 检测器基类 (DetectorBase)

```python
class DetectorBase(ABC):
    """检测器抽象基类"""

    # 属性
    @property
    def name(self) -> str          # 检测器名称
    @property
    def detection_type(self) -> DetectionType  # 检测类型
    @property
    def enabled(self) -> bool      # 是否启用

    # 方法
    def initialize(self) -> bool   # 初始化（加载模型等）
    def detect(self, image_info: ImageInfo) -> DetectionResult  # 执行检测
    def cleanup(self) -> None      # 清理资源
```

**设计要点**：
- 使用抽象基类定义统一接口
- 所有检测器必须实现 `_initialize()` 和 `_detect()` 方法
- 支持延迟初始化，节省资源

#### 1.2 检测器注册表 (DetectorRegistry)

```python
class DetectorRegistry:
    """检测器注册表 - 实现插件机制"""

    @classmethod
    def register(cls, name: str) -> callable   # 装饰器注册
    @classmethod
    def create(cls, name: str) -> DetectorBase  # 创建实例
    @classmethod
    def list_registered(cls) -> list[str]       # 列出所有注册
```

**设计要点**：
- 使用注册表模式实现插件机制
- 支持装饰器方式注册检测器
- 运行时动态加载检测器

**使用示例**：

```python
# 方式1：装饰器注册
@DetectorRegistry.register("my_detector")
class MyDetector(DetectorBase):
    ...

# 方式2：直接注册
DetectorRegistry.register_class("my_detector", MyDetectorClass)

# 创建实例
detector = DetectorRegistry.create("my_detector", config={...})
```

#### 1.3 检测类型枚举

```python
class DetectionType(Enum):
    FORGERY_PS = "forgery_ps"           # PS编辑检测
    FORGERY_AI = "forgery_ai"           # AI生成检测
    FORGERY_SPLICE = "forgery_splice"   # 拼接检测
    FORGERY_COPY_MOVE = "forgery_copy_move"  # 复制粘贴检测
    DUPLICATE_EXACT = "duplicate_exact"       # 精确重复
    DUPLICATE_SIMILAR = "duplicate_similar"   # 相似图片
    DOCUMENT_TAMPERING = "document_tampering" # 文档篡改
    DOCUMENT_TEMPLATE = "document_template"   # 模板匹配
    CONTENT_OCR = "content_ocr"               # OCR内容
    CUSTOM = "custom"                         # 自定义检测
```

### 2. 流水线层 (Pipeline Layer)

流水线协调多个检测器，管理检测流程。

#### 2.1 流水线 (Pipeline)

```python
class Pipeline:
    """检测流水线"""

    def __init__(self, config: PipelineConfig):
        self._detectors: list[DetectorBase] = []

    def add_detector(self, detector: DetectorBase) -> None
    def remove_detector(self, name: str) -> None
    def process_single(self, image_info: ImageInfo) -> PipelineResult
    def process_batch(self, images: list[ImageInfo]) -> list[PipelineResult]
```

**工作流程**：

```
输入图片
    │
    ▼
┌─────────────┐
│ 预处理      │ ← 调整尺寸、格式转换
└─────────────┘
    │
    ▼
┌─────────────┐
│ 检测器1     │ ─→ 结果1
├─────────────┤
│ 检测器2     │ ─→ 结果2
├─────────────┤
│ 检测器N     │ ─→ 结果N
└─────────────┘
    │
    ▼
┌─────────────┐
│ 结果聚合    │ ← 合并所有检测结果
└─────────────┘
    │
    ▼
PipelineResult
```

#### 2.2 并行处理

流水线支持两种处理模式：

```python
# 顺序处理（适合少量图片或调试）
results = pipeline.process_batch(images, parallel=False)

# 并行处理（适合大量图片）
results = pipeline.process_batch(images, parallel=True, max_workers=4)
```

### 3. 任务管理层 (Task Manager)

管理长时间运行的检测任务，支持暂停、恢复、取消。

```python
class TaskManager:
    """任务管理器"""

    def create_task(self, name: str, images: list) -> Task
    def start_task(self, task_id: str, pipeline: Pipeline) -> None
    def pause_task(self, task_id: str) -> None
    def resume_task(self, task_id: str) -> None
    def cancel_task(self, task_id: str) -> None
```

**任务状态流转**：

```
PENDING ──start──► RUNNING ──complete──► COMPLETED
                       │
                       ├──pause──► PAUSED ──resume──► RUNNING
                       │
                       └──cancel──► CANCELLED
                       │
                       └──error──► FAILED
```

---

## 存储层设计

### 1. 数据库 (SQLite)

```sql
-- 检测结果表
CREATE TABLE detection_results (
    id INTEGER PRIMARY KEY,
    image_path TEXT NOT NULL,
    detector_name TEXT NOT NULL,
    result_type TEXT NOT NULL,
    is_anomaly BOOLEAN,
    confidence REAL,
    details TEXT,           -- JSON格式
    created_at TIMESTAMP
);

-- 图片信息表
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    path TEXT UNIQUE NOT NULL,
    md5_hash TEXT,
    phash TEXT,
    feature_vector BLOB,    -- FAISS向量
    created_at TIMESTAMP
);

-- 检测任务表
CREATE TABLE detection_tasks (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT,
    total_images INTEGER,
    processed_images INTEGER,
    config TEXT,            -- JSON格式
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

### 2. 向量索引 (FAISS)

用于大规模相似图片检索：

```python
class VectorIndex:
    """FAISS向量索引"""

    def __init__(self, dimension: int = 512):
        self.index = faiss.IndexFlatIP(dimension)

    def add(self, vectors: np.ndarray) -> None
    def search(self, query: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]
    def save(self, path: Path) -> None
    def load(self, path: Path) -> None
```

### 3. 缓存管理

```python
class CacheManager:
    """文件缓存"""

    def get(self, key: str) -> Any | None
    def set(self, key: str, value: Any) -> None
    def delete(self, key: str) -> None
    def clear(self) -> None
```

---

## GUI层设计

### 主窗口结构

```
MainWindow
├── MenuBar
│   ├── FileMenu (打开、导出、退出)
│   ├── DetectMenu (开始、停止)
│   └── HelpMenu (关于)
├── TabWidget
│   ├── DetectionPanel (检测面板)
│   │   ├── ImageList (图片列表)
│   │   └── OptionsPanel (检测选项)
│   ├── ResultViewer (结果查看器)
│   │   ├── StatsLabel (统计信息)
│   │   ├── ResultTable (结果表格)
│   │   └── DetailPanel (详情面板)
│   └── SettingsPanel (设置面板)
└── StatusBar
    ├── StatusLabel (状态文本)
    └── ProgressBar (进度条)
```

### 异步处理

GUI使用 QThread 避免阻塞：

```python
class DetectionWorker(QThread):
    progress = pyqtSignal(int, int, str)  # 进度信号
    finished = pyqtSignal(bool)           # 完成信号

    def run(self):
        # 在后台线程执行检测
        for image in images:
            result = pipeline.process_single(image)
            self.progress.emit(i, total, message)
        self.finished.emit(True)
```

---

## 配置管理

### 配置层次

```
default_config.yaml    # 默认配置（版本控制）
    ↓ 覆盖
user_config.yaml       # 用户配置（本地）
    ↓ 覆盖
命令行参数             # 临时覆盖
```

### 配置结构

```yaml
app:                    # 应用配置
  name: "AI Check"
  version: "0.1.0"

hardware:               # 硬件配置
  device: "auto"        # auto/cpu/cuda
  gpu_memory_limit: 0.8

detection:              # 检测配置
  batch_size: 32
  confidence_threshold: 0.5
  forgery: {...}
  duplicate: {...}

storage:                # 存储配置
  database:
    path: "~/.ai_check/data/ai_check.db"
  cache:
    max_size_mb: 1024
```

---

## 扩展点

### 1. 添加新检测器

```python
# 1. 创建检测器类
@DetectorRegistry.register("my_detector")
class MyDetector(DetectorBase):
    def _initialize(self) -> bool:
        # 加载模型
        return True

    def _detect(self, image_info: ImageInfo) -> DetectionResult:
        # 执行检测
        return DetectionResult(...)

# 2. 在配置中启用
# config.yaml
detection:
  my_detector:
    enabled: true
    threshold: 0.5

# 3. 在流水线中使用
pipeline.add_detector(MyDetector())
```

### 2. 自定义预处理

```python
class Pipeline:
    def set_preprocessor(self, func: Callable[[np.ndarray], np.ndarray]):
        self._preprocessor = func
```

### 3. 自定义结果处理器

```python
class Pipeline:
    def set_result_handler(self, func: Callable[[PipelineResult], None]):
        self._result_handler = func
```

---

## 性能考虑

### 内存管理

- 图片按需加载，处理完后释放
- 批处理时分批加载，控制内存使用
- 向量索引使用FAISS，内存效率高

### 并行策略

- CPU密集型：多进程（ProcessPoolExecutor）
- I/O密集型：多线程（ThreadPoolExecutor）
- GPU推理：单线程批量推理

### 模型优化

- 使用ONNX格式，支持量化
- 模型按需加载，延迟初始化
- 支持模型缓存，避免重复加载

---

## 安全考虑

### 数据安全

- 所有处理本地进行，数据不上传
- 数据库文件权限控制
- 敏感配置（API Key）不存储

### 输入验证

- 图片格式验证
- 文件大小限制
- 路径遍历防护

---

## 相关文档

- [检测器开发指南](../guides/detector-development.md)
- [API文档](../api/README.md)
- [性能优化指南](../guides/performance.md)
