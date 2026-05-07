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
git clone https://github.com/your-org/ai-check.git
cd ai-check
```

#### 2. 创建虚拟环境

```bash
# 使用venv
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 或使用conda
conda create -n ai-check python=3.11
conda activate ai-check
```

#### 3. 安装依赖

```bash
# 安装运行依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt

# 或使用pip可编辑安装
pip install -e ".[dev]"
```

#### 4. GPU支持（可选）

如果有NVIDIA GPU，可以安装GPU版本：

```bash
pip install onnxruntime-gpu
```

验证GPU可用：

```python
import onnxruntime as ort
print(ort.get_available_providers())
# 应包含 'CUDAExecutionProvider'
```

#### 5. 安装Pre-commit钩子

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

# 启动GUI（需要PyQt6）
python -m ai_check.main
```

---

## 项目结构

```
AICheck/
├── ai_check/                    # 主包
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # 应用入口
│   │
│   ├── app/                     # GUI应用模块
│   │   ├── __init__.py
│   │   ├── main_window.py       # 主窗口类
│   │   ├── widgets/             # UI组件
│   │   │   ├── __init__.py
│   │   │   ├── main_window_widget.py   # 主窗口组件
│   │   │   ├── detection_panel.py      # 检测面板
│   │   │   ├── result_viewer.py        # 结果查看器
│   │   │   └── settings_dialog.py      # 设置对话框
│   │   └── resources/           # UI资源（图标、样式）
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
│   │   ├── forgery/             # 伪造检测
│   │   │   ├── __init__.py
│   │   │   ├── ps_detector.py        # PS编辑检测
│   │   │   ├── ai_generated_detector.py  # AI生成检测
│   │   │   ├── splice_detector.py   # 拼接检测
│   │   │   └── copy_move_detector.py    # 复制粘贴检测
│   │   ├── duplicate/           # 重复检测
│   │   │   ├── __init__.py
│   │   │   ├── hash_detector.py     # 哈希检测
│   │   │   └── similarity_detector.py   # 相似检测
│   │   ├── document/            # 文档检测
│   │   │   ├── __init__.py
│   │   │   ├── template_matcher.py  # 模板匹配
│   │   │   └── ocr_analyzer.py      # OCR分析
│   │   └── content/             # 内容检测
│   │       ├── __init__.py
│   │       └── ocr_extractor.py     # OCR提取
│   │
│   ├── models/                  # 模型管理
│   │   ├── __init__.py
│   │   ├── model_manager.py     # 模型管理器
│   │   ├── model_downloader.py  # 模型下载
│   │   └── config.yaml          # 模型配置
│   │
│   ├── storage/                 # 存储层
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite数据库
│   │   ├── cache.py             # 缓存管理
│   │   └── vector_index.py      # 向量索引
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── image_utils.py       # 图像处理
│   │   ├── hardware_utils.py    # 硬件检测
│   │   └── log_utils.py         # 日志配置
│   │
│   └── config/                  # 配置模块
│       ├── __init__.py
│       ├── settings.py          # 配置管理
│       └── default_config.yaml  # 默认配置
│
├── tests/                       # 测试目录
│   ├── conftest.py              # pytest配置
│   ├── test_core.py             # 核心模块测试
│   ├── test_utils.py            # 工具函数测试
│   ├── unit/                    # 单元测试
│   └── integration/             # 集成测试
│
├── docs/                        # 文档目录
│   ├── project-overview.md      # 项目概述
│   ├── architecture/            # 架构文档
│   ├── guides/                  # 开发指南
│   ├── api/                     # API文档
│   └── deployment/              # 部署文档
│
├── scripts/                     # 脚本目录
│   ├── download_models.py       # 下载模型
│   └── build.py                 # 构建脚本
│
├── requirements.txt             # 运行依赖
├── requirements-dev.txt         # 开发依赖
├── pyproject.toml               # 项目配置
├── README.md                    # 项目说明
├── CONTRIBUTING.md              # 贡献指南
└── LICENSE                      # 许可证
```

---

## 代码规范

### Python风格

我们遵循PEP 8规范，使用以下工具自动格式化：

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
| 模块 | snake_case | `image_utils.py` |
| 包 | snake_case | `ai_check` |
| 类 | PascalCase | `DetectorBase` |
| 函数 | snake_case | `compute_hash()` |
| 方法 | snake_case | `detect()` |
| 变量 | snake_case | `image_path` |
| 常量 | UPPER_SNAKE_CASE | `MAX_BATCH_SIZE` |
| 私有成员 | _leading_underscore | `_initialize()` |
| 保护成员 | _single_leading | `_config` |

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

