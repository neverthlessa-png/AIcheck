# 荣耀门店 AI 点检系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构现有项目为基于大模型 API 的门店巡检验证系统，支持插件化检测器架构。

**Architecture:** 采用插件化架构，将检测器抽象为统一接口的插件，支持 LLM/本地/规则三类检测器。核心任务引擎负责调度插件执行检测，规范配置驱动检测逻辑。

**Tech Stack:** PyQt6 + SQLite/SQLAlchemy + OpenAI/Claude API + Pillow + OpenCV + openpyxl

---

## 文件结构规划

### 新增文件
```
ai_check/
├── plugins/
│   ├── __init__.py
│   ├── base.py              # 插件基类和数据结构
│   ├── manager.py           # 插件管理器
│   ├── loader.py            # 插件加载器
│   └── llm/
│       ├── __init__.py
│       ├── base_llm.py      # LLM 插件基类
│       └── openai_plugin.py # OpenAI 插件
├── storage/
│   └── models.py            # SQLAlchemy 数据模型（新增）
├── core/
│   ├── inspection_pipeline.py  # 点检任务引擎（新增）
│   └── spec_loader.py       # 规范加载器（新增）
├── services/
│   ├── __init__.py
│   ├── store_service.py     # 门店服务
│   └── task_service.py      # 任务服务
├── app/
│   └── pages/
│       ├── __init__.py
│       └── task_page.py     # 任务管理页
└── config/
    └── prompts.yaml         # 提示词配置

config/
├── config.yaml              # 主配置（更新）
├── plugins.yaml             # 插件配置（新增）
└── specs/
    └── v1.1.yaml            # V1.1 规范（新增）
```

### 修改文件
- `ai_check/core/__init__.py` - 导出新模块
- `ai_check/storage/database.py` - 添加新表支持
- `requirements.txt` - 添加新依赖
- `CLAUDE.md` - 更新开发指南

---

## Task 1: 插件系统基础架构

**Files:**
- Create: `ai_check/plugins/__init__.py`
- Create: `ai_check/plugins/base.py`
- Test: `tests/unit/test_plugins_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_plugins_base.py
"""插件基类测试"""

import pytest
from ai_check.plugins.base import DetectorType, DetectionContext, DetectionResult


class TestDetectionContext:
    """检测上下文测试"""

    def test_create_context(self):
        """测试创建检测上下文"""
        context = DetectionContext(
            image_path="/path/to/image.jpg",
            question_code="B1",
            question_text="整体要求",
            inspection_rules=["物料无破损", "灯箱常亮"]
        )
        
        assert context.image_path == "/path/to/image.jpg"
        assert context.question_code == "B1"
        assert len(context.inspection_rules) == 2

    def test_context_with_extra_data(self):
        """测试带扩展数据的上下文"""
        context = DetectionContext(
            image_path="/path/to/image.jpg",
            question_code="X2",
            question_text="运营状态",
            inspection_rules=["营业时间一致"],
            extra_data={"expected_time": "09:00-21:00"}
        )
        
        assert context.extra_data["expected_time"] == "09:00-21:00"


class TestDetectionResult:
    """检测结果测试"""

    def test_create_result(self):
        """测试创建检测结果"""
        result = DetectionResult(
            question_code="B1",
            detector_name="test_detector",
            is_compliant=True,
            confidence=0.95,
            issues=[],
            suggestions=[]
        )
        
        assert result.is_compliant is True
        assert result.needs_review is False

    def test_result_needs_review(self):
        """测试需要复核的结果"""
        result = DetectionResult(
            question_code="B1",
            detector_name="test_detector",
            is_compliant=False,
            confidence=0.75,
            issues=["发现问题"],
            suggestions=["整改建议"],
            needs_review=True
        )
        
        assert result.needs_review is True
        assert len(result.issues) == 1

    def test_result_to_dict(self):
        """测试结果转字典"""
        result = DetectionResult(
            question_code="B1",
            detector_name="test_detector",
            is_compliant=True,
            confidence=0.9,
            issues=[],
            suggestions=[]
        )
        
        result_dict = result.to_dict()
        
        assert result_dict["question_code"] == "B1"
        assert result_dict["is_compliant"] is True
        assert result_dict["confidence"] == 0.9
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_plugins_base.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'ai_check.plugins'"

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/plugins/__init__.py
"""插件系统模块"""

from .base import DetectorType, DetectionContext, DetectionResult, DetectorPlugin

__all__ = [
    "DetectorType",
    "DetectionContext", 
    "DetectionResult",
    "DetectorPlugin",
]
```

```python
# ai_check/plugins/base.py
"""插件基类定义"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class DetectorType(Enum):
    """检测器类型"""
    LLM = "llm"           # 大模型检测器
    LOCAL = "local"       # 本地模型检测器
    RULE = "rule"         # 规则引擎检测器


@dataclass
class DetectionContext:
    """检测上下文"""
    image_path: str                    # 图片路径
    question_code: str                 # 问题编号 (如 B1, C2)
    question_text: str                 # 问题内容
    inspection_rules: list[str] = field(default_factory=list)  # 检查规范条目
    store_info: Optional[dict] = None  # 门店信息
    extra_data: Optional[dict] = None  # 扩展数据


@dataclass
class DetectionResult:
    """检测结果"""
    question_code: str                 # 问题编号
    detector_name: str                 # 检测器名称
    is_compliant: bool                 # 是否合规
    confidence: float                  # 置信度 (0-1)
    issues: list[str] = field(default_factory=list)  # 问题列表
    suggestions: list[str] = field(default_factory=list)  # 建议列表
    raw_response: Optional[str] = None  # 原始响应（用于调试）
    needs_review: bool = False         # 是否需要人工复核

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "question_code": self.question_code,
            "detector_name": self.detector_name,
            "is_compliant": self.is_compliant,
            "confidence": self.confidence,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "needs_review": self.needs_review,
        }


class DetectorPlugin(ABC):
    """检测器插件基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """插件名称"""
        pass

    @property
    @abstractmethod
    def detector_type(self) -> DetectorType:
        """检测器类型"""
        pass

    @property
    def supported_questions(self) -> list[str]:
        """支持的问题编号列表，空列表表示支持全部"""
        return []

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> bool:
        """初始化插件（加载配置、API Key 等）"""
        pass

    @abstractmethod
    def detect(self, context: DetectionContext) -> DetectionResult:
        """执行检测"""
        pass

    def cleanup(self) -> None:
        """清理资源（可选实现）"""
        pass

    def can_handle(self, question_code: str) -> bool:
        """判断是否能处理指定问题"""
        if not self.supported_questions:
            return True
        return question_code in self.supported_questions
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_plugins_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_check/plugins/__init__.py ai_check/plugins/base.py tests/unit/test_plugins_base.py
git commit -m "feat(plugins): add plugin base classes and data structures"
```

