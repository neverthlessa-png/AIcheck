# 开发指南

本文档为开发者提供完整的开发环境配置、代码规范、测试规范等指导。

---

## 环境配置

### 系统要求

| 要求 | 最低配置 | 推荐配置 |
|------|---------|---------|
| 操作系统 | Windows 10 / Ubuntu 20.04 / macOS 12 | Windows 11 / Ubuntu 22.04 / macOS 14 |
| Python | 3.10 | 3.11+ |
| 内存 | 8GB | 16GB+ |
| 存储 | 10GB | 50GB+ (含模型) |
| GPU | 无 | NVIDIA GPU 8GB+ |

### 安装步骤

#### 1. 克隆仓库

```bash
git clone <repository-url>
cd AICheck
```

#### 2. 创建虚拟环境

```bash
# 使用 venv
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

#### 3. 安装依赖

```bash
# 安装运行依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt
```

#### 4. GPU 支持（可选）

如果有 NVIDIA GPU，可以安装 GPU 版本：

```bash
pip install onnxruntime-gpu
```

验证 GPU 可用：

```python
import onnxruntime as ort
print(ort.get_available_providers())
# 应包含 'CUDAExecutionProvider' 或 'DmlExecutionProvider'
```

#### 5. 安装 Pre-commit 钩子

```bash
pip install pre-commit
pre-commit install
```

这会在每次提交前自动运行代码格式化和检查。

### 验证安装

```bash
# 运行测试
pytest tests/ -v

# 检查导入
python -c "from ai_check.core import Pipeline; print('OK')"

# 启动 GUI
python -m ai_check.main
```

---

## 项目结构

```
AICheck/
├── ai_check/                    # 主程序包
│   ├── __init__.py
│   ├── main.py                  # 应用入口
│   │
│   ├── app/                     # GUI 应用模块
│   │   ├── __init__.py
│   │   ├── main_window.py       # 主窗口类
│   │   ├── widgets/             # UI 组件
│   │   │   ├── detection_panel.py      # 检测面板
│   │   │   ├── result_viewer.py        # 结果查看器
│   │   │   └── settings_dialog.py      # 设置对话框
│   │   └── workers/             # 后台线程
│   │       └── detection_worker.py     # 检测工作线程
│   │
│   ├── core/                    # 核心模块
│   │   ├── __init__.py
│   │   ├── detector_base.py     # 检测器基类
│   │   ├── detector_registry.py # 检测器注册表
│   │   ├── pipeline.py          # 检测流水线
│   │   └── task_manager.py      # 任务管理器
│   │
│   ├── detectors/               # 检测器实现
│   │   ├── __init__.py
│   │   ├── basic/               # 基础校验
│   │   │   ├── quality_checker.py      # 图片质量
│   │   │   ├── time_validator.py       # 时间校验
│   │   │   ├── location_validator.py   # 地点校验
│   │   │   └── watermark_detector.py   # 水印检测
│   │   ├── content/             # 内容校验
│   │   │   ├── object_validator.py     # 物体识别
│   │   │   └── text_validator.py       # 文字识别
│   │   └── advanced/            # 高级校验
│   │       ├── ai_generator_detector.py  # AI 生成检测
│   │       ├── ps_forgery_detector.py    # PS 伪造检测
│   │       └── duplicate_detector.py     # 重复检测
│   │
│   ├── storage/                 # 存储层
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite 数据库
│   │   ├── cache.py             # 缓存管理
│   │   └── vector_index.py      # FAISS 向量索引
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── image_utils.py       # 图像处理
│   │   ├── hardware_utils.py    # 硬件检测
│   │   └── log_utils.py         # 日志配置
│   │
│   └── config/                  # 配置模块
│       ├── __init__.py
│       └── settings.py          # 配置管理
│
├── tests/                       # 测试目录
│   ├── conftest.py
│   ├── unit/                    # 单元测试
│   └── integration/             # 集成测试
│
├── docs/                        # 文档目录
│   ├── project-overview.md      # 项目概述
│   ├── architecture/            # 架构文档
│   ├── guides/                  # 开发指南
│   └── api/                     # API 文档
│
├── config/                      # 配置文件
│   └── default_config.yaml      # 默认配置
│
├── requirements.txt             # 运行依赖
├── requirements-dev.txt         # 开发依赖
├── pyproject.toml               # 项目配置
└── README.md                    # 项目说明
```

---

## 代码规范

### Python 风格

我们遵循 PEP 8 规范，使用以下工具自动格式化：

```bash
# 格式化代码
black ai_check/ tests/

