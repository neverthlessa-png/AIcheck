# AI Check 项目开发时间轴

## 项目概述

- **项目周期**: 6 个月（24 周）
- **起点**: 从零开始
- **目标**: 完成可用的图片 AI 检查桌面应用
- **团队**: 1-2 名全职开发者

---

## 阶段总览

```
月 1          月 2          月 3          月 4          月 5          月 6
│────────────│────────────│────────────│────────────│────────────│────────────│
│  阶段 1     │  阶段 2     │  阶段 3     │  阶段 4     │  阶段 5     │  阶段 6     │
│  基础搭建   │  核心开发   │  核心开发   │  GUI 开发    │  集成优化   │  测试发布   │
│  W1-W4     │  W5-W8     │  W9-W12    │  W13-W16   │  W17-W20   │  W21-W24   │
│────────────│────────────│────────────│────────────│────────────│────────────│
              │                         │                         │
              ● 里程碑 1                  ● 里程碑 2                 ● 里程碑 3
              核心框架完成                GUI 完成                   发布候选
```

---

## 阶段 1：基础搭建（第 1-4 周）

### 目标
完成项目基础架构和开发环境配置

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W1** | 项目初始化 | | ✅ 完成 |
| | - 创建项目目录结构 | 完整目录树 | ✅ |
| | - 配置依赖管理 | requirements.txt, pyproject.toml | ✅ |
| | - 配置开发工具 | black, isort, mypy, ruff | ✅ |
| | - 搭建 Git 仓库 | Git 仓库 | ✅ |
| | - 编写项目文档框架 | README, CONTRIBUTING | ✅ |
| | - 技术调研 | 技术选型报告 | ✅ |
| **W2** | 核心模块 - 检测器框架 | | ✅ 完成 |
| | - DetectorBase 抽象基类 | detector_base.py | ✅ |
| | - DetectionResult 数据类 | detector_base.py | ✅ |
| | - DetectorRegistry 注册表 | detector_registry.py | ✅ |
| | - ImageInfo 数据类 | detector_base.py | ✅ |
| | - 单元测试 | test_core.py | ✅ |
| **W3** | 核心模块 - 流水线 | | ✅ 完成 |
| | - Pipeline 类实现 | pipeline.py | ✅ |
| | - PipelineConfig 配置类 | pipeline.py | ✅ |
| | - 批处理逻辑 | pipeline.py | ✅ |
| | - 并行处理支持 | pipeline.py | ✅ |
| | - 单元测试 | test_pipeline.py | ✅ |
| **W4** | 基础设施模块 | | ✅ 完成 |
| | - 配置管理 | config/settings.py | ✅ |
| | - 日志系统 | utils/log_utils.py | ✅ |
| | - 硬件检测 | utils/hardware_utils.py | ✅ |
| | - 数据库设计 | storage/database.py | ✅ |
| | - 缓存管理 | storage/cache.py | ✅ |

### 里程碑 1 检查点（W4 结束）
- [x] 项目目录结构完整
- [x] 检测器框架可运行
- [x] 流水线可处理图片
- [x] 技术调研文档完成

---

## 阶段 2：核心检测器开发（上）（第 5-8 周）

### 目标
完成基础校验和内容校验检测器实现

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W5** | P0: 图片质量校验 | | 🔄 进行中 |
| | - QualityChecker 实现 | detectors/basic/quality_checker.py | 🔄 |
| | - 清晰度检测（Laplacian） | quality_checker.py | 🔄 |
| | - 过曝/欠曝检测（直方图） | quality_checker.py | 🔄 |
| | - 单元测试 | test_quality.py | 🔄 |
| **W6** | P0: 重复图片检测 + 文字识别 | | 📋 待开始 |
| | - DuplicateDetector 实现 | detectors/advanced/duplicate_detector.py | 📋 |
| | - MD5 + pHash 检测 | duplicate_detector.py | 📋 |
| | - TextValidator 实现 | detectors/content/text_validator.py | 📋 |
| | - PaddleOCR 集成 | text_validator.py | 📋 |
| **W7** | P1: 时间校验 + PS 伪造检测 | | 📋 待开始 |
| | - TimeValidator 实现 | detectors/basic/time_validator.py | 📋 |
| | - EXIF 时间提取 | time_validator.py | 📋 |
| | - PSForgeryDetector 实现 | detectors/advanced/ps_forgery_detector.py | 📋 |
| | - ELA 分析算法 | ps_forgery_detector.py | 📋 |
| **W8** | P1: 物体识别校验 | | 📋 待开始 |
| | - ObjectValidator 实现 | detectors/content/object_validator.py | 📋 |
| | - CLIP 模型集成 | object_validator.py | 📋 |
| | - 单元测试 | test_content.py | 📋 |