---

## Task 2: 插件管理器

**Files:**
- Create: `ai_check/plugins/manager.py`
- Test: `tests/unit/test_plugins_manager.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_plugins_manager.py
"""插件管理器测试"""

import pytest
from ai_check.plugins.base import DetectorType, DetectionContext, DetectionResult, DetectorPlugin
from ai_check.plugins.manager import PluginManager


class MockPlugin(DetectorPlugin):
    """模拟插件"""

    @property
    def name(self) -> str:
        return "mock_plugin"

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.LLM

    @property
    def supported_questions(self) -> list[str]:
        return ["B1", "B2"]

    def initialize(self, config: dict) -> bool:
        return True

    def detect(self, context: DetectionContext) -> DetectionResult:
        return DetectionResult(
            question_code=context.question_code,
            detector_name=self.name,
            is_compliant=True,
            confidence=0.9,
        )


class MockUniversalPlugin(DetectorPlugin):
    """支持所有问题的模拟插件"""

    @property
    def name(self) -> str:
        return "universal_plugin"

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.LOCAL

    def initialize(self, config: dict) -> bool:
        return True

    def detect(self, context: DetectionContext) -> DetectionResult:
        return DetectionResult(
            question_code=context.question_code,
            detector_name=self.name,
            is_compliant=True,
            confidence=0.8,
        )


class TestPluginManager:
    """插件管理器测试"""

    def test_register_plugin(self):
        """测试注册插件"""
        manager = PluginManager()
        plugin = MockPlugin()
        plugin.initialize({})
        
        manager.register(plugin)
        
        assert manager.get("mock_plugin") == plugin

    def test_get_by_type(self):
        """测试按类型获取插件"""
        manager = PluginManager()
        llm_plugin = MockPlugin()
        local_plugin = MockUniversalPlugin()
        
        llm_plugin.initialize({})
        local_plugin.initialize({})
        
        manager.register(llm_plugin)
        manager.register(local_plugin)
        
        llm_plugins = manager.get_by_type(DetectorType.LLM)
        local_plugins = manager.get_by_type(DetectorType.LOCAL)
        
        assert len(llm_plugins) == 1
        assert len(local_plugins) == 1
        assert llm_plugins[0].name == "mock_plugin"

    def test_get_detector_for_question(self):
        """测试根据问题获取检测器"""
        manager = PluginManager()
        plugin = MockPlugin()
        plugin.initialize({})
        manager.register(plugin)
        
        # B1 在 supported_questions 中
        detector = manager.get_detector_for_question("B1")
        assert detector == plugin
        
        # X1 不在 supported_questions 中
        detector = manager.get_detector_for_question("X1")
        assert detector is None

    def test_get_detector_priority(self):
        """测试检测器优先级"""
        manager = PluginManager()
        
        # 注册 LLM 和 本地插件
        llm_plugin = MockPlugin()
        local_plugin = MockUniversalPlugin()
        
        llm_plugin.initialize({})
        local_plugin.initialize({})
        
        manager.register(llm_plugin)
        manager.register(local_plugin)
        
        # 本地插件应该优先（LOCAL > LLM）
        detector = manager.get_detector_for_question("X1")
        assert detector.name == "universal_plugin"

    def test_list_all(self):
        """测试列出所有插件"""
        manager = PluginManager()
        llm_plugin = MockPlugin()
        local_plugin = MockUniversalPlugin()
        
        llm_plugin.initialize({})
        local_plugin.initialize({})
        
        manager.register(llm_plugin)
        manager.register(local_plugin)
        
        all_plugins = manager.list_all()
        
        assert len(all_plugins) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_plugins_manager.py -v`
Expected: FAIL with "ModuleNotFoundError: No module named 'ai_check.plugins.manager'"

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/plugins/manager.py
"""插件管理器"""

from typing import Optional
from .base import DetectorPlugin, DetectorType


class PluginManager:
    """插件管理器"""

    def __init__(self) -> None:
        self._plugins: dict[str, DetectorPlugin] = {}
        self._plugins_by_type: dict[DetectorType, list[str]] = {
            DetectorType.LLM: [],
            DetectorType.LOCAL: [],
            DetectorType.RULE: [],
        }

    def register(self, plugin: DetectorPlugin) -> None:
        """注册插件"""
        self._plugins[plugin.name] = plugin
        self._plugins_by_type[plugin.detector_type].append(plugin.name)

    def get(self, name: str) -> Optional[DetectorPlugin]:
        """获取插件"""
        return self._plugins.get(name)

    def get_by_type(self, detector_type: DetectorType) -> list[DetectorPlugin]:
        """按类型获取插件列表"""
        return [
            self._plugins[name] 
            for name in self._plugins_by_type[detector_type]
            if name in self._plugins
        ]

    def get_detector_for_question(self, question_code: str) -> Optional[DetectorPlugin]:
        """根据问题编号获取合适的检测器
        
        优先级: RULE > LOCAL > LLM
        """
        # 按优先级遍历
        for detector_type in [DetectorType.RULE, DetectorType.LOCAL, DetectorType.LLM]:
            for plugin in self.get_by_type(detector_type):
                if plugin.can_handle(question_code):
                    return plugin
        return None

    def list_all(self) -> list[DetectorPlugin]:
        """列出所有插件"""
        return list(self._plugins.values())

    def unregister(self, name: str) -> bool:
        """注销插件"""
        if name not in self._plugins:
            return False
        
        plugin = self._plugins[name]
        plugin.cleanup()
        
        # 从类型列表中移除
        if name in self._plugins_by_type[plugin.detector_type]:
            self._plugins_by_type[plugin.detector_type].remove(name)
        
        del self._plugins[name]
        return True
