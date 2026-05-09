# AI Check - 图片 AI 检查工具

**AI Check** 是一个本地运行的图片 AI 检查桌面应用，支持伪造检测、重复检测、内容分析等功能，旨在替代人工进行图片内容的自动化审核。
---

## ✨ 核心功能

### 🔍 伪造检测
- **PS 编辑检测**: 检测图片是否经过 Photoshop 等工具编辑（ELA 分析、噪声分析）
- **AI 生成检测**: 识别由 Midjourney、Stable Diffusion 等 AI 生成的图片
- **拼接检测**: 发现多张图片拼接合成的痕迹
- **复制粘贴检测**: 检测图片内部复制粘贴的伪造区域

### 🔁 重复检测
- **精确重复**: 基于 MD5 哈希，检测完全相同的图片
- **相似图片**: 基于感知哈希 (pHash) 和深度特征，检测经过编辑的相似图片
- **大规模检索**: 支持万级图库的毫秒级检索（FAISS 向量索引）

### 📄 文档检测
- **文档篡改**: 检测合同、票据、证件等文档的篡改痕迹
- **OCR 识别**: 提取图片中的文字内容（PaddleOCR，中文支持优秀）
- **模板匹配**: 验证文档是否符合预设模板格式

### 📊 质量校验
- **图片质量**: 检测清晰度、过曝、欠曝等质量问题
- **元数据校验**: 验证 EXIF 时间、GPS 地点等信息
- **水印检测**: 识别图片中的文字/图形水印

---

## 🎯 适用场景

| 场景 | 说明 |
|------|------|
| **合同/票据审核** | 验证文档是否被篡改，OCR 提取内容比对 |
| **图库管理** | 检测重复/相似图片，优化存储空间 |
| **内容审核** | 识别 AI 生成图片、违规内容 |
| **证件验证** | 验证身份证、护照等证件真伪 |
| **新闻真实性** | 验证新闻图片是否经过伪造编辑 |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Windows 10/11, Linux, macOS
- 可选：NVIDIA GPU（支持 CUDA 加速）

### 安装依赖

```bash
# 克隆项目
git clone <repository-url>
cd AICheck

# 安装核心依赖
pip install -r requirements.txt

# 开发环境（可选）
pip install -r requirements-dev.txt
```

### 运行应用

```bash
# GUI 模式（推荐）
python -m ai_check.main

# 命令行模式
python -m ai_check.main --no-gui image1.png image2.png

# 指定检测器
python -m ai_check.main --detectors ps_detector,hash_detector images/
```

### 打包为 exe

```bash
# Windows 打包
pip install pyinstaller
pyinstaller -w -n "AI Check" --icon=resources/icon.ico ai_check/main.py

# 生成的 exe 位于 dist/AI Check.exe
```

---

## 📦 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    PyQt6 GUI                            │
│         主窗口 | 检测面板 | 结果查看器 | 设置           │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层                           │
│              Pipeline | TaskManager                     │
├─────────────────────────────────────────────────────────┤
│                    检测器层                             │
│    伪造检测 | 重复检测 | 文档检测 | 内容检测            │
├─────────────────────────────────────────────────────────┤
│                    数据层                               │
│          SQLite 数据库 | FAISS 向量索引 | 缓存          │
└─────────────────────────────────────────────────────────┘
```

### 核心技术栈

| 模块 | 技术 | 说明 |
|------|------|------|
| GUI 框架 | PyQt6 | 跨平台桌面界面 |
| 推理引擎 | ONNX Runtime | CPU/GPU 自适应推理 |
| 图像处理 | OpenCV + Pillow | 图像质量分析、EXIF 读取 |
| OCR | PaddleOCR | 中文文字识别 |
| 向量检索 | FAISS | 大规模图片检索 |
| 数据库 | SQLite | 本地数据存储 |

---

## 📁 项目结构

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
├── requirements.txt          # 运行依赖
├── requirements-dev.txt      # 开发依赖
└── pyproject.toml           # 项目配置
```

---

## 🔧 配置说明

### 检测器配置

编辑 `config/pipeline_config.yaml` 启用/禁用检测器：

```yaml
enabled_detectors:
  - ps_detector       # PS 编辑检测
  - hash_detector     # 哈希重复检测
  - ocr_detector      # OCR 文字识别
  - ai_detector       # AI 生成检测

parallel: true        # 启用并行处理
max_workers: 4        # 最大工作线程
batch_size: 32        # 批处理大小
```

### 硬件加速

软件自动检测硬件并选择最佳推理后端：
- **NVIDIA GPU**: 自动使用 CUDA 加速
- **Intel 核显**: 可使用 OpenVINO 加速（可选）
- **纯 CPU**: 自动降级到 CPU 模式

---

## 📊 检测结果

检测结果支持以下导出格式：

- **Excel**: 包含详细检测数据和统计
- **CSV**: 便于后续数据处理
- **JSON**: 机器可读格式
- **HTML 报告**: 可视化检测报告

---

## 🧪 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 带覆盖率报告
pytest tests/ --cov=ai_check --cov-report=html

# 仅单元测试
pytest tests/unit/ -v

# 仅集成测试
pytest tests/integration/ -v
```

---

## 📝 代码规范

```bash
# 代码格式化
black ai_check/ tests/
isort ai_check/ tests/

# 类型检查
mypy ai_check/

# Linting
ruff check ai_check/

# 一键检查
black . && isort . && mypy . && ruff check . && pytest
```

---

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [项目概述](docs/project-overview.md) | 项目背景、目标、范围 |
| [架构设计](docs/architecture/README.md) | 系统架构设计 |
| [前端架构](docs/architecture/frontend-architecture.md) | GUI 模块设计 |
| [技术调研](docs/guides/desktop-app-technical-research.md) | 技术选型报告 |
| [功能调研](docs/guides/feature-technical-research.md) | 功能点技术方案 |
| [开发指南](docs/guides/development.md) | 开发规范 |
| [时间轴](docs/project-timeline.md) | 6 个月开发计划 |

---
