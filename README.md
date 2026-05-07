# AI Check - 图片AI检查工具

图片AI检查工具，支持伪造检测、重复检测、内容分析等功能，用于替代人工检查。

## 功能特性

- **伪造检测**
  - PS编辑痕迹检测（ELA分析、噪声分析）
  - AI生成图片检测
  - 图片拼接检测
  - 复制粘贴检测

- **重复检测**
  - 精确重复检测（MD5哈希）
  - 相似图片检测（感知哈希、深度特征）

- **文档检测**
  - 文档篡改检测
  - 模板匹配
  - OCR内容提取

- **大规模处理**
  - 支持万级以上图库
  - FAISS向量索引
  - 并行处理

## 快速开始

### 安装依赖

```bash
cd D:\AICheck
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 开发依赖
```

### 运行

```bash
# GUI模式
python -m ai_check.main

# 命令行模式
python -m ai_check.main --no-gui image1.png image2.png
```

### 打包为exe

```bash
pip install pyinstaller
pyinstaller -w -n "AICheck" ai_check/main.py
```

## 项目结构

```
AICheck/
├── ai_check/                 # 主包
│   ├── __init__.py
│   ├── main.py               # 应用入口
│   ├── app/                  # GUI应用
│   │   ├── main_window.py
│   │   └── widgets/
│   ├── core/                 # 核心模块
│   │   ├── detector_base.py     # 检测器基类
│   │   ├── detector_registry.py # 检测器注册表
│   │   ├── pipeline.py          # 检测流水线
│   │   └── task_manager.py      # 任务管理
│   ├── detectors/            # 检测器实现
│   │   ├── forgery/             # 伪造检测
│   │   ├── duplicate/           # 重复检测
│   │   ├── document/            # 文档检测
│   │   └── content/             # 内容检测
│   ├── models/               # 模型管理
│   ├── storage/              # 存储层
│   │   ├── database.py          # SQLite数据库
│   │   ├── cache.py             # 缓存管理
│   │   └── vector_index.py      # 向量索引
│   ├── utils/                # 工具函数
│   └── config/               # 配置管理
├── tests/                    # 测试
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## 扩展开发

### 添加自定义检测器

```python
from ai_check.core import DetectorBase, DetectionResult, DetectionType

@DetectorBase.register("my_detector")
class MyDetector(DetectorBase):
    def __init__(self, name="my_detector", config=None):
        super().__init__(name, DetectionType.CUSTOM, config)

    def _initialize(self):
        # 加载模型等初始化操作
        return True

    def _detect(self, image_info):
        # 执行检测
        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=False,
            confidence=0.0,
            description="检测结果",
        )
```

### 配置流水线

```yaml
# pipeline_config.yaml
enabled_detectors:
  - ps_detector
  - hash_detector
  - my_detector

parallel: true
max_workers: 4
batch_size: 32
```

## 运行测试

```bash
pytest tests/ -v
pytest tests/ --cov=ai_check  # 带覆盖率
```

## 代码规范

```bash
black ai_check/ tests/
isort ai_check/ tests/
mypy ai_check/
ruff check ai_check/
```

## 许可证

MIT License
