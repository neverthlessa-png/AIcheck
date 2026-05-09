# 开发日志 (Development Log)

记录 AI Check 项目的开发过程，包括时间、作者、新增或修改的内容等。

---

## 使用说明

### 记录格式

```markdown
## YYYY-MM-DD - [作者]

### 类型
- ✨ 新增 (Feature)
- 🐛 修复 (Bugfix)
- 📝 文档 (Documentation)
- ♻️ 重构 (Refactoring)
- 🎨 样式 (Style)
- ⚡ 性能 (Performance)
- 🔧 配置 (Configuration)
- 🧪 测试 (Test)

### 变更内容
- 模块/文件：具体变更描述

### 备注
- 可选的补充说明
```

### 提交前

1. 阅读本日志，了解最近的开发内容
2. 确认没有冲突的修改
3. 在本日志末尾添加你的开发记录

### 提交后

1. 更新本日志
2. 如有重大变更，同步更新 `CHANGELOG.md`

---

## 开发记录

### 2024-05-07 - [初始开发团队]

#### 类型
- ✨ 新增
- 📝 文档

#### 变更内容
- **项目结构**: 创建完整的项目目录结构
  - `ai_check/` - 主程序包
  - `core/` - 核心模块（检测器基类、注册表、流水线、任务管理）
  - `detectors/` - 检测器实现（伪造、重复、文档、内容）
  - `app/` - GUI 应用（主窗口、组件）
  - `storage/` - 存储层（数据库、缓存、向量索引）
  - `utils/` - 工具函数
  - `config/` - 配置管理
  - `tests/` - 测试代码
  - `docs/` - 文档

- **核心框架**: 
  - `core/detector_base.py` - 检测器抽象基类
  - `core/detector_registry.py` - 检测器注册表（插件机制）
  - `core/pipeline.py` - 检测流水线
  - `core/task_manager.py` - 任务管理器

- **配置**:
  - `requirements.txt` - 运行依赖
  - `requirements-dev.txt` - 开发依赖
  - `pyproject.toml` - 项目配置
  - `.pre-commit-config.yaml` - Pre-commit 钩子
  - `config/default_config.yaml` - 默认配置

- **Skills/Rules**:
  - `.claude/skills/` - 自定义技能（code-review, test-gen, doc-gen, pyqt-helper, pyinstaller-build）
  - `.rules/` - 开发规则（python-style, git-commit, testing, project-rules）

- **文档**:
  - `README.md` - 项目说明
  - `CONTRIBUTING.md` - 贡献指南
  - `docs/project-overview.md` - 项目概述
  - `docs/architecture/README.md` - 架构设计
  - `docs/architecture/frontend-architecture.md` - 前端架构
  - `docs/guides/development.md` - 开发指南
  - `docs/project-timeline.md` - 6 个月开发时间轴

#### 备注
- 项目初始化完成，基础框架已搭建
- 下一步：实现具体检测器功能

---

## 开发记录

### 2026-05-08 - [AI Assistant]

#### 类型
- 📝 文档
- ♻️ 重构

#### 变更内容

**文档重构**:
- `README.md`: 重写为用户导向的软件介绍文档

- `CLAUDE.md`: 重写为开发者/AI 导向的开发指南

**技术调研文档**:
- `docs/guides/desktop-app-technical-research.md`: 桌面软件技术方案调研
  - 需求概述（用户定位、核心需求）
  - 技术选型总览（GUI 框架、推理引擎、数据库、向量检索等）
  - 详细技术调研（7 个核心模块的方案对比）
  - 性能优化策略（批量处理、内存管理、GPU 加速）
  - 准确率控制策略（多模型融合、阈值可调、人工复核）
  - 完整依赖清单和风险应对

- `docs/guides/detectors-implementation-guide.md`: 9 个检测器实现指南
  - 基础校验模块（4 个）：水印检测、时间校验、地点校验、质量校验
  - 内容校验模块（2 个）：物体识别、文字识别
  - 高级校验模块（3 个）：AI 生成检测、PS 伪造检测、重复图片检测
  - 每个检测器包含：技术方案对比、完整代码示例、依赖配置
  - 检测器注册与使用示例
  - 性能优化建议

