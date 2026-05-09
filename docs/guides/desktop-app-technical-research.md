# 桌面软件技术方案调研报告

## 一、需求概述

### 1.1 用户定位
- **目标用户**: 个人专业用户（摄影师、设计师、自媒体从业者）
- **使用场景**: 本地图片质量检测、伪造识别、内容审核

### 1.2 核心需求
| 需求项 | 要求 |
|--------|------|
| 处理量级 | 重量级 (>1000 张/次) |
| 数据存储 | 本地数据库 (SQLite) |
| 准确率 | 可控，越高越好，支持人工复核 |
| 模型策略 | 仅使用预训练模型 |
| 发布方式 | 单机版 (exe 打包) |
| 硬件兼容 | CPU + 可选 GPU 自适应 |
| 网络要求 | 完全离线运行 |

---

## 二、技术选型总览

### 2.1 架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    表现层 (GUI)                          │
│                   PyQt6 + QSS                            │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层                            │
│              Pipeline + TaskManager                      │
├─────────────────────────────────────────────────────────┤
│                    检测器层                              │
│         DetectorRegistry + 各类检测器                    │
├─────────────────────────────────────────────────────────┤
│                    数据访问层                            │
│          SQLite (SQLAlchemy) + 缓存                      │
├─────────────────────────────────────────────────────────┤
│                    基础设施层                            │
│       日志 + 配置 + 硬件检测 + 图像处理工具              │
└─────────────────────────────────────────────────────────┘
```

### 2.2 核心技术栈

| 层级 | 技术选型 | 备选方案 | 选择理由 |
|------|----------|----------|----------|
| **GUI 框架** | PyQt6 | PySide6、Tkinter | 组件丰富、文档完善、跨平台 |
| **推理引擎** | ONNX Runtime | PyTorch、TensorFlow | CPU/GPU 自适应、性能好 |
| **数据库** | SQLite + SQLAlchemy | PostgreSQL、MySQL | 零配置、单文件、免运维 |
| **向量检索** | FAISS | Annoy、HNSWlib | Facebook 出品、万级数据高效 |
| **图像处理** | OpenCV + Pillow | scikit-image | 功能全面、性能优秀 |
| **OCR** | PaddleOCR | Tesseract、EasyOCR | 中文支持最好、速度快 |
| **打包工具** | PyInstaller | Nuitka、cx_Freeze | 成熟稳定、社区活跃 |

---

## 三、详细技术调研

### 3.1 GUI 框架选型

#### 方案对比

| 框架 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **PyQt6** | 组件最丰富、文档完善、社区大 | 商业授权收费 (GPL/LGPL) | 复杂桌面应用 |
| **PySide6** | Qt 官方、BSD 授权免费 | 生态略小于 PyQt | 开源项目优先 |
| **Tkinter** | Python 内置、零依赖 | 界面简陋、功能有限 | 简单工具 |
| **CustomTkinter** | 现代化界面、简单易用 | 功能有限 | 中小型应用 |
| **Flet** | 跨平台 (Web/桌面/移动) | 较新、生态不成熟 | 全平台应用 |

#### 推荐：**PyQt6**

**理由**:
1. 组件最丰富，支持复杂界面
2. 文档和教程最多，学习成本低
3. 支持 QSS 样式表，可高度定制
4. 信号槽机制，线程安全

**依赖**:
```txt
PyQt6>=6.6.0
PyQt6-Qt6>=6.6.0
```

---

### 3.2 推理引擎选型

#### 方案对比

| 引擎 | CPU 性能 | GPU 支持 | 模型格式 | 离线支持 |
|------|----------|----------|----------|----------|
| **ONNX Runtime** | ⭐⭐⭐⭐⭐ | CUDA/DirectML | .onnx | ✅ |
| **PyTorch** | ⭐⭐⭐⭐ | CUDA | .pt/.pth | ✅ |
| **TensorFlow** | ⭐⭐⭐ | CUDA | .pb/.h5 | ✅ |
| **OpenVINO** | ⭐⭐⭐⭐⭐ | 仅 Intel | .xml/.bin | ✅ |

#### 推荐：**ONNX Runtime**

**理由**:
1. **CPU/GPU 自适应**: 自动检测并使用最佳后端
2. **性能优秀**: 比原生 PyTorch 快 2-3 倍
3. **模型转换**: 支持 PyTorch/TensorFlow → ONNX
4. **内存占用低**: 适合批量处理

**依赖**:
```txt
onnxruntime>=1.16.0           # CPU 版本
onnxruntime-gpu>=1.16.0       # GPU 版本 (可选)
```

**硬件检测代码**:
```python
import onnxruntime as ort

