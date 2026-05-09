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
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐       │     │
│  │  │ 基础校验    │ │ 内容校验    │ │ 高级校验    │       │     │
│  │  │ 4 检测器    │ │ 2 检测器    │ │ 3 检测器    │       │     │
│  │  └────────────┘ └──────────── └────────────┘       │     │
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

1. **单一职责原则**: 每个模块只负责一个功能
2. **依赖倒置原则**: 高层模块不依赖低层模块，都依赖抽象
3. **开闭原则**: 对扩展开放，对修改关闭
4. **接口隔离原则**: 使用小接口而非大接口

---

## 检测器层详解

### 检测器分类

```
detectors/
├── basic/                      # 基础校验模块
│   ├── watermark_detector.py   # 水印/标签检测
│   ├── time_validator.py       # 时间校验
│   ├── location_validator.py   # 地点校验
│   └── quality_checker.py      # 图片质量校验
├── content/                    # 内容校验模块
│   ├── object_validator.py     # 物体识别校验
│   └── text_validator.py       # 文字识别校验
└── advanced/                   # 高级校验模块
    ├── ai_generator_detector.py  # AI 生成检测
    ├── ps_forgery_detector.py    # PS 伪造检测
    └── duplicate_detector.py     # 重复图片检测
```

### 检测器基类

```python
# ai_check/core/detector_base.py
class DetectorBase(ABC):
    """检测器抽象基类"""

    @property
    def name(self) -> str                    # 检测器名称
    @property
    def detection_type(self) -> DetectionType  # 检测类型
    @property
    def enabled(self) -> bool                # 是否启用

    def initialize(self) -> bool             # 初始化（加载模型等）
    def detect(self, image_info) -> DetectionResult  # 执行检测
    def cleanup(self) -> None                # 清理资源
```

### 检测类型枚举

```python
# ai_check/core/detector_base.py
class DetectionType(Enum):
    # 基础校验
    BASIC_WATERMARK = "basic_watermark"       # 水印检测
    BASIC_TIME = "basic_time"                 # 时间校验
    BASIC_LOCATION = "basic_location"         # 地点校验
    BASIC_QUALITY = "basic_quality"           # 质量校验
    
    # 内容校验
    CONTENT_OBJECT = "content_object"         # 物体识别
    CONTENT_TEXT = "content_text"             # 文字识别
    
    # 高级校验
    ADVANCED_AI_GENERATED = "advanced_ai"     # AI 生成检测
    ADVANCED_PS_FORGERY = "advanced_ps"       # PS 伪造检测
    ADVANCED_DUPLICATE = "advanced_duplicate" # 重复检测
    
    # 扩展
    CUSTOM = "custom"                         # 自定义检测
```

### 检测器注册表

```python
# ai_check/core/detector_registry.py
class DetectorRegistry:
    """检测器注册表 - 实现插件机制"""

    @classmethod
    def register(cls, name: str) -> callable   # 装饰器注册
    @classmethod
    def create(cls, name: str) -> DetectorBase  # 创建实例
    @classmethod
    def list_registered(cls) -> list[str]       # 列出所有注册
```

**使用示例**:

```python
# 方式 1：装饰器注册
@DetectorRegistry.register("quality_checker")
class QualityChecker(DetectorBase):
    ...

# 方式 2：直接注册
DetectorRegistry.register_class("my_detector", MyDetectorClass)

# 创建实例
detector = DetectorRegistry.create("quality_checker", config={...})
```

---

## 核心模块详解

### 1. 流水线层 (Pipeline)

```python
# ai_check/core/pipeline.py
class Pipeline:
    """检测流水线"""

    def __init__(self, config: PipelineConfig):
        self._detectors: list[DetectorBase] = []

    def add_detector(self, detector: DetectorBase) -> None
    def remove_detector(self, name: str) -> None
    def process_single(self, image_info) -> PipelineResult
    def process_batch(self, images: list) -> list[PipelineResult]
```

**工作流程**:

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
│ 检测器 1     │ ─→ 结果 1
├─────────────┤
│ 检测器 2     │ ─→ 结果 2
├─────────────┤
│ 检测器 N     │ ─→ 结果 N
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

### 2. 任务管理层 (TaskManager)

```python
# ai_check/core/task_manager.py
class TaskManager:
    """任务管理器 - 支持暂停/恢复/取消"""

    def create_task(self, name: str, images: list) -> Task
    def start_task(self, task_id: str, pipeline: Pipeline) -> None
    def pause_task(self, task_id: str) -> None
    def resume_task(self, task_id: str) -> None
    def cancel_task(self, task_id: str) -> None
```

**任务状态流转**:

