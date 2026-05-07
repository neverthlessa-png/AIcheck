# 贡献指南

感谢您对 AI Check 项目的关注！本文档将帮助您了解如何参与项目开发。

---

## 行为准则

### 我们的承诺

- 包容、友好的交流环境
- 尊重不同的观点和经验
- 优雅地接受建设性批评
- 关注对社区最有利的事情

### 不可接受的行为

- 使用性化的语言或图像
- 人身攻击或侮辱性评论
- 骚扰、公开或私下的
- 未经许可发布他人私人信息

---

## 如何贡献

### 报告Bug

如果您发现了Bug，请通过 [GitHub Issues](../../issues) 提交，包含以下信息：

1. **Bug标题**：简短描述问题
2. **复现步骤**：详细的步骤说明
3. **预期行为**：您期望发生什么
4. **实际行为**：实际发生了什么
5. **环境信息**：
   - 操作系统及版本
   - Python版本
   - 依赖版本（`pip freeze` 输出）
6. **截图**：如果适用，添加截图帮助解释
7. **日志**：相关的错误日志

**Bug报告模板**：

```markdown
## Bug描述
[简短描述]

## 复现步骤
1. 打开应用
2. 点击 '...'
3. 选择 '...'
4. 出现错误

## 预期行为
[描述预期行为]

## 实际行为
[描述实际行为]

## 环境信息
- OS: Windows 11
- Python: 3.11.0
- AI Check: v0.1.0

## 日志
```
[粘贴错误日志]
```
```

### 提交功能请求

我们欢迎新功能建议！请提交 Issue 并标记为 `enhancement`：

1. **功能描述**：清晰描述您希望的功能
2. **使用场景**：为什么需要这个功能
3. **实现建议**：如果有想法，提供实现建议
4. **替代方案**：考虑过的其他方案

### 提交代码

#### 1. Fork仓库

```bash
# 在GitHub上Fork仓库
# 然后克隆您的Fork
git clone https://github.com/YOUR_USERNAME/ai-check.git
cd ai-check
```

#### 2. 创建分支

```bash
# 创建并切换到新分支
git checkout -b feature/your-feature-name
# 或
git checkout -b fix/your-bug-fix
```

分支命名规范：
- `feature/xxx` - 新功能
- `fix/xxx` - Bug修复
- `refactor/xxx` - 代码重构
- `docs/xxx` - 文档更新
- `test/xxx` - 测试相关

#### 3. 设置开发环境

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 安装开发依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 安装pre-commit钩子
pre-commit install
```

#### 4. 进行开发

确保遵循：
- [代码规范](./guides/development.md#代码规范)
- [提交规范](#提交信息规范)
- [测试规范](./guides/development.md#测试规范)

#### 5. 运行测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行带覆盖率的测试
pytest tests/ --cov=ai_check --cov-report=html

# 运行特定测试
pytest tests/test_core.py -v
```

#### 6. 代码检查

```bash
# 代码格式化
black ai_check/ tests/
isort ai_check/ tests/

# 类型检查
mypy ai_check/

# Linting
ruff check ai_check/
```

#### 7. 提交更改

```bash
git add .
git commit -m "feat(detector): add new forgery detector"
git push origin feature/your-feature-name
```

#### 8. 创建Pull Request

1. 在GitHub上创建Pull Request
2. 填写PR模板
3. 等待代码审查
4. 根据反馈修改

---

## 提交信息规范

我们采用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type类型

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | feat(detector): add AI-generated detector |
| `fix` | Bug修复 | fix(pipeline): resolve memory leak |
| `docs` | 文档更新 | docs(readme): update installation guide |
| `style` | 代码格式 | style: format code with black |
| `refactor` | 代码重构 | refactor(core): simplify pipeline logic |
| `test` | 测试相关 | test(forgery): add unit tests for PSDetector |
| `chore` | 构建/工具 | chore(deps): update dependencies |
| `perf` | 性能优化 | perf(batch): optimize parallel processing |

### Scope范围

| 范围 | 说明 |
|------|------|
| `core` | 核心模块 |
| `detector` | 检测器 |
| `pipeline` | 流水线 |
| `gui` | GUI界面 |
| `storage` | 存储模块 |
| `config` | 配置模块 |
| `utils` | 工具函数 |

### 示例

```bash
# 新功能
feat(detector): add copy-move forgery detector

Implement copy-move forgery detection using SIFT feature matching.
The detector identifies regions within an image that have been 
duplicated and moved to another location.

Closes #123

# Bug修复
fix(pipeline): resolve race condition in parallel processing

The parallel processing was causing race conditions when multiple
detectors tried to access shared resources. Fixed by adding proper
synchronization.

Fixes #456

# 文档更新
docs(api): add documentation for DetectorBase class

Add comprehensive documentation for the DetectorBase abstract class,
including usage examples and method descriptions.
```

---

## 代码审查标准

### 我们关注

- **正确性**：代码是否正确实现了功能
- **可读性**：代码是否清晰易懂
- **可维护性**：代码是否易于修改和扩展
- **性能**：是否存在性能问题
- **安全性**：是否存在安全隐患
- **测试覆盖**：是否有足够的测试

### 审查流程

1. 至少需要1位维护者批准
2. 所有CI检查必须通过
3. 解决所有讨论的问题
4. 保持提交历史整洁（必要时rebase）

---

## 开发规范

### 代码风格

- 遵循 PEP 8 规范
- 使用 black 格式化代码
- 使用 isort 排序导入
- 使用类型注解

### 文档规范

- 所有公共模块、类、函数必须有文档字符串
- 使用 Google Style 文档格式
- 保持文档与代码同步

### 测试规范

- 新功能必须有对应的测试
- Bug修复应该包含回归测试
- 测试覆盖率不应降低

详见 [开发指南](./guides/development.md)

---

## 项目结构

```
AICheck/
├── ai_check/              # 主包
│   ├── core/              # 核心模块（高优先级）
│   ├── detectors/         # 检测器
│   ├── app/               # GUI界面
│   ├── storage/           # 存储
│   ├── utils/             # 工具
│   └── config/            # 配置
├── tests/                 # 测试
├── docs/                  # 文档
└── scripts/               # 脚本
```

---

## 获取帮助

- **文档**：查看 [docs/](./) 目录
- **Issues**：在GitHub上提问
- **讨论**：参与GitHub Discussions

---

## 许可证

本项目采用 MIT 许可证。提交代码即表示您同意将代码以相同许可证授权。

---

## 致谢

感谢所有贡献者的付出！