def get_available_providers():
    """获取可用推理后端"""
    providers = ['CPUExecutionProvider']
    
    # 检测 CUDA
    if 'CUDAExecutionProvider' in ort.get_available_providers():
        providers.insert(0, 'CUDAExecutionProvider')
    
    # 检测 DirectML (Windows)
    if 'DmlExecutionProvider' in ort.get_available_providers():
        providers.insert(0, 'DmlExecutionProvider')
    
    return providers
```

---

### 3.3 数据库选型

#### 方案对比

| 数据库 | 优点 | 缺点 | 适用场景 |
|--------|------|------|----------|
| **SQLite** | 零配置、单文件、免运维 | 并发写入受限 | 本地应用 ✅ |
| **PostgreSQL** | 功能强大、扩展性好 | 需要独立服务 | 服务端应用 |
| **MySQL** | 流行、文档多 | 需要独立服务 | 服务端应用 |
| **DuckDB** | 分析查询快 | 较新、生态小 | 数据分析 |

#### 推荐：**SQLite + SQLAlchemy**

**理由**:
1. **零配置**: 无需安装数据库服务
2. **单文件**: 数据存储在单一 .db 文件
3. **SQLAlchemy ORM**: 类型安全、代码简洁
4. **足够性能**: 单用户场景完全够用

**依赖**:
```txt
sqlite3              # Python 内置
sqlalchemy>=2.0.0
```

**数据库设计**:
```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DetectionResult(Base):
    __tablename__ = 'detection_results'
    
    id = Column(Integer, primary_key=True)
    image_path = Column(String, nullable=False, index=True)
    image_hash = Column(String, index=True)  # pHash 用于去重
    
    # 检测时间
    created_at = Column(DateTime, default=datetime.now)
    
    # 检测结果 (JSON 格式存储各检测器结果)
    result_json = Column(Text)  # JSON 字符串
    
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

---

### 3.4 向量检索选型

#### 方案对比

| 引擎 | 检索速度 | 内存占用 | 规模支持 | 易用性 |
|------|----------|----------|----------|--------|
| **FAISS** | ⭐⭐⭐⭐⭐ | 中等 | 百万级 | ⭐⭐⭐⭐ |
| **Annoy** | ⭐⭐⭐⭐ | 低 | 十万级 | ⭐⭐⭐⭐⭐ |
| **HNSWlib** | ⭐⭐⭐⭐⭐ | 高 | 百万级 | ⭐⭐⭐ |
| **Chroma** | ⭐⭐⭐ | 高 | 十万级 | ⭐⭐⭐⭐ |

#### 推荐：**FAISS**

**理由**:
1. **Facebook 出品**: 成熟稳定，持续维护
2. **高性能**: IVF 索引支持百万级图片毫秒检索
3. **多种索引**: 支持精确/近似检索
4. **CPU/GPU**: 支持 GPU 加速检索

**依赖**:
```txt
faiss-cpu>=1.7.4        # CPU 版本
# 或
faiss-gpu>=1.7.4        # GPU 版本
```

