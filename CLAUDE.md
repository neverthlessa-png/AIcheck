# CLAUDE.md - AI Check 项目开发指南
> 本文档为 Claude Code 提供项目上下文和开发指导。请仔细阅读以下信息。
---

## 📖 项目概述
**AI Check** 是一个本地运行的图片 AI 检查桌面应用（PyQt6），支持伪造检测、重复检测、内容分析等功能。

### 核心信息
| 项目 | 说明 |
|------|------|
| **目标用户** | 个人专业用户 |
| **处理规模** | 重量级 (>1000 张/次) |
| **数据存储** | SQLite 本地数据库 |
| **运行环境** | 完全离线，CPU + 可选 GPU 自适应 |
| **发布方式** | 单机版 exe 打包 |
| **开发周期** | 6 个月（24 周） |

---

## 🏗️ 架构分层

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

---

## 📁 目录结构

```
AICheck/
├── ai_check/                 # 主程序包
│   ├── main.py               # 应用入口
│   ├── app/                  # GUI 应用
│   │   ├── main_window.py    # 主窗口
│   │   └── widgets/          # UI 组件
│   ├── core/                 # 核心模块
│   │   ├── detector_base.py     # 检测器基类
│   │   ├── detector_registry.py # 注册表
│   │   ├── pipeline.py          # 流水线
│   │   └── task_manager.py      # 任务管理
│   ├── detectors/            # 检测器实现
│   │   ├── forgery/          # 伪造检测
│   │   ├── duplicate/        # 重复检测
│   │   ├── document/         # 文档检测
│   │   └── content/          # 内容检测
│   ├── storage/              # 存储层
│   │   ├── database.py       # SQLite 数据库
│   │   └── vector_index.py   # FAISS 索引
│   └── utils/                # 工具函数
├── tests/                    # 测试
├── docs/                     # 文档
├── config/                   # 配置文件
├── DEVELOPMENT_LOG.md        # 开发日志（重要）
├── README.md                 # 用户文档
└── pyproject.toml           # 项目配置
```

---

## 🔧 开发命令

### 安装依赖

```bash
# 核心依赖
pip install -r requirements.txt

# 开发依赖
pip install -r requirements-dev.txt
```

### 运行应用

```bash
# GUI 模式
python -m ai_check.main

# 命令行模式
python -m ai_check.main --no-gui <images>
```

### 测试

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率
pytest tests/ --cov=ai_check --cov-report=html

# 仅单元测试
pytest tests/unit/ -v
```

### 代码质量

```bash
# 格式化
black ai_check/ tests/
isort ai_check/ tests/

# 类型检查
mypy ai_check/

# Linting
ruff check ai_check/
```

### 打包

```bash
# Windows exe
pyinstaller -w -n "AI Check" --icon=resources/icon.ico ai_check/main.py
```

---

## 📦 技术栈

### 核心依赖

| 模块 | 技术 | 版本 |
|------|------|------|
| GUI 框架 | PyQt6 | >=6.5.0 |
| 推理引擎 | ONNX Runtime | >=1.15.0 |
| 深度学习 | PyTorch | >=2.0.0 |
| 图像处理 | OpenCV + Pillow | >=4.8.0, >=10.0.0 |
| OCR | PaddleOCR | >=2.7.0 |
| 向量检索 | FAISS | >=1.7.4 |
| 数据库 | SQLite + SQLAlchemy | >=2.0.0 |

### 完整依赖树

```
ai_check/
├── core/                      # 0 外部依赖
├── detectors/
│   ├── duplicate/             # imagehash, Pillow
│   ├── forgery/               # OpenCV, ONNX, torch
│   └── content/               # PaddleOCR
├── storage/                   # SQLAlchemy, FAISS
├── app/                       # PyQt6
└── utils/                     # OpenCV, Pillow, psutil
```

---

## 📋 开发规范

### Git 提交规范 (Conventional Commits)

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(detectors): add AI generated detection` |
| `fix` | Bug 修复 | `fix(core): resolve null pointer in pipeline` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式 | `style: format code with black` |
| `refactor` | 重构 | `refactor(models): simplify detector interface` |
| `test` | 测试 | `test(forgery): add unit tests for PS detector` |
| `chore` | 构建/工具 | `chore(deps): update dependencies` |
| `perf` | 性能优化 | `perf(query): optimize database query` |
| `ci` | CI 配置 | `ci: add GitHub Actions workflow` |

