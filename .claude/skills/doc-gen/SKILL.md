# Documentation Generation Skill

Generate documentation for the AI Check project.

## Trigger

Use this skill when:
- Adding new modules or classes
- Updating existing documentation
- Creating API references
- Writing user guides

## Instructions

### Docstring Format (Google Style)

#### Module Docstring

```python
"""Image forgery detection module.

This module provides detectors for identifying various types of image
manipulation, including:
- Photoshop editing detection
- AI-generated image detection
- Image splicing detection
- Copy-move forgery detection

Example:
    >>> from ai_check.detectors.forgery import PSDetector
    >>> detector = PSDetector()
    >>> detector.initialize()
    >>> result = detector.detect(image_info)
"""
```

#### Class Docstring

```python
class PSDetector(DetectorBase):
    """Photoshop editing痕迹检测器.

    通过ELA(Error Level Analysis)和噪声分析检测图片是否经过
    Photoshop等工具编辑。

    Attributes:
        threshold: 检测阈值，高于此值判定为篡改。
        ela_quality: ELA分析时的JPEG质量。

    Example:
        >>> detector = PSDetector(config={"threshold": 0.6})
        >>> detector.initialize()
        >>> result = detector.detect(image_info)
        >>> print(result.is_anomaly)
        False
    """
```

#### Function/Method Docstring

```python
def detect(self, image_info: ImageInfo) -> DetectionResult:
    """执行PS编辑检测.

    分析图片的ELA特征和噪声分布，判断是否存在编辑痕迹。

    Args:
        image_info: 图片信息对象，包含图片数据和元数据。

    Returns:
        检测结果对象，包含:
        - is_anomaly: 是否检测到异常
        - confidence: 检测置信度 (0-1)
        - bounding_boxes: 疑似篡改区域
        - description: 结果描述

    Raises:
        ValueError: 如果图片格式不支持。
        RuntimeError: 如果检测器未初始化。

    Note:
        对于高分辨率图片 (>4K)，建议先调整尺寸以提高性能。

    Example:
        >>> detector = PSDetector()
        >>> detector.initialize()
        >>> image = load_image("test.jpg")
        >>> info = ImageInfo(path=Path("test.jpg"), image=image)
        >>> result = detector.detect(info)
    """
```

### Documentation Files

#### README.md Structure

```markdown
# Module Name

Brief description.

## Features

- Feature 1
- Feature 2

## Installation

```bash
pip install ai-check
```

## Quick Start

```python
from ai_check import Pipeline

pipeline = Pipeline()
pipeline.add_detector(PSDetector())
results = pipeline.process_batch(images)
```

## Documentation

- [API Reference](./docs/api.md)
- [User Guide](./docs/guide.md)
- [Examples](./examples/)

## License

MIT
```

### API Documentation

For each public module/class:

```markdown
# Module: ai_check.core.pipeline

Pipeline management for coordinating multiple detectors.

## Classes

### Pipeline

Manage detection pipeline.

**Methods:**

#### `__init__(config: PipelineConfig)`

Initialize pipeline with configuration.

#### `add_detector(detector: DetectorBase) -> None`

Add a detector to the pipeline.

#### `process_batch(images: list[ImageInfo]) -> list[PipelineResult]`

Process multiple images.

**Parameters:**
- `images`: List of image info objects

**Returns:**
- List of pipeline results

**Example:**
```python
pipeline = Pipeline()
pipeline.add_detector(PSDetector())
results = pipeline.process_batch(images)
```
```

## Example Usage

```
Generate documentation for ai_check/core/detector_base.py:
1. Update module docstring
2. Add class docstrings with examples
3. Document all public methods
4. Include type information
5. Add usage examples
```