### 里程碑 2 检查点（W8 结束）
- [ ] P0 检测器完成（质量、重复、文字）
- [ ] P1 检测器完成（时间、PS、物体）
- [ ] 单元测试覆盖率 > 70%

---

## 阶段 3：核心检测器开发（下）（第 9-12 周）

### 目标
完成高级校验检测器和数据管理

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W9** | P2: 水印检测 + 地点校验 | | 📋 待开始 |
| | - WatermarkDetector 实现 | detectors/basic/watermark_detector.py | 📋 |
| | - PaddleOCR 水印识别 | watermark_detector.py | 📋 |
| | - LocationValidator 实现 | detectors/basic/location_validator.py | 📋 |
| | - GPS 提取 + 距离计算 | location_validator.py | 📋 |
| **W10** | P2: AI 生成图片检测 | | 📋 待开始 |
| | - AIGeneratedDetector 实现 | detectors/advanced/ai_generator_detector.py | 📋 |
| | - UnivFD 模型集成 | ai_generator_detector.py | 📋 |
| | - 频域分析补充 | ai_generator_detector.py | 📋 |
| **W11** | 向量索引模块 | | 📋 待开始 |
| | - FAISS 集成 | storage/vector_index.py | 📋 |
| | - 特征向量存储 | vector_index.py | 📋 |
| | - 相似度检索 | vector_index.py | 📋 |
| **W12** | 任务管理模块 + 缓冲 | | 📋 待开始 |
| | - TaskManager 实现 | core/task_manager.py | 📋 |
| | - 任务状态管理 | task_manager.py | 📋 |
| | - 暂停/恢复/取消 | task_manager.py | 📋 |
| | - 缓冲周（机动时间） | | 📋 |

### 里程碑 3 检查点（W12 结束）
- [ ] 所有检测器实现完成
- [ ] 向量索引支持万级图片
- [ ] 任务管理支持暂停恢复
- [ ] 单元测试覆盖率 > 75%

---

## 阶段 4：GUI 开发（第 13-16 周）

### 目标
完成 PyQt6 图形界面

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W13** | GUI 框架搭建 | | 📋 待开始 |
| | - MainWindow 主窗口 | app/main_window.py | 📋 |
| | - 菜单栏/工具栏 | main_window.py | 📋 |
| | - Tab 页签切换 | main_window.py | 📋 |
| | - 样式表 (QSS) | app/resources/style.qss | 📋 |
| **W14** | 检测面板 | | 📋 待开始 |
| | - DetectionPanel | app/widgets/detection_panel.py | 📋 |
| | - 图片列表组件 | detection_panel.py | 📋 |
| | - 检测器配置组件 | detection_panel.py | 📋 |
| | - 进度显示 | detection_panel.py | 📋 |
| **W15** | 后台工作线程 | | 📋 待开始 |
| | - DetectionWorker (QThread) | app/workers/detection_worker.py | 📋 |
| | - 信号槽连接 | detection_worker.py | 📋 |
| | - 进度回调 | detection_worker.py | 📋 |
| | - 取消/暂停处理 | detection_worker.py | 📋 |
| **W16** | 结果查看器和设置 | | 📋 待开始 |
| | - ResultViewer | app/widgets/result_viewer.py | 📋 |
| | - 结果表格/详情 | result_viewer.py | 📋 |
| | - SettingsPanel | app/widgets/settings_dialog.py | 📋 |
| | - 导出报告功能 | result_viewer.py | 📋 |

### 里程碑 4 检查点（W16 结束）
- [ ] GUI 可正常运行
- [ ] 检测流程可执行
- [ ] 结果可查看和导出
- [ ] 设置可保存

---

## 阶段 5：集成与优化（第 17-20 周）