**Scope 范围**:
- `core` - 核心模块
- `detectors` - 检测器
- `app` / `gui` - GUI 应用
- `storage` - 存储层
- `utils` - 工具函数
- `config` - 配置
- `deps` - 依赖

### 代码风格

**Python 命名规范**:
- 函数/变量：`snake_case`
- 类：`PascalCase`
- 常量：`UPPER_SNAKE_CASE`
- 私有成员：`_leading_underscore`

**文档字符串 (Google Style)**:
```python
def calculate_total(items: list[Item]) -> Decimal:
    """Calculate the total price of items.

    Args:
        items: A list of Item objects to calculate.

    Returns:
        The total price as a Decimal.

    Raises:
        ValueError: If items list is empty.
    """
```

**类型注解**:
```python
from typing import Optional, List, Dict, Any

def process_data(
    data: Dict[str, Any],
    options: Optional[List[str]] = None
) -> bool:
    pass
```

---

## 📝 开发日志规则 (重要)

**在开始任何开发任务前，必须阅读 `DEVELOPMENT_LOG.md` 文件。**

### 阅读目的
1. 了解最近的开发内容和变更
2. 确认没有冲突的修改
3. 理解当前开发进度和待办事项

### 更新要求

每次完成开发任务后，必须更新 `DEVELOPMENT_LOG.md`：
- 新增功能模块
- 修改现有代码
- 修复 Bug
- 更新文档
- 配置变更

### 更新格式

```markdown
### YYYY-MM-DD - [作者名]

#### 类型
- ✨ 新增 / 🐛 修复 / 📝 文档 / ♻️ 重构 / ⚡ 性能 / 🔧 配置 / 🧪 测试

#### 变更内容
- 模块/文件：具体变更描述

#### 备注
- 可选的补充说明
```

### 示例

```markdown
### 2024-05-08 - [张三]

#### 类型
- ✨ 新增

#### 变更内容
- `detectors/forgery/ai_detector.py`: 实现 AI 生成图片检测器
- `tests/test_forgery.py`: 添加对应单元测试

#### 备注
- 使用频域分析算法，准确率约 85%
```

---

## 🎯 当前开发状态

### 已完成 (W1-W4)
- [x] 项目初始化和目录结构
- [x] 核心框架 (DetectorBase, Registry, Pipeline)
- [x] 配置文件和开发工具配置
- [x] 技术调研文档

### 进行中
- [ ] P0 功能实现：图片质量校验、重复检测、文字识别

### 待开发 (按优先级)

**P0 (本周)**:
- [ ] 图片质量校验 (OpenCV Laplacian + 直方图)
- [ ] 重复图片检测 (MD5 + pHash) - 已有基础
- [ ] 文字识别校验 (PaddleOCR)

**P1 (下周)**:
- [ ] 时间校验 (EXIF + OCR)
- [ ] PS 伪造检测 (ELA + 噪声) - 已有基础
- [ ] 物体识别校验 (CLIP)

**P2 (第 3 周)**:
- [ ] 地点校验 (GPS + OCR)
- [ ] AI 生成检测 (UnivFD)
- [ ] 水印检测

**P3 (后续)**:
- [ ] FAISS 深度特征检索
- [ ] 高级 PS 检测 (多特征融合)

---

## 🧪 测试规范

### Python 测试规范