# 排序导入
isort ai_check/ tests/

# 类型检查
mypy ai_check/

# Linting
ruff check ai_check/
```

### 命名约定

| 类型 | 规范 | 示例 |
|------|------|------|
| 模块/包 | snake_case | `image_utils.py`, `ai_check` |
| 类 | PascalCase | `DetectorBase`, `Pipeline` |
| 函数/方法 | snake_case | `compute_hash()`, `detect()` |
| 变量 | snake_case | `image_path`, `result` |
| 常量 | UPPER_SNAKE_CASE | `MAX_BATCH_SIZE` |
| 私有成员 | `_leading_underscore` | `_initialize()` |

### 类型注解

**必须**使用类型注解：

```python
# 正确 ✓
def detect(self, image_info: ImageInfo) -> DetectionResult:
    ...

def process_batch(
    self,
    images: list[ImageInfo],
    parallel: bool = True,
) -> list[PipelineResult]:
    ...

# 错误 ✗
def detect(self, image_info):
    ...
```

### 文档字符串

使用 Google Style 文档格式：

```python
def compute_hash(image: np.ndarray, algorithm: str = "phash") -> str:
    """计算图片的感知哈希。

    Args:
        image: 输入图片，BGR 格式的 numpy 数组。
        algorithm: 哈希算法，可选 "phash"、"dhash"、"ahash"。

    Returns:
        十六进制哈希字符串。

    Raises:
        ValueError: 如果 algorithm 不是支持的算法。

    Example:
        >>> image = cv2.imread("test.jpg")
        >>> hash_value = compute_hash(image, "phash")
        >>> print(hash_value)
        'a1b2c3d4e5f6g7h8'
    """
    ...
```

### 导入顺序

使用 isort 自动排序，顺序为：

1. 标准库
2. 第三方库
3. 本地模块

```python
# 标准库
import os
import sys
from pathlib import Path
from typing import Any, Optional

# 第三方库
import numpy as np
from loguru import logger
from PyQt6.QtWidgets import QWidget

# 本地模块
from ai_check.core import DetectorBase, DetectionResult
from ai_check.utils.image_utils import load_image
```

---

## 测试规范

### 测试组织

```
tests/
├── conftest.py           # 共享 fixtures
├── unit/                 # 单元测试
│   ├── test_detector_base.py
│   ├── test_pipeline.py
│   └── test_detectors/
│       ├── test_quality_checker.py
│       ├── test_duplicate_detector.py
│       └── ...
└── integration/          # 集成测试
    └── test_full_pipeline.py
```

### 测试命名

- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试方法：`test_<scenario>`

```python
class TestQualityChecker:
    """图片质量检测器测试"""

    def test_initialize_success(self):
        """测试初始化成功"""
        ...

    def test_detect_blurry_image(self):
        """测试模糊图片检测"""
        ...

    def test_detect_overexposed_image(self):
        """测试过曝图片检测"""
        ...
```

### 测试结构

使用 Arrange-Act-Assert 模式：

```python
def test_detection_result(self):
    # Arrange - 准备测试数据
    detector = QualityChecker()
    image = create_test_image()

    # Act - 执行测试操作
    result = detector.detect(image)

    # Assert - 验证结果
    assert result.is_anomaly is False
    assert result.confidence >= 0.0
