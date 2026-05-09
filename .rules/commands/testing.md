# Testing Rules

Rules for writing tests in the AI Check project.

## Test Organization

```
tests/
├── conftest.py           # Shared fixtures
├── test_core.py          # Core module tests
├── test_utils.py         # Utility tests
├── unit/                 # Unit tests
│   ├── test_detector_base.py
│   ├── test_pipeline.py
│   └── test_database.py
├── integration/          # Integration tests
│   └── test_full_pipeline.py
└── gui/                  # GUI tests
    └── test_main_window.py
```

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| File | `test_<module>.py` | `test_pipeline.py` |
| Class | `Test<Name>` | `TestPipeline` |
| Method | `test_<scenario>` | `test_detect_with_forgery` |

## Test Structure (AAA Pattern)

```python
def test_detection_result(self, detector, sample_image):
    """Test detection returns correct result structure."""
    # Arrange
    image_info = ImageInfo(path=Path("test.jpg"), image=sample_image)

    # Act
    result = detector.detect(image_info)

    # Assert
    assert result.detector_name == "ps_detector"
    assert result.confidence >= 0.0
    assert result.confidence <= 1.0
```

## Fixtures

Define shared fixtures in `conftest.py`:

```python
import pytest
import numpy as np

@pytest.fixture
def sample_image():
    """Create a sample test image."""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    yield image

@pytest.fixture
def detector():
    """Create and initialize a detector."""
    from ai_check.detectors.forgery.ps_detector import PSDetector
    detector = PSDetector()
    detector.initialize()
    yield detector
    detector.cleanup()
```

## Parametrized Tests

```python
@pytest.mark.parametrize("hash_type,expected_len", [
    ("phash", 16),
    ("dhash", 16),
    ("ahash", 16),
])
def test_hash_length(self, hash_type, expected_len, sample_image):
    """Test hash output length."""
    detector = HashDetector(config={"hash_type": hash_type})
    result = detector.detect(ImageInfo(image=sample_image))
    assert len(result.metadata["hash_value"]) == expected_len
```

## Test Categories

### Unit Tests

- Test single function/method
- Mock external dependencies
- Fast execution
- Location: `tests/unit/`

```python
from unittest.mock import Mock, patch

def test_detector_calls_model(self, detector):
    """Test that detector calls the model correctly."""
    with patch.object(detector, '_run_model') as mock_model:
        mock_model.return_value = np.zeros((10, 10))
        detector.detect(image_info)
        mock_model.assert_called_once()
```

### Integration Tests

- Test component interactions
- Use real dependencies
- May be slower
- Location: `tests/integration/`

```python
def test_full_pipeline(self, tmp_path):
    """Test complete pipeline with multiple detectors."""
    pipeline = Pipeline()
    pipeline.add_detector(PSDetector())
    pipeline.add_detector(HashDetector())

    # Create test images
    images = create_test_images(tmp_path, count=10)

    # Process
    results = pipeline.process_batch(images)

    # Verify
    assert len(results) == 10
    for result in results:
        assert len(result.results) == 2
```

### GUI Tests

- Use pytest-qt
- Test UI behavior
- Location: `tests/gui/`

```python
from pytestqt.qtbot import QtBot

def test_button_click(qtbot):
    """Test button click updates label."""
    widget = MyWidget()
    qtbot.addWidget(widget)

    qtbot.mouseClick(widget.button, Qt.MouseButton.LeftButton)

    assert widget.label.text() == "Clicked"
```

## What to Test

### Must Test

1. **Happy path**: Normal operation
2. **Edge cases**: Empty input, boundaries
3. **Error handling**: Invalid input, exceptions
4. **State changes**: Object state after operations

### Test for Detectors

```python
def test_detector_initialization(self):
    """Test detector initializes correctly."""

def test_detector_detect_normal(self):
    """Test detection with normal image."""

def test_detector_detect_anomaly(self):
    """Test detection with anomalous image."""

def test_detector_confidence_range(self):
    """Test confidence is in valid range."""

def test_detector_cleanup(self):
    """Test resources are released."""
```

## Coverage Requirements

| Module | Minimum Coverage |
|--------|-----------------|
| `core/` | 90% |
| `detectors/` | 80% |
| `utils/` | 70% |
| `gui/` | 50% |
| Overall | 75% |

## Running Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_core.py

# Specific test
pytest tests/test_core.py::TestPipeline::test_process_batch

# With coverage
pytest --cov=ai_check --cov-report=html

# Verbose
pytest -v

# Only fast tests
pytest -m "not slow"
```

## Best Practices

1. **One assertion per test** (when practical)
2. **Use descriptive names**: `test_detect_returns_anomaly_for_edited_image`
3. **Don't test implementation details**: Test behavior
4. **Keep tests independent**: No shared mutable state
5. **Clean up resources**: Use yield in fixtures