```

- [ ] **Step 4: Update `__init__.py`**

```python
# ai_check/plugins/__init__.py
"""插件系统模块"""

from .base import DetectorType, DetectionContext, DetectionResult, DetectorPlugin
from .manager import PluginManager

__all__ = [
    "DetectorType",
    "DetectionContext", 
    "DetectionResult",
    "DetectorPlugin",
    "PluginManager",
]
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_plugins_manager.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ai_check/plugins/manager.py ai_check/plugins/__init__.py tests/unit/test_plugins_manager.py
git commit -m "feat(plugins): add plugin manager for detector registration and dispatch"
```

---

## Task 3: LLM 插件基类

**Files:**
- Create: `ai_check/plugins/llm/__init__.py`
- Create: `ai_check/plugins/llm/base_llm.py`
- Test: `tests/unit/test_llm_base.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_llm_base.py
"""LLM 插件基类测试"""

import pytest
from ai_check.plugins.base import DetectionContext
from ai_check.plugins.llm.base_llm import BaseLLMPlugin


class TestLLMPlugin(BaseLLMPlugin):
    """测试用 LLM 插件"""

    @property
    def name(self) -> str:
        return "test_llm"

    def initialize(self, config: dict) -> bool:
        self.model = config.get("model", "test-model")
        return True

    def analyze_image(self, image_path: str, prompt: str) -> str:
        # 模拟响应
        return """是否合规：是
置信度：95%
发现的问题：无
整改建议：无"""


class TestBaseLLMPlugin:
    """LLM 插件基类测试"""

    def test_build_prompt(self):
        """测试构建提示词"""
        plugin = TestLLMPlugin()
        plugin.initialize({})
        
        context = DetectionContext(
            image_path="/test.jpg",
            question_code="B1",
            question_text="整体要求",
            inspection_rules=["物料无破损", "灯箱常亮"]
        )
        
        prompt = plugin.build_prompt(context)
        
        assert "B1" in prompt
        assert "整体要求" in prompt
        assert "物料无破损" in prompt
        assert "灯箱常亮" in prompt

    def test_parse_response(self):
        """测试解析响应"""
        plugin = TestLLMPlugin()
        plugin.initialize({})
        
        response = """是否合规：是
置信度：95%
发现的问题：无
整改建议：无"""
        
        result = plugin.parse_response(response, "B1")
        
        assert result.question_code == "B1"
        assert result.detector_name == "test_llm"
        assert result.is_compliant is True
        assert result.confidence == 0.95

    def test_parse_non_compliant_response(self):
        """测试解析不合规响应"""
        plugin = TestLLMPlugin()
        plugin.initialize({})
        
        response = """是否合规：否
置信度：85%
发现的问题：灯箱未亮
整改建议：检查灯箱电源"""
        
        result = plugin.parse_response(response, "B1")
        
        assert result.is_compliant is False
        assert result.confidence == 0.85
        assert result.needs_review is True  # 置信度低于 0.8 时需要复核
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_llm_base.py -v`
Expected: FAIL with "ModuleNotFoundError"

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/plugins/llm/__init__.py
"""LLM 插件模块"""

from .base_llm import BaseLLMPlugin

__all__ = ["BaseLLMPlugin"]
```

```python
# ai_check/plugins/llm/base_llm.py
"""LLM 插件基类"""

import re
from abc import abstractmethod
from typing import Any

from ..base import DetectorPlugin, DetectorType, DetectionContext, DetectionResult


class BaseLLMPlugin(DetectorPlugin):
    """LLM 插件基类"""

    @property
    def detector_type(self) -> DetectorType:
        return DetectorType.LLM

    @abstractmethod
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """调用 LLM API 分析图片
        
        Args:
            image_path: 图片路径
            prompt: 提示词
            
        Returns:
            LLM 的原始响应文本
        """
        pass

    def build_prompt(self, context: DetectionContext) -> str:
        """构建提示词"""
        rules_text = "\n".join(f"- {rule}" for rule in context.inspection_rules)
        
        prompt = f"""你是一个门店巡检验收专家。请根据以下检查规范分析图片。

【问题编号】{context.question_code}
【检查项目】{context.question_text}
【检查规范】
{rules_text}

请分析图片并判断是否符合规范。输出格式如下：
1. 是否合规：是/否
2. 置信度：0-100%
3. 发现的问题：（如有问题请列出）
4. 整改建议：（如有问题请给出建议）

请开始分析："""
        return prompt

    def parse_response(self, response: str, question_code: str) -> DetectionResult:
        """解析 LLM 响应"""
        # 解析是否合规
        is_compliant = "是否合规：是" in response or "是否合规：是" in response.replace(" ", "")
        
        # 解析置信度
        confidence_match = re.search(r"置信度[：:]\s*(\d+)", response)
        confidence = int(confidence_match.group(1)) / 100 if confidence_match else 0.7
        
        # 提取问题
        issues = self._extract_section(response, "发现的问题")
        
        # 提取建议
        suggestions = self._extract_section(response, "整改建议")
        
        # 判断是否需要复核（置信度低于 0.8 或存在问题）
        needs_review = confidence < 0.8 or (issues and "无" not in issues[0])

        return DetectionResult(
            question_code=question_code,
            detector_name=self.name,
            is_compliant=is_compliant,
            confidence=confidence,
            issues=issues,
            suggestions=suggestions,
            raw_response=response,
            needs_review=needs_review
        )

    def _extract_section(self, response: str, section_name: str) -> list[str]:
        """提取响应中的特定部分"""
        pattern = rf"{section_name}[：:]\s*(.+?)(?=\n|$)"
        match = re.search(pattern, response)
        if match:
            content = match.group(1).strip()
            if content and content != "无":
                return [content]
        return []

    def detect(self, context: DetectionContext) -> DetectionResult:
        """执行检测"""
        prompt = self.build_prompt(context)
        response = self.analyze_image(context.image_path, prompt)
        return self.parse_response(response, context.question_code)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_llm_base.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_check/plugins/llm/__init__.py ai_check/plugins/llm/base_llm.py tests/unit/test_llm_base.py
git commit -m "feat(plugins): add LLM plugin base class with prompt building and response parsing"
```