```

### Fixtures

```python
# tests/conftest.py
import pytest
import numpy as np
import cv2

@pytest.fixture
def sample_image():
    """创建测试图片"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    yield image

@pytest.fixture
def temp_dir():
    """创建临时目录"""
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

# test_xxx.py
def test_save_image(sample_image, temp_dir):
    path = temp_dir / "test.png"
    cv2.imwrite(str(path), sample_image)
    assert path.exists()
```

### 参数化测试

```python
import pytest

@pytest.mark.parametrize("hash_type,expected", [
    ("phash", True),
    ("dhash", True),
    ("ahash", True),
    ("invalid", False),
])
def test_hash_types(hash_type, expected):
    detector = HashDetector(config={"hash_type": hash_type})
    assert detector.initialize() == expected
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_core.py

# 运行特定测试
pytest tests/test_quality.py::TestQualityChecker::test_detect_blurry

# 运行带覆盖率的测试
pytest --cov=ai_check --cov-report=html

# 显示打印输出
pytest -s

# 详细输出
pytest -v
```

---

## 调试技巧

### 日志配置

```python
from loguru import logger

# 设置日志级别
import sys
logger.remove()
logger.add(sys.stderr, level="DEBUG")

# 记录调试信息
logger.debug("Processing image: {}", image_path)
logger.info("Detection result: {}", result)
```

### 断点调试

```python
# Python 3.7+
breakpoint()

# 或
import pdb; pdb.set_trace()
```

### 性能分析

```python
import cProfile

cProfile.run('pipeline.process_batch(images)', sort='cumtime')
```

---

## Git 工作流

### 分支策略

```
main (主分支，稳定版本)
  │
  ├── develop (开发分支)
  │     │
  │     ├── feature/quality-detector
  │     ├── feature/duplicate-detector
  │     └── fix/memory-leak
  │
  └── release/v0.2.0
```

### 工作流程

1. 从 `develop` 创建 feature 分支
2. 开发并测试
3. 提交 PR 到 `develop`
4. 代码审查通过后合并
5. 定期从 `develop` 发布 release

### 常用命令

```bash
# 创建并切换分支
git checkout -b feature/my-feature

# 查看状态
git status

# 暂存更改
git add .
git add -p  # 交互式暂存

# 提交（遵循 Conventional Commits 规范）
git commit -m "feat: add quality checker detector"

# 推送
git push origin feature/my-feature

# 拉取最新代码
git pull origin develop --rebase
```

### 提交信息规范

采用 Conventional Commits 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Type 类型**:
| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(detectors): add quality checker` |
| `fix` | Bug 修复 | `fix(core): resolve null pointer in pipeline` |
| `docs` | 文档更新 | `docs(readme): update installation guide` |
| `style` | 代码格式 | `style: format code with black` |
| `refactor` | 重构 | `refactor(models): simplify detector interface` |
| `test` | 测试 | `test(forgery): add unit tests for PS detector` |
| `chore` | 构建/工具 | `chore(deps): update dependencies` |
| `perf` | 性能优化 | `perf(query): optimize database query` |
| `ci` | CI 配置 | `ci: add GitHub Actions workflow` |

---

## 常见问题

### Q: 导入错误 "ModuleNotFoundError: No module named 'ai_check'"

A: 确保在项目根目录运行，或安装包：
```bash
pip install -e .
```

### Q: PyQt6 安装失败

A: 尝试使用 conda 安装：
```bash
conda install pyqt
```

### Q: CUDA 不可用

A: 检查 CUDA 和 cuDNN 版本，重新安装 onnxruntime-gpu：
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

### Q: PaddleOCR 下载模型失败

A: 手动下载模型或使用镜像源：
```bash
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple paddleocr
```

---

## 相关文档

- [架构设计](../architecture/README.md)
- [检测器实现指南](detectors-implementation-guide.md)
- [开发日志规则](development-log-guide.md)

---

**最后更新**: 2026-05-08
