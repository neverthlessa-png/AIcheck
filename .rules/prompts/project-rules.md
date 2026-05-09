# Prompt Rules

Rules for prompts when working with the AI Check project.

## ⚠️ 强制阅读要求 (Mandatory Reading)

**在开始任何开发任务前，必须先阅读 `DEVELOPMENT_LOG.md` 文件！**

```
阅读顺序:
1. DEVELOPMENT_LOG.md (开发日志) ← 必须首先阅读
2. 相关模块代码
3. 相关文档
```

阅读后需要：
- 了解最近的开发内容和变更
- 确认没有冲突的修改
- 理解当前开发进度
- 在完成任务后，提醒用户更新开发日志

---

## Project Context

When starting a new conversation, consider this context:

### Technology Stack

- **Language**: Python 3.10+
- **GUI**: PyQt6
- **Inference**: ONNX Runtime
- **Database**: SQLite
- **Testing**: pytest

### Project Structure

```
ai_check/
├── core/           # Core modules (pipeline, detectors base)
├── detectors/      # Detector implementations
├── app/            # GUI application
├── storage/        # Database, cache
├── utils/          # Utilities
└── config/         # Configuration
```

## When Writing Code

### Always

1. Use type annotations for all public APIs
2. Add Google-style docstrings
3. Follow naming conventions
4. Handle errors gracefully
5. Consider thread safety for GUI code

### Never

1. Block the GUI thread with long operations
2. Store credentials in code
3. Use global mutable state
4. Ignore import order (use isort)

## Common Tasks

### Adding a New Detector

1. Create class inheriting from `DetectorBase`
2. Implement `_initialize()` and `_detect()`
3. Register with `@DetectorRegistry.register("name")`
4. Add tests
5. Update documentation

### Adding GUI Components

1. Use QThread for long operations
2. Use signals for cross-thread communication
3. Clean up in `closeEvent`
4. Add to appropriate widget in `app/widgets/`

### Working with Images

1. Use numpy arrays (BGR format from OpenCV)
2. Release memory after processing
3. Handle different image formats
4. Consider image size limits

## Error Handling

```python
from loguru import logger

try:
    result = detector.detect(image_info)
except ValueError as e:
    logger.error(f"Invalid input: {e}")
    raise
except RuntimeError as e:
    logger.error(f"Detection failed: {e}")
    return DetectionResult(..., description=f"Failed: {e}")
```

## Performance Considerations

1. Batch processing for multiple images
2. GPU acceleration when available
3. Lazy loading of models
4. Memory-efficient image handling

## Testing Checklist

- [ ] Unit tests for new functions
- [ ] Integration tests for workflows
- [ ] Edge cases covered
- [ ] Error cases covered
- [ ] Coverage > 75%