---

## Task 4: OpenAI 插件实现

**Files:**
- Create: `ai_check/plugins/llm/openai_plugin.py`
- Test: `tests/unit/test_openai_plugin.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_openai_plugin.py
"""OpenAI 插件测试"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from ai_check.plugins.llm.openai_plugin import OpenAIPlugin


class TestOpenAIPlugin:
    """OpenAI 插件测试"""

    def test_plugin_properties(self):
        """测试插件属性"""
        plugin = OpenAIPlugin()
        
        assert plugin.name == "openai_gpt4v"
        assert plugin.detector_type.value == "llm"

    def test_initialize_with_config(self):
        """测试初始化配置"""
        plugin = OpenAIPlugin()
        
        with patch("ai_check.plugins.llm.openai_plugin.OpenAI") as mock_openai:
            result = plugin.initialize({
                "api_key": "test-key",
                "model": "gpt-4o"
            })
            
            assert result is True
            assert plugin.model == "gpt-4o"
            mock_openai.assert_called_once()

    def test_initialize_with_base_url(self):
        """测试自定义 API 地址"""
        plugin = OpenAIPlugin()
        
        with patch("ai_check.plugins.llm.openai_plugin.OpenAI") as mock_openai:
            result = plugin.initialize({
                "api_key": "test-key",
                "model": "gpt-4o",
                "base_url": "https://api.proxy.com/v1"
            })
            
            assert result is True

    def test_analyze_image(self, tmp_path):
        """测试图片分析"""
        plugin = OpenAIPlugin()
        
        # 创建测试图片
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image content")
        
        with patch("ai_check.plugins.llm.openai_plugin.OpenAI") as mock_openai:
            plugin.initialize({"api_key": "test-key"})
            
            # 模拟 API 响应
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content="测试响应"))]
            plugin.client.chat.completions.create = Mock(return_value=mock_response)
            
            response = plugin.analyze_image(str(test_image), "测试提示词")
            
            assert response == "测试响应"
            plugin.client.chat.completions.create.assert_called_once()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_openai_plugin.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/plugins/llm/openai_plugin.py
"""OpenAI GPT-4V 插件"""

import base64
from typing import Any

from loguru import logger

from .base_llm import BaseLLMPlugin


class OpenAIPlugin(BaseLLMPlugin):
    """OpenAI GPT-4V 插件"""

    def __init__(self) -> None:
        self.client = None
        self.model = "gpt-4o"
        self.api_key = None
        self.base_url = None

    @property
    def name(self) -> str:
        return "openai_gpt4v"

    def initialize(self, config: dict[str, Any]) -> bool:
        """初始化插件"""
        try:
            from openai import OpenAI
            
            self.api_key = config_key")
            self.model = config.get("model", "gpt-4o")
            self.base_url = config.get("base_url")
            
            if not self.api_key:
                logger.error("OpenAI API key not provided")
                return False
            
            client_kwargs: dict[str, Any] = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            
            self.client = OpenAI(**client_kwargs)
            logger.info(f"OpenAI plugin initialized with model: {self.model}")
            return True
            
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI plugin: {e}")
            return False

    def analyze_image(self, image_path: str, prompt: str) -> str:
        """调用 OpenAI API 分析图片"""
        if not self.client:
            raise RuntimeError("Plugin not initialized")
        
        # 读取并编码图片
        with open(image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
        
        # 判断图片类型
        image_type = "image/jpeg"
        if image_path.lower().endswith(".png"):
            image_type = "image/png"
        elif image_path.lower().endswith(".gif"):
            image_type = "image/gif"
        elif image_path.lower().endswith(".webp"):
            image_type = "image/webp"
        
        # 调用 API
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{image_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content or ""
```

- [ ] **Step 4: Update LLM `__init__.py`**

```python
# ai_check/plugins/llm/__init__.py
"""LLM 插件模块"""

from .base_llm import BaseLLMPlugin
from .openai_plugin import OpenAIPlugin

__all__ = ["BaseLLMPlugin", "OpenAIPlugin"]
```

- [ ] **Step 5: Update requirements.txt**

```txt
# 在 requirements.txt 添加
openai>=1.0.0
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/unit/test_openai_plugin.py -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add ai_check/plugins/llm/__init__.py ai_check/plugins/llm/openai_plugin.py tests/unit/test_openai_plugin.py requirements.txt
git commit -m "feat(plugins): add OpenAI GPT-4V plugin implementation"
```

---

## Task 5: SQLAlchemy 数据模型

