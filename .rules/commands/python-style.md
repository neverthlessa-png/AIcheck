# Python Code Style Rules

Rules for Python code style in the AI Check project.

## Code Style

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Module | snake_case | `image_utils.py` |
| Package | snake_case | `ai_check` |
| Class | PascalCase | `DetectorBase` |
| Function | snake_case | `compute_hash()` |
| Method | snake_case | `detect()` |
| Variable | snake_case | `image_path` |
| Constant | UPPER_SNAKE_CASE | `MAX_BATCH_SIZE` |
| Private | _leading_underscore | `_initialize()` |

### Type Annotations

All public functions and methods MUST have type annotations:

```python
# Correct ✓
def detect(self, image: np.ndarray, threshold: float = 0.5) -> DetectionResult:
    ...

def process_batch(self, images: list[ImageInfo]) -> list[PipelineResult]:
    ...

# Incorrect ✗
def detect(self, image, threshold=0.5):
    ...
```

### Docstrings

Public APIs MUST have Google-style docstrings:

```python
def compute_hash(image: np.ndarray) -> str:
    """Compute perceptual hash of an image.

    Args:
        image: Input image as BGR numpy array.

    Returns:
        Hexadecimal hash string.

    Raises:
        ValueError: If image is empty.
    """
    ...
```

### Import Order

Use isort with the following configuration:

```python
# Standard library
import os
import sys
from pathlib import Path
from typing import Any, Optional

# Third-party
import numpy as np
from loguru import logger

# Local
from ai_check.core import DetectorBase
```

### Line Length

Maximum line length: 100 characters

### Comments

- Use comments to explain WHY, not WHAT
- Use TODO, FIXME, NOTE markers:

```python
# TODO: Implement GPU acceleration
# FIXME: Handle empty image case
# NOTE: Algorithm is less accurate for small images
```

## Formatting

Run these tools before committing:

```bash
# Format code
black ai_check/ tests/

# Sort imports
isort ai_check/ tests/

# Check types
mypy ai_check/

# Lint
ruff check ai_check/
```

## Pre-commit

Install pre-commit hooks:

```bash
pre-commit install
```

Configuration in `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.0.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```
