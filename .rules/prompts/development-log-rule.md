# 开发日志规则 (Development Log Rule)

## 强制阅读要求

**在开始任何开发任务前，必须阅读 `DEVELOPMENT_LOG.md` 文件。**

### 阅读目的

1. 了解最近的开发内容和变更
2. 确认没有冲突的修改
3. 理解当前开发进度和待办事项

### 阅读时机

- 开始新的开发任务时
- 准备提交代码前
- 响应开发相关请求时

### 阅读后行动

1. 确认理解最近的变更内容
2. 如有冲突或疑问，先与团队沟通
3. 完成任务后，更新 `DEVELOPMENT_LOG.md`

---

## 更新要求

### 何时更新

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
### 2026-05-08 - [张三]

#### 类型
- ✨ 新增
- 📝 文档

#### 变更内容
- `detectors/basic/quality_checker.py`: 实现图片质量校验器
  - 清晰度检测（Laplacian 方差）
  - 过曝/欠曝检测（直方图分析）
- `docs/guides/detectors-implementation-guide.md`: 检测器实现指南
  - 9 个检测器的完整实现方案
  - 技术方案对比和代码示例

#### 备注
- 质量校验器单元测试通过率 100%
- 技术选型：PyQt6 + ONNX Runtime + SQLite + FAISS + PaddleOCR
```

---

## 与其他文档的关系

| 文档 | 用途 | 更新频率 |
|------|------|----------|
| `DEVELOPMENT_LOG.md` | 日常开发记录 | 每次开发后 |
| `CHANGELOG.md` | 版本变更历史 | 每个版本发布 |
| `docs/guides/development.md` | 开发规范 | 规范变更时 |
| `docs/project-timeline.md` | 项目时间轴 | 阶段完成时 |

---

## AI 助手特别规则

作为 AI 助手，在参与项目开发时：

1. **开始任务前**: 必须读取 `DEVELOPMENT_LOG.md`，了解最近的开发内容
2. **完成任务后**: 主动询问用户是否需要更新开发日志
3. **回答问题时**: 参考开发日志中的上下文信息
4. **发现冲突**: 提醒用户检查最近的变更记录

### 典型工作流程

```
1. 用户提出开发需求
   ↓
2. AI 读取 DEVELOPMENT_LOG.md ← 必须步骤
   ↓
3. AI 了解最近变更和进度
   ↓
4. AI 提供开发建议或实现代码
   ↓
5. 完成任务后，AI 提醒用户更新日志
   ↓
6. 用户（或 AI 协助）更新 DEVELOPMENT_LOG.md
```

---

## 检查清单

在提交代码前，确认：

- [ ] 已阅读 `DEVELOPMENT_LOG.md`
- [ ] 理解最近的变更内容
- [ ] 没有与最近代码冲突
- [ ] 已更新 `DEVELOPMENT_LOG.md`
- [ ] 重大变更已更新 `CHANGELOG.md`

---

## 当前项目状态（供参考）

**项目**: AI Check - 图片 AI 检查工具

**当前阶段**: 阶段 2 - 核心检测器开发（上）(W5-W8)

**检测器分类**:
```
detectors/
├── basic/          # 基础校验（4 个）
│   ├── watermark_detector
│   ├── time_validator
│   ├── location_validator
│   └── quality_checker
├── content/        # 内容校验（2 个）
│   ├── object_validator
│   └── text_validator
└── advanced/       # 高级校验（3 个）
    ├── ai_generator_detector
    ├── ps_forgery_detector
    └── duplicate_detector
```

**开发优先级**:
- P0（本周）: 质量校验、重复检测、文字识别
- P1（下周）: 时间校验、PS 检测、物体识别
- P2（第 3 周）: 地点校验、AI 生成检测、水印检测

**技术栈**: PyQt6 + ONNX Runtime + SQLite + FAISS + PaddleOCR

---

**最后更新**: 2026-05-08