**Files:**
- Create: `ai_check/storage/models.py`
- Test: `tests/unit/test_models.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_models.py
"""数据模型测试"""

import pytest
from datetime import datetime

from ai_check.storage.models import (
    Base,
    StoreInfo,
    InspectionSpec,
    InspectionTask,
    TaskImage,
    DetectionResult,
    ReviewRecord
)


class TestStoreInfo:
    """门店信息模型测试"""

    def test_create_store(self):
        """测试创建门店"""
        store = StoreInfo(
            store_code="BJ001",
            store_name="北京朝阳体验店",
            region="北京"
        )
        
        assert store.store_code == "BJ001"
        assert store.store_name == "北京朝阳体验店"
        assert store.status == "active"

    def test_store_default_status(self):
        """测试默认状态"""
        store = StoreInfo(
            store_code="SH001",
            store_name="上海浦东体验店"
        )
        
        assert store.status == "active"


class TestInspectionSpec:
    """点检规范模型测试"""

    def test_create_spec(self):
        """测试创建规范"""
        spec = InspectionSpec(
            version="V1.1",
            category="B",
            question_code="B1",
            question_name="整体要求",
            rules=["物料无破损", "灯箱常亮"],
            score_value=10,
            scoring_criteria="任意1条不符合扣5分"
        )
        
        assert spec.question_code == "B1"
        assert spec.score_value == 10
        assert len(spec.rules) == 2

    def test_spec_is_active_default(self):
        """测试默认启用状态"""
        spec = InspectionSpec(
            version="V1.1",
            category="B",
            question_code="B2",
            question_name="产品试用",
            rules=["样机正常"],
            score_value=5
        )
        
        assert spec.is_active is True


class TestInspectionTask:
    """点检任务模型测试"""

    def test_create_task(self):
        """测试创建任务"""
        task = InspectionTask(
            task_no="TASK20260611001",
            store_id=1,
            spec_version="V1.1",
            source="manual"
        )
        
        assert task.task_no == "TASK20260611001"
        assert task.status == "pending"

    def test_task_default_values(self):
        """测试任务默认值"""
        task = InspectionTask(
            task_no="TASK001",
            store_id=1,
            spec_version="V1.1"
        )
        
        assert task.source == "manual"
        assert task.status == "pending"


class TestDetectionResult:
    """检测结果模型测试"""

    def test_create_result(self):
        """测试创建检测结果"""
        result = DetectionResult(
            task_id=1,
            image_id=1,
            spec_id=1,
            question_code="B1",
            detector_name="openai_gpt4v",
            is_compliant=True,
            confidence=0.95
        )
        
        assert result.is_compliant is True
        assert result.confidence == 0.95
        assert result.needs_review is False

    def test_result_needs_review(self):
        """测试需要复核的结果"""
        result = DetectionResult(
            task_id=1,
            image_id=1,
            spec_id=1,
            question_code="B1",
            detector_name="openai_gpt4v",
            is_compliant=False,
            confidence=0.75,
            issues=["灯箱未亮"],
            needs_review=True
        )
        
        assert result.needs_review is True
        assert len(result.issues) == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_models.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/storage/models.py
"""数据模型定义"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
    Boolean,
    Text,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class StoreInfo(Base):
    """门店信息表"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    store_code = Column(String(50), unique=True, nullable=False, index=True)
    store_name = Column(String(200), nullable=False)
    region = Column(String(50))
    address = Column(String(500))
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关联
    tasks = relationship("InspectionTask", back_populates="store")


class InspectionSpec(Base):
    """点检规范表"""
    __tablename__ = "inspection_specs"

    id = Column(Integer, primary_key=True)
    version = Column(String(20), nullable=False)
    category = Column(String(50), nullable=False)
    question_code = Column(String(10), nullable=False, index=True)
    question_name = Column(String(100), nullable=False)
    rules = Column(JSON, nullable=False)
    score_value = Column(Integer, nullable=False)
    scoring_criteria = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # 关联
    results = relationship("DetectionResult", back_populates="spec")


class InspectionTask(Base):
    """点检任务表"""
    __tablename__ = "inspection_tasks"

    id = Column(Integer, primary_key=True)
    task_no = Column(String(50), unique=True, nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False)
    spec_version = Column(String(20), nullable=False)
    source = Column(String(20), default="manual")
    source_ref = Column(String(200))
    status = Column(String(20), default="pending")
    total_score = Column(Float)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime)

    # 关联
    store = relationship("StoreInfo", back_populates="tasks")
    images = relationship("TaskImage", back_populates="task")
    results = relationship("DetectionResult", back_populates="task")


class TaskImage(Base):
    """任务图片表"""
    __tablename__ = "task_images"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("inspection_tasks.id"), nullable=False)
    question_code = Column(String(10), nullable=False, index=True)
    image_path = Column(String(500), nullable=False)
    image_hash = Column(String(64), index=True)
    original_name = Column(String(200))
    file_size = Column(Integer)
    shot_time = Column(DateTime)
    upload_time = Column(DateTime, default=datetime.now)

    # 关联
    task = relationship("InspectionTask", back_populates="images")
    results = relationship("DetectionResult", back_populates="image")


class DetectionResult(Base):
    """检测结果表"""
    __tablename__ = "detection_results"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("inspection_tasks.id"), nullable=False)
    image_id = Column(Integer, ForeignKey("task_images.id"), nullable=False)
    spec_id = Column(Integer, ForeignKey("inspection_specs.id"), nullable=False)
    question_code = Column(String(10), nullable=False, index=True)

    # 检测结果
    detector_name = Column(String(50))
    is_compliant = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    issues = Column(JSON)
    suggestions = Column(JSON)
    raw_response = Column(Text)

    # 复核状态
    needs_review = Column(Boolean, default=False)
    review_status = Column(String(20))
    reviewed_by = Column(String(50))
    reviewed_at = Column(DateTime)
    review_note = Column(Text)
    final_result = Column(Boolean)

    created_at = Column(DateTime, default=datetime.now)

    # 关联
    task = relationship("InspectionTask", back_populates="results")
    image = relationship("TaskImage", back_populates="results")
    spec = relationship("InspectionSpec", back_populates="results")


class ReviewRecord(Base):
    """复核记录表"""
    __tablename__ = "review_records"

    id = Column(Integer, primary_key=True)
    result_id = Column(Integer, ForeignKey("detection_results.id"), nullable=False)
    reviewer = Column(String(50), nullable=False)
    original_result = Column(Boolean)
    final_result = Column(Boolean, nullable=False)
    note = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
```

- [ ] **Step 4: Update requirements.txt**

```txt
# 在 requirements.txt 添加
sqlalchemy>=2.0.0
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_models.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ai_check/storage/models.py tests/unit/test_models.py requirements.txt
git commit -m "feat(storage): add SQLAlchemy models for inspection system"
```

---

## Task 6: 点检规范加载器

