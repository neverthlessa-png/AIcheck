# 项目概述

## 项目简介

**AI Check** 是一个本地运行的图片 AI 检查桌面应用，支持伪造检测、重复检测、内容分析等功能，旨在替代人工进行图片内容的自动化审核。

### 核心定位

| 项目 | 说明 |
|------|------|
| **目标用户** | 个人专业用户（摄影师、设计师、自媒体） |
| **处理规模** | 重量级 (>1000 张/次) |
| **数据存储** | SQLite 本地数据库 |
| **运行环境** | 完全离线，CPU + 可选 GPU 自适应 |
| **发布方式** | 单机版 exe 打包 |

---

## 功能模块总览

```
点检功能
├── 基础校验
│   ├── watermark_detector    图片标签/水印检测
│   ├── time_validator       时间校验（EXIF + OCR）
│   ├── location_validator    地点校验（GPS + 地名识别）
│   └── quality_checker      图片质量校验（清晰度、过曝等）
│
├── 内容校验
│   ├── object_validator     物体识别校验（CLIP）
│   └── text_validator       文字识别校验（PaddleOCR）
│
└── 高级校验
    ├── ai_generator_detector    AI 生成图片检测（UnivFD）
    ├── ps_forgery_detector       PS 伪造检测（ELA + 噪声分析）
    └── duplicate_detector       重复图片检测（MD5 + pHash + FAISS）
```

### 基础校验模块

| 检测器 | 功能 | 技术方案 |
|--------|------|----------|
| `watermark_detector` | 检测图片水印/标签 | PaddleOCR + 模板匹配 |
| `time_validator` | 验证图片时间信息 | EXIF 提取 + OCR 识别 + 规则验证 |
| `location_validator` | 验证图片地点信息 | GPS 提取 + 距离计算 + OCR 地名 |
| `quality_checker` | 检测图片质量问题 | Laplacian 方差 + 直方图分析 |

### 内容校验模块

| 检测器 | 功能 | 技术方案 |
|--------|------|----------|
| `object_validator` | 验证图片物体与描述相符 | CLIP 零样本分类 |
| `text_validator` | 验证图片文字与描述相符 | PaddleOCR + 相似度比对 |

### 高级校验模块

| 检测器 | 功能 | 技术方案 |
|--------|------|----------|
| `ai_generator_detector` | 检测 AI 生成图片 | UnivFD 预训练模型 + 频域分析 |
| `ps_forgery_detector` | 检测 PS 伪造痕迹 | ELA 分析 + 噪声一致性 + 元数据 |
| `duplicate_detector` | 检测重复/相似图片 | MD5 + pHash + FAISS |

---

## 技术架构

### 核心技术栈

| 模块 | 技术选型 | 理由 |
|------|------|------|
| GUI 框架 | PyQt6 | 组件丰富、文档完善、支持复杂界面 |
| 推理引擎 | ONNX Runtime | CPU/GPU 自适应、性能优秀 |
| 数据库 | SQLite + SQLAlchemy | 零配置、单文件、适合本地应用 |
| 向量检索 | FAISS | Facebook 出品、支持百万级高效检索 |
| OCR | PaddleOCR | 中文支持最好、速度快、准确率高 |
| 图像处理 | OpenCV + Pillow | 功能全面、性能优秀 |
| 打包工具 | PyInstaller | 成熟稳定、支持单文件 exe |

### 系统架构分层

```
┌─────────────────────────────────────────────────────────┐
│                    PyQt6 GUI                            │
│         主窗口 | 检测面板 | 结果查看器 | 设置           │
├─────────────────────────────────────────────────────────┤
│                    业务逻辑层                           │
│              Pipeline | TaskManager                     │
├─────────────────────────────────────────────────────────┤
│                    检测器层                             │
│    基础校验 | 内容校验 | 高级校验 | 可扩展自定义检测器   │
├─────────────────────────────────────────────────────────┤
│                    数据层                               │
│          SQLite 数据库 | FAISS 向量索引 | 缓存          │
└─────────────────────────────────────────────────────────┘
```

---

## 开发优先级

### P0（本周）

| 检测器 | 预计工时 | 依赖 |
|--------|----------|------|
| `quality_checker` | 4h | OpenCV |
| `duplicate_detector` | 8h | imagehash（已有基础） |
| `text_validator` | 8h | PaddleOCR |

### P1（下周）

| 检测器 | 预计工时 | 依赖 |
|--------|----------|------|
| `time_validator` | 4h | Pillow, dateutil |
| `ps_forgery_detector` | 8h | OpenCV（已有基础） |
| `object_validator` | 12h | transformers (CLIP) |

### P2（第 3 周）

| 检测器 | 预计工时 | 依赖 |
|--------|----------|------|
| `watermark_detector` | 8h | PaddleOCR |
| `location_validator` | 8h | geopy, Pillow |
| `ai_generator_detector` | 16h | torch, torchvision |

### P3（后续）

| 检测器 | 预计工时 | 依赖 |
|--------|----------|------|
| FAISS 深度检索 | 12h | FAISS |
| 高级 PS 检测 | 16h | 多种算法融合 |

---

## 项目背景

### 业务需求

在日常运营中，存在大量需要人工审核的图片内容：

1. **合同/票据审核**: 验证文档是否被篡改
2. **图库管理**: 检测重复或相似图片，优化存储
3. **内容审核**: 检测违规内容、AI 生成图片
4. **证件验证**: 验证身份证、护照等证件真伪

### 目标用户

- 个人专业用户（摄影师、设计师、自媒体）
- 企业内部审核团队
- 内容创作者和版权管理者

---

## 项目目标

### 短期目标 (v0.1.0)

- [ ] 完成 P0 优先级检测器
- [ ] 完善 GUI 界面
- [ ] 支持批量处理

### 中期目标 (v0.2.0)

- [ ] 完成 P1/P2 优先级检测器
- [ ] 实现人工复核工作流
- [ ] 完善报告导出功能

### 长期目标 (v1.0.0)

- [ ] 所有检测器开发完成
- [ ] 优化大规模处理性能
- [ ] 支持插件扩展机制

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 用户文档 |
| [架构设计](architecture/README.md) | 系统架构 |
| [前端架构](architecture/frontend-architecture.md) | GUI 模块设计 |
| [技术调研](guides/desktop-app-technical-research.md) | 技术选型报告 |
| [功能调研](guides/feature-technical-research.md) | 功能点技术方案 |
| [检测器实现指南](guides/detectors-implementation-guide.md) | 检测器详细实现 |
| [开发指南](guides/development.md) | 开发规范 |
| [时间轴](project-timeline.md) | 6 个月开发计划 |

---

**最后更新**: 2026-05-08