```python
# tests/conftest.py - 测试配置和 fixtures
import pytest
from ai_check.core import Pipeline

@pytest.fixture
def pipeline():
    """Create pipeline for testing."""
    return Pipeline()

@pytest.fixture
def sample_image():
    """Return path to test image."""
    return "tests/data/sample.jpg"

# tests/unit/test_detector.py
class TestDetector:
    """Detector tests."""

    def test_detect_success(self, pipeline, sample_image):
        """Test successful detection."""
        result = pipeline.run([sample_image])
        assert result is not None
        assert len(result) > 0

    def test_detect_invalid_image(self, pipeline):
        """Test detection with invalid image."""
        with pytest.raises(ValueError):
            pipeline.run(["invalid.jpg"])
```

### 测试文件组织

```
tests/
├── unit/                    # 单元测试
│   ├── test_detector_base.py
│   ├── test_pipeline.py
│   └── test_detectors/
├── integration/             # 集成测试
│   ├── test_full_pipeline.py
│   └── test_database.py
├── system/                  # 系统测试
│   └── test_gui.py
├── conftest.py             # 测试配置
└── data/                   # 测试数据
```

---

## 📚 核心模块说明

### DetectorBase (检测器基类)

所有检测器的抽象基类，定义统一接口：

```python
# ai_check/core/detector_base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class DetectionResult:
    detector_name: str
    detection_type: str
    is_anomaly: bool
    confidence: float
    description: str

class DetectorBase(ABC):
    @abstractmethod
    def _initialize(self) -> bool:
        """初始化检测器（加载模型等）"""
    
    @abstractmethod
    def _detect(self, image_info) -> DetectionResult:
        """执行检测"""
    
    def run(self, image_info) -> DetectionResult:
        """公共入口，不要重写"""
        if not self.initialized:
            self._initialize()
        return self._detect(image_info)
```

### DetectorRegistry (检测器注册表)

插件式注册表，支持装饰器注册：

```python
# ai_check/core/detector_registry.py
class DetectorRegistry:
    _detectors: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(detector_cls):
            cls._detectors[name] = detector_cls
            return detector_cls
        return decorator
    
    @classmethod
    def get_detector(cls, name: str):
        return cls._detectors.get(name)
```

### Pipeline (检测流水线)

协调多个检测器的流水线：

```python
# ai_check/core/pipeline.py
class Pipeline:
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.detectors = []
    
    def add_detector(self, detector: DetectorBase):
        self.detectors.append(detector)
    
    def run(self, images: list) -> list[DetectionResult]:
        """执行检测流水线"""
        results = []
        for image in images:
            for detector in self.detectors:
                result = detector.run(image)
                results.append(result)
        return results
```

---

## 📊 数据库设计

```python
# ai_check/storage/database.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

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

---

## 🔗 相关文档

| 文档 | 用途 |
|------|------|
| [DEVELOPMENT_LOG.md](DEVELOPMENT_LOG.md) | 开发日志（开始任务前必读） |
| [README.md](README.md) | 用户文档 |
| [docs/project-overview.md](docs/project-overview.md) | 项目概述 |
| [docs/architecture/](docs/architecture/) | 架构设计 |
| [docs/guides/development.md](docs/guides/development.md) | 开发指南 |
| [docs/guides/desktop-app-technical-research.md](docs/guides/desktop-app-technical-research.md) | 技术选型报告 |
| [docs/guides/feature-technical-research.md](docs/guides/feature-technical-research.md) | 功能点技术方案 |
| [docs/project-timeline.md](docs/project-timeline.md) | 6 个月开发时间轴 |

---

## ⚠️ 注意事项

1. **敏感配置**: 不要提交 `.env` 文件或包含密钥的配置文件
2. **大文件**: 模型文件 (>100MB) 不要提交到 Git，使用下载链接
3. **开发日志**: 每次开发后必须更新 `DEVELOPMENT_LOG.md`
4. **测试覆盖**: 新功能必须包含单元测试
5. **类型注解**: 所有公共函数必须有类型注解

---

**最后更新**: 2026-05-08
