"""测试配置"""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_dir():
    """临时目录fixture"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_image(temp_dir):
    """创建测试图片"""
    import numpy as np
    import cv2

    # 创建一个简单的测试图片
    image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    image_path = temp_dir / "test_image.png"
    cv2.imwrite(str(image_path), image)

    return image_path