**Files:**
- Create: `ai_check/core/spec_loader.py`
- Create: `config/specs/v1.1.yaml`
- Test: `tests/unit/test_spec_loader.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_spec_loader.py
"""规范加载器测试"""

import pytest
from pathlib import Path
import yaml

from ai_check.core.spec_loader import SpecLoader


class TestSpecLoader:
    """规范加载器测试"""

    def test_load_spec_from_yaml(self, tmp_path):
        """测试从 YAML 加载规范"""
        # 创建测试规范文件
        spec_file = tmp_path / "v1.1.yaml"
        spec_content = """
version: "V1.1"
effective_date: "2026-06-01"

categories:
  - code: "B"
    name: "产品营销能力"
    total_score: 60

questions:
  - code: "B1"
    category: "B"
    name: "整体要求"
    score: 10
    rules:
      - "物料无破损"
      - "灯箱常亮"
    scoring_criteria: "任意1条不符合扣5分"
"""
        spec_file.write_text(spec_content, encoding="utf-8")
        
        loader = SpecLoader()
        spec = loader.load(spec_file)
        
        assert spec["version"] == "V1.1"
        assert len(spec["questions"]) == 1
        assert spec["questions"][0]["code"] == "B1"

    def test_get_question_by_code(self, tmp_path):
        """测试按编号获取问题"""
        spec_file = tmp_path / "v1.1.yaml"
        spec_content = """
version: "V1.1"
questions:
  - code: "B1"
    name: "整体要求"
    score: 10
    rules:
      - "物料无破损"
"""
        spec_file.write_text(spec_content, encoding="utf-8")
        
        loader = SpecLoader()
        loader.load(spec_file)
        
        question = loader.get_question("B1")
        
        assert question is not None
        assert question["name"] == "整体要求"
        assert question["score"] == 10

    def test_get_all_codes(self, tmp_path):
        """测试获取所有问题编号"""
        spec_file = tmp_path / "v1.1.yaml"
        spec_content = """
version: "V1.1"
questions:
  - code: "B1"
    name: "问题1"
    score: 10
    rules: []
  - code: "B2"
    name: "问题2"
    score: 5
    rules: []
"""
        spec_file.write_text(spec_content, encoding="utf-8")
        
        loader = SpecLoader()
        loader.load(spec_file)
        
        codes = loader.get_all_codes()
        
        assert len(codes) == 2
        assert "B1" in codes
        assert "B2" in codes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_spec_loader.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/core/spec_loader.py
"""点检规范加载器"""

from pathlib import Path
from typing import Any, Optional

import yaml
from loguru import logger


class SpecLoader:
    """点检规范加载器"""

    def __init__(self) -> None:
        self._spec: dict[str, Any] = {}
        self._questions: dict[str, dict[str, Any]] = {}
        self._categories: dict[str, dict[str, Any]] = {}

    def load(self, spec_path: Path | str) -> dict[str, Any]:
        """加载规范文件
        
        Args:
            spec_path: 规范文件路径
            
        Returns:
            规范数据字典
        """
        spec_path = Path(spec_path)
        
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")
        
        with open(spec_path, "r", encoding="utf-8") as f:
            self._spec = yaml.safe_load(f)
        
        # 索引问题
        self._questions = {}
        for question in self._spec.get("questions", []):
            self._questions[question["code"]] = question
        
        # 索引分类
        self._categories = {}
        for category in self._spec.get("categories", []):
            self._categories[category["code"]] = category
        
        logger.info(f"Loaded spec: {self._spec.get('version', 'unknown')}, "
                   f"{len(self._questions)} questions")
        
        return self._spec

    def get_question(self, question_code: str) -> Optional[dict[str, Any]]:
        """获取指定问题
        
        Args:
            question_code: 问题编号
            
        Returns:
            问题数据字典，不存在则返回 None
        """
        return self._questions.get(question_code)

    def get_category(self, category_code: str) -> Optional[dict[str, Any]]:
        """获取指定分类
        
        Args:
            category_code: 分类编号
            
        Returns:
            分类数据字典
        """
        return self._categories.get(category_code)

    def get_all_codes(self) -> list[str]:
        """获取所有问题编号"""
        return list(self._questions.keys())

    def get_questions_by_category(self, category_code: str) -> list[dict[str, Any]]:
        """获取指定分类下的所有问题"""
        return [
            q for q in self._questions.values()
            if q.get("category") == category_code
        ]

    @property
    def version(self) -> str:
        """获取规范版本"""
        return self._spec.get("version", "unknown")

    @property
    def spec(self) -> dict[str, Any]:
        """获取完整规范数据"""
        return self._spec
```

- [ ] **Step 4: Create default spec file**

```yaml
# config/specs/v1.1.yaml
version: "V1.1"
effective_date: "2026-06-01"

categories:
  - code: "X"
    name: "业务专项"
    total_score: 20

  - code: "B"
    name: "产品营销能力（陈列管理）"
    total_score: 60

  - code: "C"
    name: "人员服务能力"
    total_score: 20

questions:
  - code: "X1"
    category: "X"
    name: "视频监控使用"
    score: 5
    rules:
      - "监控画面角度正常，保持清晰彩色画面"
      - "门店监控或网络故障必须第一时间修复"
      - "体验店监控视频必须保留30天"
    scoring_criteria: "第1条不符合扣5分；第2-3条为提醒项，不扣分"

  - code: "X2"
    category: "X"
    name: "运营状态"
    score: 15
    rules:
      - "门店营业时间必须与荣耀官网保持一致"
      - "运营时间需规范填写"
    scoring_criteria: "第1条不符合扣10分；第2点不符合扣5分"

  - code: "B1"
    category: "B"
    name: "整体要求"
    score: 10
    rules:
      - "店内所有物料无破损，不可遮挡客流通道"
      - "店内灯箱常亮，画面必须为最新主推内容"
    scoring_criteria: "任意1条不符合扣5分；不符合2条不得分"

  - code: "B2"
    category: "B"
    name: "产品试用-样机"
    score: 5
    rules:
      - "机位不得空置"
      - "样机不可黑屏"
      - "互联功能正常"
    scoring_criteria: "此项不符合扣5分"

  - code: "B3"
    category: "B"
    name: "道具"
    score: 15
    rules:
      - "台卡不得与桌面导视灯陈列在同一侧"
      - "体验桌台卡画面需遵循最新陈列指引"
      - "店内不得陈列损坏的道具"
    scoring_criteria: "任意1条不符合扣5分；不符合3条以上不得分"

  - code: "B4"
    category: "B"
    name: "价格签"
    score: 5
    rules:
      - "所有商品配备价签"
      - "信息准确匹配"
      - "无破损无污渍"
    scoring_criteria: "此项不符合扣5分"

  - code: "C1"
    category: "C"
    name: "服务态度-标准服务"
    score: 5
    rules:
      - "消费者进店30S内，主动迎接问好"
      - "接待中友好沟通"
      - "离店时礼貌送别"
    scoring_criteria: "任意1条不符合扣5分"

  - code: "C2"
    category: "C"
    name: "店员形象-店员着装"
    score: 5
    rules:
      - "店内员工统一穿着荣耀工装"
      - "建议穿深色长裤"
      - "建议黑/白板鞋或运动鞋"
      - "店员需佩戴工牌"
    scoring_criteria: "任意1条不符合扣5分"

  - code: "C3"
    category: "C"
    name: "店员形象-行为规范"
    score: 10
    rules:
      - "营业期间门店不得超过10分钟无人看管"
      - "营业区及店门口店员严禁吸烟"
      - "禁止与工作无关行为"
      - "店内禁止玩手机"
    scoring_criteria: "任意1条不符合扣5分；不符合2条及2条以上不得分"
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/unit/test_spec_loader.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add ai_check/core/spec_loader.py config/specs/v1.1.yaml tests/unit/test_spec_loader.py
git commit -m "feat(core): add spec loader for inspection standards"
```