#### 备注
- 确认用户需求：个人专业用户、重量级处理 (>1000 张/次)、SQLite 本地存储、完全离线运行、CPU+GPU 自适应
- 技术选型确认：PyQt6 + ONNX Runtime + SQLite + FAISS + PaddleOCR

### 2026-05-08 - [AI Assistant] (文档维护)

#### 类型
- 📝 文档
- ♻️ 重构

#### 变更内容

**项目文档维护**:
- `docs/project-overview.md`: 更新项目概述
  - 更新核心定位（目标用户、处理规模、运行环境等）
  - 更新功能模块总览（9 个检测器分类）
  - 更新技术架构和开发优先级

- `docs/architecture/README.md`: 更新架构设计
  - 更新检测器分类（基础校验、内容校验、高级校验）
  - 更新检测类型枚举
  - 更新数据库设计（人工复核字段）

- `docs/guides/development.md`: 更新开发指南
  - 更新项目结构（新的 detectors 目录结构）
  - 更新检测器分类说明

- `docs/project-timeline.md`: 更新开发时间轴
  - 更新阶段 2 周计划（W5-W8 检测器开发）
  - 添加当前状态（W5，P0 图片质量校验器实现）

- `.rules/prompts/development-log-rule.md`: 更新开发日志规则
  - 添加当前项目状态参考
  - 添加检测器分类结构
  - 添加开发优先级说明

#### 备注
- 文档结构：detectors/basic/ (4 个) + detectors/content/ (2 个) + detectors/advanced/ (3 个)
- 开发优先级：P0（质量校验、重复检测、文字识别）→ P1（时间校验、PS 检测、物体识别）→ P2（地点校验、AI 生成、水印检测）

### 2026-05-09 - [AI Assistant] (.gitignore 更新)

#### 类型
- 🔧 配置

#### 变更内容

**`.gitignore` 更新**:
- 补充 Python 相关忽略规则（venv, __pycache__, *.pyc 等）
- 补充 IDE 忽略规则（.idea/, .vscode/, .pydevproject 等）
- 补充操作系统忽略规则（.DS_Store, Thumbs.db 等）
- 补充日志和数据库忽略规则（*.db, *.log, logs/）
- 补充模型和大型文件忽略规则（*.onnx, *.pt, models/, *.faiss）
- 补充缓存和临时文件忽略规则（cache/, *.tmp, *.bak）
- 补充测试和覆盖率忽略规则（.pytest_cache/, .coverage 等）
- 补充环境变量和敏感文件忽略规则（.env, *.pem, credentials 等）
- 补充应用数据忽略规则（data/, exports/, tasks/）
- 补充开发工具忽略规则（.mypy_cache/, .ruff_cache/ 等）
- 保留必要的占位文件（.gitkeep, __init__.py 等）

#### 备注
- 确保模型文件、数据库文件、日志文件等不会被提交到仓库
- 保留必要的配置文件和占位文件

### 2026-05-09 - [AI Assistant] (二次迁移)

#### 类型
- 🔧 配置
- ♻️ 重构

#### 变更内容

**项目二次迁移**:
- 从 `D:\IdeaProjects\AICheck` 迁移所有代码变更到 `D:\AIcheck`
- 迁移内容：
  - `ai_check/` - 所有源代码文件
  - `tests/` - 所有测试文件
  - `docs/` - 所有文档
  - `.claude/` - Claude 技能配置
  - `.rules/` - 项目规则
  - 根目录配置文件（pyproject.toml, requirements*.txt, README.md, CLAUDE.md）
  - `CONTRIBUTING.md` - 贡献指南

**`.gitignore` 再次更新**:
- 精简规则，保留核心忽略项
- 确保模型、数据库、缓存等不被提交

#### 备注
- 迁移完成，两个目录文件数量一致（65 个文件）
- 后续开发统一使用 `D:\AIcheck` 目录

---

## 待补充

请后续开发者按格式在此处添加记录。

```markdown
### YYYY-MM-DD - [你的名字]

#### 类型
- 

#### 变更内容
- 

#### 备注
- 
```

---

## 相关文档

- [CHANGELOG.md](../CHANGELOG.md) - 版本变更历史
- [CONTRIBUTING.md](../CONTRIBUTING.md) - 贡献指南
- [docs/guides/development.md](guides/development.md) - 开发指南
