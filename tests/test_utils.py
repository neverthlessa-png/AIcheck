"""工具函数测试"""

import pytest
import numpy as np
import cv2
from pathlib import Path


class TestImageUtils:
    """图像工具测试"""

    def test_compute_phash(self, sample_image):
        """测试感知哈希计算"""
        from ai_check.utils.image_utils import compute_phash, load_image

        image = load_image(sample_image)
        phash = compute_phash(image)

        assert isinstance(phash, str)
        assert len(phash) > 0

    def test_compute_md5(self, sample_image):
        """测试MD5计算"""
        from ai_check.utils.image_utils import compute_md5

        md5 = compute_md5(sample_image)

        assert isinstance(md5, str)
        assert len(md5) == 32  # MD5长度

    def test_resize_image(self, sample_image):
        """测试图片缩放"""
        from ai_check.utils.image_utils import load_image, resize_image

        image = load_image(sample_image)
        resized = resize_image(image, target_size=50)

        assert resized.shape[0] <= 50
        assert resized.shape[1] <= 50

    def test_hash_similarity(self):
        """测试哈希相似度"""
        from ai_check.utils.image_utils import hash_similarity

        # 相同哈希
        sim = hash_similarity("a" * 16, "a" * 16)
        assert sim == 1.0

        # 不同哈希
        sim = hash_similarity("a" * 16, "b" * 16)
        assert 0 <= sim < 1


class TestHardwareUtils:
    """硬件工具测试"""

    def test_detect_hardware(self):
        """测试硬件检测"""
        from ai_check.utils.hardware_utils import detect_hardware

        info = detect_hardware()

        assert info.cpu_count > 0
        assert info.total_memory_gb > 0
        assert info.platform != ""

    def test_get_available_device(self):
        """测试获取可用设备"""
        from ai_check.utils.hardware_utils import get_available_device

        device = get_available_device()
        assert device in ["cpu", "cuda"]


class TestDatabase:
    """数据库测试"""

    def test_database_creation(self, temp_dir):
        """测试数据库创建"""
        from ai_check.storage.database import Database

        db_path = temp_dir / "test.db"
        db = Database(db_path)

        assert db_path.exists()

        # 测试插入
        result_id = db.insert_detection_result(
            image_path="/test/image.png",
            detector_name="test_detector",
            result_type="test",
            is_anomaly=True,
            confidence=0.9,
        )
        assert result_id > 0

        # 测试查询
        results = db.get_detection_results()
        assert len(results) == 1
        assert results[0]["is_anomaly"] == 1

        db.close()


class TestCache:
    """缓存测试"""

    def test_cache_operations(self, temp_dir):
        """测试缓存操作"""
        from ai_check.storage.cache import CacheManager

        cache = CacheManager(temp_dir / "cache")

        # 设置缓存
        cache.set("test_key", {"data": "test_value"})

        # 获取缓存
        value = cache.get("test_key")
        assert value is not None
        assert value["data"] == "test_value"

        # 删除缓存
        cache.delete("test_key")
        value = cache.get("test_key")
        assert value is None

        # 获取统计
        stats = cache.get_stats()
        assert isinstance(stats, dict)
        assert "count" in stats