---

## Task 7: 点检任务引擎

**Files:**
- Create: `ai_check/core/inspection_pipeline.py`
- Test: `tests/unit/test_inspection_pipeline.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/unit/test_inspection_pipeline.py
"""点检任务引擎测试"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from ai_check.core.inspection_pipeline import InspectionPipeline
from ai_check.plugins.base import DetectionContext, DetectionResult


class TestInspectionPipeline:
    """点检任务引擎测试"""

    def test_create_pipeline(self, tmp_path):
        """测试创建引擎"""
        # 创建模拟规范加载器
        mock_spec_loader = Mock()
        mock_spec_loader.version = "V1.1"
        mock_spec_loader.get_question.return_value = {
            "code": "B1",
            "name": "整体要求",
            "rules": ["物料无破损"]
        }
        
        # 创建模拟插件管理器
        mock_plugin_manager = Mock()
        mock_plugin = Mock()
        mock_plugin.detect.return_value = DetectionResult(
            question_code="B1",
            detector_name="mock",
            is_compliant=True,
            confidence=0.9,
        )
        mock_plugin_manager.get_detector_for_question.return_value = mock_plugin
        
        pipeline = InspectionPipeline(
            spec_loader=mock_spec_loader,
            plugin_manager=mock_plugin_manager
        )
        
        assert pipeline is not None

    def test_detect_single_image(self, tmp_path):
        """测试单图检测"""
        # 准备测试图片
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image")
        
        # 模拟组件
        mock_spec_loader = Mock()
        mock_spec_loader.get_question.return_value = {
            "code": "B1",
            "name": "整体要求",
            "rules": ["物料无破损"]
        }
        
        mock_plugin_manager = Mock()
        mock_plugin = Mock()
        mock_plugin.detect.return_value = DetectionResult(
            question_code="B1",
            detector_name="mock",
            is_compliant=True,
            confidence=0.95,
        )
        mock_plugin_manager.get_detector_for_question.return_value = mock_plugin
        
        pipeline = InspectionPipeline(
            spec_loader=mock_spec_loader,
            plugin_manager=mock_plugin_manager
        )
        
        result = pipeline.detect_single(
            image_path=str(test_image),
            question_code="B1"
        )
        
        assert result is not None
        assert result.question_code == "B1"
        assert result.is_compliant is True

    def test_build_context(self, tmp_path):
        """测试构建检测上下文"""
        test_image = tmp_path / "test.jpg"
        test_image.write_bytes(b"fake image")
        
        mock_spec_loader = Mock()
        mock_spec_loader.get_question.return_value = {
            "code": "B1",
            "name": "整体要求",
            "rules": ["物料无破损", "灯箱常亮"]
        }
        
        mock_plugin_manager = Mock()
        
        pipeline = InspectionPipeline(
            spec_loader=mock_spec_loader,
            plugin_manager=mock_plugin_manager
        )
        
        context = pipeline._build_context(
            image_path=str(test_image),
            question_code="B1"
        )
        
        assert context.image_path == str(test_image)
        assert context.question_code == "B1"
        assert len(context.inspection_rules) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/unit/test_inspection_pipeline.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# ai_check/core/inspection_pipeline.py
"""点检任务引擎"""

from typing import Any, Optional
from pathlib import Path

from loguru import logger

from ai_check.plugins.base import DetectionContext, DetectionResult, DetectorPlugin, PluginManager
from .spec_loader import SpecLoader


class InspectionPipeline:
    """点检任务引擎
    
    负责协调规范加载器和检测器插件，执行检测任务。
    """

    def __init__(
        self,
        spec_loader: SpecLoader,
        plugin_manager: PluginManager,
    ) -> None:
        self.spec_loader = spec_loader
        self.plugin_manager = plugin_manager

    def detect_single(
        self,
        image_path: str,
        question_code: str,
        extra_data: Optional[dict[str, Any]] = None,
    ) -> Optional[DetectionResult]:
        """检测单张图片
        
        Args:
            image_path: 图片路径
            question_code: 问题编号
            extra_data: 扩展数据
            
        Returns:
            检测结果
        """
        # 构建检测上下文
        context = self._build_context(image_path, question_code, extra_data)
        
        if context is None:
            logger.error(f"Failed to build context for {question_code}")
            return None
        
        # 获取合适的检测器
        detector = self.plugin_manager.get_detector_for_question(question_code)
        
        if detector is None:
            logger.error(f"No detector available for {question_code}")
            return None
        
        # 执行检测
        logger.info(f"Detecting {question_code} with {detector.name}")
        result = detector.detect(context)
        
        return result

    def _build_context(
        self,
        image_path: str,
        question_code: str,
        extra_data: Optional[dict[str, Any]] = None,
    ) -> Optional[DetectionContext]:
        """构建检测上下文"""
        # 获取问题信息
        question = self.spec_loader.get_question(question_code)
        
        if question is None:
            logger.error(f"Question not found: {question_code}")
            return None
        
        return DetectionContext(
            image_path=image_path,
            question_code=question_code,
            question_text=question.get("name", ""),
            inspection_rules=question.get("rules", []),
            extra_data=extra_data,
        )

    def detect_batch(
        self,
        images: list[dict[str, Any]],
    ) -> list[DetectionResult]:
        """批量检测
        
        Args:
            images: 图片列表，每项包含 image_path 和 question_code
            
        Returns:
            检测结果列表
        """
        results = []
        
        for item in images:
            result = self.detect_single(
                image_path=item["image_path"],
                question_code=item["question_code"],
                extra_data=item.get("extra_data"),
            )
            if result:
                results.append(result)
        
        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/unit/test_inspection_pipeline.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add ai_check/core/inspection_pipeline.py tests/unit/test_inspection_pipeline.py
git commit -m "feat(core): add inspection pipeline for task orchestration"
```