使用Google Style文档格式：

```python
def compute_hash(image: np.ndarray, algorithm: str = "phash") -> str:
    """计算图片的感知哈希。

    Args:
        image: 输入图片，BGR格式的numpy数组。
        algorithm: 哈希算法，可选 "phash"、"dhash"、"ahash"。

    Returns:
        十六进制哈希字符串。

    Raises:
        ValueError: 如果algorithm不是支持的算法。

    Example:
        >>> image = cv2.imread("test.jpg")
        >>> hash_value = compute_hash(image, "phash")
        >>> print(hash_value)
        'a1b2c3d4e5f6g7h8'
    """
    ...
```

### 导入顺序

使用isort自动排序，顺序为：

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

### 注释规范

- 代码应该自文档化，避免显而易见的注释
- 注释解释"为什么"而不是"是什么"
- 使用TODO、FIXME、NOTE标记：

```python
# TODO: 实现GPU加速
# FIXME: 处理空图片的情况
# NOTE: 这个算法在图片较小时效果不好
```

---

## 测试规范

### 测试组织

```
tests/
├── conftest.py           # 共享fixtures
├── test_core.py          # 核心模块测试
├── test_utils.py         # 工具函数测试
├── unit/                 # 单元测试
│   ├── test_detector_base.py
│   └── test_pipeline.py
└── integration/          # 集成测试
    └── test_full_pipeline.py
```

### 测试命名

- 测试文件：`test_<module_name>.py`
- 测试类：`Test<ClassName>`
- 测试方法：`test_<scenario>`

```python
class TestPSDetector:
    """PS检测器测试"""

    def test_initialize_success(self):
        """测试初始化成功"""
        ...

    def test_detect_no_forgery(self):
        """测试无伪造图片的检测"""
        ...

    def test_detect_with_forgery(self):
        """测试有伪造图片的检测"""
        ...
```

### 测试结构

使用Arrange-Act-Assert模式：

```python
def test_detection_result(self):
    # Arrange - 准备测试数据
    detector = PSDetector()
    image = create_test_image()

    # Act - 执行测试操作
    result = detector.detect(image)

    # Assert - 验证结果
    assert result.is_anomaly is False
    assert result.confidence >= 0.0
```

### Fixtures

使用pytest fixtures共享测试数据：

```python
# conftest.py
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
pytest tests/test_core.py::TestDetectorBase::test_detection_type_enum

# 运行带标记的测试
pytest -m "not slow"

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

使用IDE断点或：

```python
import pdb; pdb.set_trace()
# 或 Python 3.7+
breakpoint()
```

### 性能分析

```python
import cProfile

cProfile.run('pipeline.process_batch(images)', sort='cumtime')
```

---

## Git工作流

### 分支策略

```
main (主分支，稳定版本)
  │
  ├── develop (开发分支)
  │     │
  │     ├── feature/new-detector
  │     ├── feature/gui-improvement
  │     └── fix/memory-leak
  │
  └── release/v0.2.0
```

### 工作流程

1. 从develop创建feature分支
2. 开发并测试
3. 提交PR到develop
4. 代码审查通过后合并
5. 定期从develop发布release

### 常用命令

```bash
# 创建并切换分支
git checkout -b feature/my-feature

# 查看状态
git status

# 暂存更改
git add .
git add -p  # 交互式暂存

# 提交
git commit -m "feat: add new feature"

# 推送
git push origin feature/my-feature

# 拉取最新代码
git pull origin develop --rebase

# 解决冲突后
git add .
git rebase --continue
```

---

## 常见问题

### Q: 导入错误 "ModuleNotFoundError: No module named 'ai_check'"

A: 确保在项目根目录运行，或安装包：
```bash
pip install -e .
```

### Q: PyQt6安装失败

A: 尝试使用conda安装：
```bash
conda install pyqt
```

### Q: CUDA不可用

A: 检查CUDA和cuDNN版本，重新安装onnxruntime-gpu：
```bash
pip uninstall onnxruntime
pip install onnxruntime-gpu
```

### Q: 测试失败 "fixture 'xxx' not found"

A: 确保conftest.py在正确位置，或导入fixtures：
```python
pytest_plugins = ['conftest']
```

---

## 相关文档

- [贡献指南](../../CONTRIBUTING.md)
- [架构设计](../architecture/README.md)
- [API文档](../api/README.md)
