# Test Generation Skill

Generate comprehensive tests for the AI Check project using pytest.

## Trigger

Use this skill when:
- Creating tests for new code
- Expanding test coverage
- Writing regression tests for bugs

## Instructions

### Test Structure

```python
"""Test module for [module_name]"""

import pytest
import numpy as np
from pathlib import Path

from ai_check.core import [ClassUnderTest]


class Test[ClassName]:
    """Tests for [ClassName]"""

    @pytest.fixture
    def setup_data(self):
        """Setup test data"""
        ...

    def test_[scenario]_success(self, setup_data):
        """Test [scenario] with valid input"""
        # Arrange
        ...

        # Act
        ...

        # Assert
        ...

    def test_[scenario]_failure(self, setup_data):
        """Test [scenario] with invalid input"""
        ...

    @pytest.mark.parametrize("input,expected", [
        (value1, expected1),
        (value2, expected2),
    ])
    def test_[scenario]_parametrized(self, input, expected):
        """Test [scenario] with multiple inputs"""
        ...
```

### Test Categories

1. **Unit Tests** (`tests/unit/`)
   - Test single functions/methods
   - Mock external dependencies
   - Fast execution

2. **Integration Tests** (`tests/integration/`)
   - Test component interactions
   - Use real dependencies where appropriate
   - May be slower

3. **GUI Tests** (`tests/gui/`)
   - Use pytest-qt
   - Test UI components
   - Simulate user interactions

### Fixtures (conftest.py)

```python
import pytest
import numpy as np
import cv2
from pathlib import Path
import tempfile

@pytest.fixture
def sample_image():
    """Create a sample test image"""
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    yield image

@pytest.fixture
def sample_image_path(sample_image, tmp_path):
    """Create a sample image file"""
    path = tmp_path / "test.png"
    cv2.imwrite(str(path), sample_image)
    yield path

@pytest.fixture
def detector():
    """Create a detector instance"""
    from ai_check.detectors.forgery.ps_detector import PSDetector
    detector = PSDetector()
    detector.initialize()
    yield detector
    detector.cleanup()

@pytest.fixture
def qtbot(qapp):
    """pytest-qt fixture for GUI testing"""
    return qtbot
```

### PyQt Testing

```python
from pytestqt.qtbot import QtBot
from PyQt6.QtWidgets import QApplication

def test_button_click(qtbot):
    """Test button click behavior"""
    widget = MyWidget()
    qtbot.addWidget(widget)

    # Click button
    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

    # Wait for signal
    with qtbot.waitSignal(widget.finished, timeout=1000):
        widget.start_process()

    # Assert result
    assert widget.result is not None
```

### What to Test

- **Normal behavior**: Happy path scenarios
- **Edge cases**: Empty inputs, boundary values
- **Error handling**: Invalid inputs, exceptions
- **Performance**: Timing for critical functions

### Coverage Goals

- Core modules: > 90%
- Detectors: > 80%
- Utils: > 70%
- GUI: > 50%

## Example Usage

```
Generate tests for ai_check/core/pipeline.py:
1. Unit tests for Pipeline class
2. Test process_single with various inputs
3. Test process_batch with parallel processing
4. Test error handling
5. Include fixtures for common test data
```