**万级图片索引策略**:
```python
import faiss
import numpy as np

class VectorIndex:
    def __init__(self, dim: int = 512):
        self.dim = dim
        # IVF 索引，适合万级数据
        # nlist = 16 * sqrt(N) ≈ 1600 for N=10000
        quantizer = faiss.IndexFlatL2(dim)
        self.index = faiss.IndexIVFFlat(quantizer, dim, nlist=1600)
    
    def train(self, vectors: np.ndarray):
        """训练索引 (需要部分数据)"""
        self.index.train(vectors)
    
    def add(self, vectors: np.ndarray, ids: np.ndarray):
        """添加向量"""
        self.index.add(vectors)
    
    def search(self, query: np.ndarray, k: int = 5):
        """检索最相似 k 个"""
        distances, indices = self.index.search(query.reshape(1, -1), k)
        return indices[0], distances[0]
```

---

### 3.5 图像处理库选型

#### 方案对比

| 库 | 功能 | 性能 | 易用性 | 推荐场景 |
|----|------|------|--------|----------|
| **OpenCV** | 最全 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 专业图像处理 |
| **Pillow** | 基础 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 简单图片操作 |
| **scikit-image** | 科研向 | ⭐⭐ | ⭐⭐⭐ | 算法研究 |

#### 推荐：**OpenCV + Pillow 组合**

**OpenCV**: 图像质量分析、频域分析、特征提取
**Pillow**: EXIF 读取、格式转换、基础操作

**依赖**:
```txt
opencv-python>=4.8.0
Pillow>=10.0.0
```

---

### 3.6 OCR 引擎选型

#### 方案对比

| 引擎 | 中文支持 | 速度 | 准确率 | 依赖 |
|------|----------|------|--------|------|
| **PaddleOCR** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | PaddlePaddle |
| **Tesseract** | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 无 |
| **EasyOCR** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | PyTorch |
| **RapidOCR** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ONNX |

#### 推荐：**PaddleOCR** (或 RapidOCR 作为轻量替代)

**理由**:
1. **中文支持最好**: 专门针对中文优化
2. **速度快**: PP-OCRv4 模型轻量高效
3. **准确率高**: 业界领先水平
4. **离线运行**: 完全本地推理

**依赖**:
```txt
paddlepaddle>=2.5.0      # 或 paddlepaddle-gpu
paddleocr>=2.7.0
```

**轻量替代方案**:
```txt
rapidocr-onnxruntime>=1.0.0  # ONNX 版本，更轻量
```

---

### 3.7 打包工具选型

#### 方案对比

| 工具 | 打包速度 | 输出大小 | 兼容性 | 易用性 |
|------|----------|----------|--------|--------|
| **PyInstaller** | ⭐⭐⭐ | 中等 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **Nuitka** | ⭐⭐ | 小 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **cx_Freeze** | ⭐⭐⭐ | 中等 | ⭐⭐⭐ | ⭐⭐⭐ |
| **py2exe** | ⭐⭐ | 中等 | ⭐⭐⭐ | ⭐⭐ |

#### 推荐：**PyInstaller**

**理由**:
1. **成熟稳定**: 社区最活跃，问题少
2. **跨平台**: Windows/macOS/Linux 通吃
3. **单文件模式**: 可打包为单一 exe
4. **隐藏控制台**: 支持 GUI 模式

**依赖**:
```txt
pyinstaller>=6.0.0
```

**打包配置示例**:
```python
# ai_check.spec
from PyInstaller.utils.hooks import collect_submodules

a = Analysis(
    ['ai_check/app/main.py'],
    packages=[
        'ai_check',
        'onnxruntime',
        'paddleocr',
        'sqlalchemy',
    ],
    hiddenimports=[
        *collect_submodules('ai_check.detectors'),
        'paddle.fluid',
        'paddle.nn',
    ],
)

exe = EXE(
    a,
    name='AI Check',
    icon='ai_check/resources/icon.ico',
    console=False,  # 隐藏控制台
    upx=True,       # 压缩
)
```