### 目标
完成模块集成和性能优化

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W17** | 模块集成测试 | | 📋 待开始 |
| | - 端到端测试 | tests/integration/test_full_pipeline.py | 📋 |
| | - Bug 修复 | 各类修复 | 📋 |
| | - 性能分析 | 性能分析报告 | 📋 |
| **W18** | 性能优化 | | 📋 待开始 |
| | - 批处理优化 | core/pipeline.py | 📋 |
| | - 内存管理优化 | utils/image_utils.py | 📋 |
| | - GPU 加速 | core/pipeline.py | 📋 |
| | - 性能测试报告 | docs/performance-report.md | 📋 |
| **W19** | 数据管理增强 | | 📋 待开始 |
| | - 批量导入 | app/widgets/batch_import.py | 📋 |
| | - 数据备份 | storage/backup.py | 📋 |
| | - 数据清理 | storage/cleanup.py | 📋 |
| **W20** | 报表中心 | | 📋 待开始 |
| | - 报表查询 | app/widgets/report_center.py | 📋 |
| | - 统计图表 | app/widgets/chart_widget.py | 📋 |
| | - Excel 导出 | app/widgets/report_center.py | 📋 |

### 里程碑 5 检查点（W20 结束）
- [ ] 端到端测试通过
- [ ] 性能满足要求（1000 张/小时）
- [ ] 数据管理功能完整
- [ ] 报表可正常导出

---

## 阶段 6：测试与发布（第 21-24 周）

### 目标
完成测试、文档和发布

### 周计划

| 周次 | 任务 | 交付物 | 状态 |
|------|------|--------|------|
| **W21** | 系统测试 | | 📋 待开始 |
| | - 功能测试 | tests/system/ | 📋 |
| | - 兼容性测试 | 测试报告 | 📋 |
| | - Bug 修复 | 各类修复 | 📋 |
| **W22** | 用户测试 | | 📋 待开始 |
| | - 内部用户测试 | 反馈收集 | 📋 |
| | - 问题修复 | 各类修复 | 📋 |
| | - 用户体验优化 | UI 优化 | 📋 |
| **W23** | 文档完善 | | 📋 待开始 |
| | - 用户手册 | docs/user-guide.md | 📋 |
| | - API 文档 | docs/api/ | 📋 |
| | - 部署文档 | docs/deployment/ | 📋 |
| | - 更新日志 | CHANGELOG.md | 📋 |
| **W24** | 打包发布 | | 📋 待开始 |
| | - PyInstaller 打包 | pyinstaller 配置 | 📋 |
| | - 安装包制作 | 安装包 | 📋 |
| | - 发布准备 | 发布说明 | 📋 |
| | - v1.0.0 发布 | GitHub Release | 📋 |

### 里程碑 6 检查点（W24 结束）
- [ ] 所有测试通过
- [ ] 文档完整
- [ ] 安装包可用
- [ ] v1.0.0 发布

---

## 关键路径

```
W1-2 项目初始化 ──→ W3-4 核心框架 ──→ W5-8 检测器 (上) ──→ W9-12 检测器 (下)
                                                  │
                                                  ↓
W21-24 发布 ←── W19-20 集成优化 ←── W13-16 GUI 开发 ←─────────┘
```

---

## 风险与应对

| 风险 | 概率 | 影响 | 应对措施 |
|------|------|------|----------|
| 技术难点（AI 模型） | 中 | 高 | 使用预训练模型，降低自研风险 |
| 人员变动 | 低 | 高 | 保持文档更新，知识共享 |
| 需求变更 | 中 | 中 | 保持架构可扩展性 |
| 性能不达标 | 中 | 中 | 提前性能测试，预留优化时间 |
| GPU 资源不足 | 高 | 低 | 优先支持 CPU，GPU 为可选 |

---

## 缓冲时间

在以下节点预留缓冲时间：
- W12 结束：预留 1 周缓冲（核心功能完成）
- W16 结束：预留 1 周缓冲（GUI 完成）
- W20 结束：预留 1 周缓冲（集成完成）

**实际可用时间**: 24 周 + 3 周缓冲 = 27 周（约 6.5 个月）

---

## 当前状态

**当前周次**: W5 (2026-05-08)
**当前阶段**: 阶段 2 - 核心检测器开发（上）
**本周任务**: P0 图片质量校验器实现

### 本周待办
- [ ] 实现 QualityChecker 检测器
- [ ] 实现清晰度检测（Laplacian 方差）
- [ ] 实现过曝/欠曝检测（直方图分析）
- [ ] 编写单元测试

---

**最后更新**: 2026-05-08