---

## Task 8: 配置文件

**Files:**
- Create: `config/config.yaml`
- Create: `config/plugins.yaml`
- Create: `config/prompts.yaml`

- [ ] **Step 1: Create main config file**

```yaml
# config/config.yaml
app:
  name: "荣耀门店AI点检系统"
  version: "1.0.0"
  language: "zh_CN"

database:
  path: "data/ai_check.db"

storage:
  image_path: "data/images"
  export_path: "data/exports"

detection:
  default_detector: "llm"
  confidence_threshold: 0.8
  parallel_tasks: 3

report:
  template_path: "templates/"
  default_format: "excel"
```

- [ ] **Step 2: Create plugins config file**

```yaml
# config/plugins.yaml
plugins:
  # LLM 插件
  - name: openai_gpt4v
    enabled: true
    type: llm
    module: ai_check.plugins.llm.openai_plugin
    class: OpenAIPlugin
    config:
      api_key: "${OPENAI_API_KEY}"
      model: "gpt-4o"

  # 本地插件（后续添加）
  - name: image_quality
    enabled: false
    type: local
    module: ai_check.plugins.local.quality_plugin
    class: ImageQualityPlugin
    config:
      blur_threshold: 100
```

- [ ] **Step 3: Create prompts config file**

```yaml
# config/prompts.yaml
# 提示词模板配置

default_prompt: |
  你是一个门店巡检验收专家。请根据以下检查规范分析图片。

  【问题编号】{question_code}
  【检查项目】{question_name}
  【检查规范】
  {rules}

  请分析图片并判断是否符合规范。输出格式如下：
  1. 是否合规：是/否
  2. 置信度：0-100%
  3. 发现的问题：（如有问题请列出）
  4. 整改建议：（如有问题请给出建议）

  请开始分析：

# 特定问题的提示词覆盖
overrides:
  B1: |
    你是门店陈列检查专家。请检查图片中的整体陈列情况。
    
    检查要点：
    - 物料是否有破损
    - 是否有遮挡客流通道的情况
    - 灯箱是否正常亮起
    
    请输出检查结果。
```

- [ ] **Step 4: Commit**

```bash
mkdir -p config
git add config/config.yaml config/plugins.yaml config/prompts.yaml
git commit -m "feat(config): add configuration files for app, plugins and prompts"
```

---

## Task 9: 更新依赖文件

**Files:**
- Modify: `requirements.txt`
- Modify: `requirements-dev.txt`

- [ ] **Step 1: Update requirements.txt**

```txt
# AI Check - Image AI Checker Dependencies

# GUI Framework
PyQt6>=6.5.0

# Database
sqlalchemy>=2.0.0

# LLM APIs
openai>=1.0.0
# anthropic>=0.18.0  # Claude (可选)
# dashscope>=1.14.0  # 通义千问 (可选)

# Image Processing
opencv-python>=4.8.0
Pillow>=10.0.0
numpy>=1.24.0
imagehash>=4.3.0

# Report Generation
openpyxl>=3.1.0
python-docx>=1.1.0

# Configuration
pyyaml>=6.0
pydantic>=2.0.0

# Utilities
loguru>=0.7.0
tqdm>=4.65.0
psutil>=5.9.0

# Type Support
typing-extensions>=4.5.0
```

- [ ] **Step 2: Update requirements-dev.txt**

```txt
# Development Dependencies

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-qt>=4.2.0

# Code Quality
black>=23.0.0
isort>=5.12.0
ruff>=0.1.0
mypy>=1.5.0

# Pre-commit
pre-commit>=3.4.0
```

- [ ] **Step 3: Commit**

```bash
git add requirements.txt requirements-dev.txt
git commit -m "feat(deps): update dependencies for LLM API and SQLAlchemy"
```

---

## Task 10: 更新项目文档

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update CLAUDE.md**

在现有 CLAUDE.md 顶部添加项目变更说明：

```markdown
# CLAUDE.md - AI Check 项目开发指南

> **项目变更说明 (2026-06-11)**
> 
> 本项目已从"图片 AI 检查工具"重构为"荣耀门店 AI 点检系统"。
> 
> **主要变化：**
> - 目标用户：摄影师/设计师 → 门店督导
> - 核心功能：图片真伪检测 → 门店巡检验证
> - 技术方案：本地模型 → 大模型 API（支持多模型）
> - 架构：单一检测器 → 插件化检测器架构
> 
> **详细设计文档：** `docs/荣耀门店AI点检系统设计文档.md`

---

## 📖 项目概述
...
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: update CLAUDE.md with project restructuring notes"
```

---

## 执行总结

完成以上 10 个 Task 后，系统核心框架将具备：

| 模块 | 状态 | 说明 |
|------|------|------|
| 插件系统 | ✅ | 基类 + 管理器 + LLM 基类 |
| OpenAI 插件 | ✅ | 可用的 GPT-4V 检测器 |
| 数据模型 | ✅ | SQLAlchemy ORM 模型 |
| 规范加载器 | ✅ | YAML 规范文件解析 |
| 任务引擎 | ✅ | 检测任务编排 |
| 配置文件 | ✅ | 完整配置体系 |

**下一步迭代：**
- Task 11-15: GUI 页面重构
- Task 16-20: 数据库集成
- Task 21-25: 报告生成

---

**计划完成，保存至：** `docs/superpowers/plans/2026-06-11-inspection-system-mvp.md`