---

## 四、性能优化策略

### 4.1 批量处理优化

**问题**: 1000+ 图片逐个处理太慢

**解决方案**:
```python
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

class BatchProcessor:
    def __init__(self, batch_size: int = 32, num_workers: int = 4):
        self.batch_size = batch_size
        self.num_workers = num_workers
    
    def process_batch(self, images: list):
        """批量处理图片"""
        # 1. 并行加载图片
        with ThreadPoolExecutor(self.num_workers) as loader:
            loaded_images = list(loader.map(self._load_image, images))
        
        # 2. 批量推理 (ONNX Runtime 支持批处理)
        batch_results = self._batch_inference(loaded_images)
        
        # 3. 异步写入数据库
        self._async_save_results(batch_results)
        
        return batch_results
```

### 4.2 内存管理优化

**问题**: 大量图片同时加载导致内存溢出

**解决方案**:
```python
import gc
from collections import OrderedDict

class LRUCache:
    """LRU 缓存，限制内存占用"""
    def __init__(self, max_size: int = 100):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key: str):
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            oldest = self.cache.popitem(last=False)
            del oldest  # 释放内存
            gc.collect()
```

### 4.3 GPU 加速策略

**自适应硬件检测**:
```python
import torch
import onnxruntime as ort

class HardwareDetector:
    @staticmethod
    def detect() -> dict:
        """检测硬件能力"""
        result = {
            'cuda_available': torch.cuda.is_available(),
            'gpu_name': None,
            'gpu_memory': 0,
            'recommended_backend': 'cpu',
        }
        
        if torch.cuda.is_available():
            result['gpu_name'] = torch.cuda.get_device_name(0)
            result['gpu_memory'] = torch.cuda.get_device_properties(0).total_memory
            result['recommended_backend'] = 'cuda'
        
        # 检查 ONNX Runtime 可用后端
        result['ort_providers'] = ort.get_available_providers()
        
        return result
```

---

## 五、准确率控制策略

### 5.1 多模型融合

**策略**: 使用多个检测器投票决定结果

```python
class EnsembleDetector:
    def __init__(self):
        self.detectors = [
            UnivFDDetector(),      # 模型 1
            FrequencyDetector(),   # 模型 2
            NoiseDetector(),       # 模型 3
        ]
    
    def detect(self, image) -> dict:
        results = [d.detect(image) for d in self.detectors]
        
        # 加权投票
        weighted_score = sum(
            r['confidence'] * r['is_ai_generated'] 
            for r in results
        ) / len(results)
        
        return {
            'is_ai_generated': weighted_score > 0.5,
            'confidence': weighted_score,
            'individual_results': results,
        }
```

### 5.2 阈值可调

**策略**: 用户可调整检测灵敏度

```python
class ConfigurableDetector:
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
    
    def set_threshold(self, value: float):
        """调整阈值 (0-1)"""
        self.threshold = max(0, min(1, value))
    
    def detect(self, image) -> dict:
        score = self._compute_score(image)
        return {
            'is_positive': score > self.threshold,
            'confidence': score,
            'threshold': self.threshold,
        }
```

### 5.3 人工复核流程

**策略**: 低置信度结果标记为"待复核"

```python
class ReviewWorkflow:
    UNCERTAIN_THRESHOLD = 0.3  # 置信度在 0.3-0.7 之间标记为待复核
    
    def process(self, result: dict) -> dict:
        confidence = result['confidence']
        
        # 计算不确定区间
        if 0.5 - self.UNCERTAIN_THRESHOLD < confidence < 0.5 + self.UNCERTAIN_THRESHOLD:
            result['needs_review'] = True
            result['review_priority'] = 'medium'
        elif confidence < 0.2 or confidence > 0.8:
            result['needs_review'] = False
        else:
            result['needs_review'] = True
            result['review_priority'] = 'low'
        
        return result
```

---

## 六、模块依赖关系