```
PENDING ──start──► RUNNING ──complete──► COMPLETED
                       │
                       ├──pause──► PAUSED ──resume──► RUNNING
                       │
                       ├──cancel──► CANCELLED
                       │
                       └──error──► FAILED
```

### 3. 存储层 (Storage)

#### 3.1 数据库 (SQLite)

```python
# ai_check/storage/database.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text

class DetectionResult(Base):
    __tablename__ = 'detection_results'
    
    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False, index=True)
    image_hash = Column(String, index=True)  # pHash 用于去重
    created_at = Column(DateTime, default=datetime.now)
    result_json = Column(Text)  # JSON 存储各检测器结果
    
    # 汇总状态
    is_duplicate = Column(Boolean, default=False)
    is_ai_generated = Column(Boolean, default=False)
    is_tampered = Column(Boolean, default=False)
    quality_score = Column(Float)
    
    # 人工复核状态
    reviewed = Column(Boolean, default=False)
    review_result = Column(String)  # 'pass' / 'fail' / 'uncertain'
    review_note = Column(String)
```

#### 3.2 向量索引 (FAISS)

```python
# ai_check/storage/vector_index.py
class VectorIndex:
    """FAISS 向量索引 - 支持万级图片毫秒检索"""

    def __init__(self, dimension: int = 512):
        self.index = faiss.IndexIVFFlat(dimension)

    def add(self, vectors: np.ndarray) -> None
    def search(self, query: np.ndarray, k: int) -> tuple
    def save(self, path: Path) -> None
    def load(self, path: Path) -> None
```

#### 3.3 缓存管理

```python
# ai_check/storage/cache.py
class CacheManager:
    """LRU 缓存管理 - 控制内存占用"""

    def get(self, key: str) -> Any | None
    def set(self, key: str, value: Any) -> None
    def delete(self, key: str) -> None
    def clear(self) -> None
```

---

## GUI 层设计

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

```python
# ai_check/app/workers/detection_worker.py
class DetectionWorker(QThread):
    """后台检测线程 - 避免阻塞 GUI"""
    
    progress = pyqtSignal(int, int, str)  # 当前/总数/消息
    finished = pyqtSignal(bool)           # 完成信号
    result_ready = pyqtSignal(object)     # 结果信号

    def run(self):
        for i, image in enumerate(images):
            result = pipeline.process_single(image)
            self.progress.emit(i, len(images), f"处理中...")
            self.result_ready.emit(result)
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
# config/default_config.yaml
app:
  name: "AI Check"
  version: "0.1.0"

hardware:
  device: "auto"        # auto/cpu/cuda
  gpu_memory_limit: 0.8

detection:
  batch_size: 32
  confidence_threshold: 0.5
  
  # 检测器配置
  detectors:
    quality_checker:
      enabled: true
      blur_threshold: 100
    duplicate_detector:
      enabled: true
      similarity_threshold: 5
    ps_forgery_detector:
      enabled: true
      ela_threshold: 30

storage:
  database:
    path: "~/.ai_check/data/ai_check.db"
  cache:
    max_size_mb: 1024
```

---

## 扩展点

### 添加新检测器

```python
# 1. 创建检测器类
from ai_check.core import DetectorBase, DetectionResult, DetectionType
from ai_check.core.detector_registry import DetectorRegistry

@DetectorRegistry.register("my_detector")
class MyDetector(DetectorBase):
    def __init__(self, name="my_detector", config=None):
        super().__init__(name, DetectionType.CUSTOM, config)

    def _initialize(self) -> bool:
        # 加载模型等初始化操作
        return True

    def _detect(self, image_info):
        # 执行检测
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=False,
            confidence=0.0,
            description="检测结果"
        )

# 2. 在配置中启用
# config.yaml
detection:
  detectors:
    my_detector:
      enabled: true
      threshold: 0.5

# 3. 在流水线中使用
pipeline.add_detector(MyDetector())
```

---

## 性能考虑

### 内存管理

- 图片按需加载，处理完后释放
- 批处理时分批加载，控制内存使用
- 使用 LRU 缓存，限制最大内存占用

### 并行策略

| 场景 | 策略 | 实现 |
|------|------|------|
| CPU 密集型 | 多进程 | ProcessPoolExecutor |
| I/O 密集型 | 多线程 | ThreadPoolExecutor |
| GPU 推理 | 单线程批量 | ONNX Runtime batch |

### 模型优化

- 使用 ONNX 格式，支持量化
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

- [检测器实现指南](../guides/detectors-implementation-guide.md)
- [前端架构](frontend-architecture.md)
- [性能优化指南](../guides/performance.md)

---

**最后更新**: 2026-05-08