### 6.1 完整依赖树

```
ai_check/
├── core/                      # 核心模块 (0 外部依赖)
│   ├── detector_base.py       # 检测器基类
│   ├── detector_registry.py   # 注册表
│   └── pipeline.py            # 流水线
│
├── detectors/                 # 检测器模块
│   ├── duplicate/             # 重复检测
│   │   └── hash_detector.py   # 依赖：imagehash, Pillow
│   ├── forgery/               # 伪造检测
│   │   ├── ps_detector.py     # 依赖：OpenCV
│   │   └── ai_detector.py     # 依赖：ONNX Runtime, torch
│   └── content/               # 内容检测
│       └── ocr_detector.py    # 依赖：PaddleOCR
│
├── storage/                   # 存储模块
│   ├── database.py            # 依赖：SQLAlchemy, SQLite
│   └── vector_index.py        # 依赖：FAISS, numpy
│
├── app/                       # GUI 模块
│   ├── main_window.py         # 依赖：PyQt6
│   └── widgets/               # 组件
│
└── utils/                     # 工具模块
    ├── image_utils.py         # 依赖：OpenCV, Pillow
    ├── hardware_utils.py      # 依赖：torch, onnxruntime
    └── log_utils.py           # 依赖：logging
```

### 6.2 依赖分级

**核心依赖** (必须):
```txt
PyQt6>=6.6.0
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
sqlalchemy>=2.0.0
```

**检测器依赖** (按需):
```txt
# 重复检测
imagehash>=4.3.0

# 伪造检测
onnxruntime>=1.16.0
torch>=2.0.0

# OCR
paddlepaddle>=2.5.0
paddleocr>=2.7.0

# 向量检索
faiss-cpu>=1.7.4
```

**开发依赖**:
```txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
pre-commit>=3.0.0
```

---

## 七、风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| **模型准确率低** | 中 | 高 | 多模型融合、阈值可调、人工复核 |
| **处理速度慢** | 中 | 中 | 批量处理、GPU 加速、进度显示 |
| **内存溢出** | 低 | 中 | LRU 缓存、分块处理、流式加载 |
| **打包体积大** | 高 | 低 | 模型按需加载、可选组件、UPX 压缩 |
| **兼容性问题** | 中 | 中 | 多环境测试、降级方案、详细日志 |
| **PaddleOCR 依赖大** | 高 | 低 | 提供 RapidOCR 轻量替代方案 |

---

## 八、最终技术栈清单

### 8.1 运行时依赖

```txt
# GUI
PyQt6>=6.6.0

# 图像处理
opencv-python>=4.8.0
Pillow>=10.0.0
imagehash>=4.3.0

# 深度学习推理
onnxruntime>=1.16.0
torch>=2.0.0

# OCR (二选一)
paddlepaddle>=2.5.0
paddleocr>=2.7.0
# 或轻量版
rapidocr-onnxruntime>=1.0.0

# 数据库
sqlalchemy>=2.0.0

# 向量检索
faiss-cpu>=1.7.4

# 工具库
numpy>=1.24.0
```

### 8.2 开发工具

```txt
# 代码质量
black>=23.0.0
isort>=5.12.0
mypy>=1.0.0
ruff>=0.1.0

# 测试
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-qt>=4.0.0

# 打包
pyinstaller>=6.0.0

# 预提交钩子
pre-commit>=3.0.0
```

---

## 九、下一步行动

1. **确认技术选型**: 评审本方案，确认无遗漏
2. **开始实现 P0 功能**:
   - 图片质量校验 (OpenCV)
   - 重复图片检测 (imagehash)
   - 文字识别校验 (PaddleOCR)
3. **搭建 GUI 框架**: PyQt6 主窗口 + 基础组件
4. **性能基准测试**: 建立性能基线，持续优化

---

**文档版本**: v1.0
**创建时间**: 2026-05-08
**作者**: AI Assistant
