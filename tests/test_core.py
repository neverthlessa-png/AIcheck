"""核心模块测试"""

import pytest
from pathlib import Path
import numpy as np


class TestDetectorBase:
    """检测器基类测试"""

    def test_detection_type_enum(self):
        """测试检测类型枚举"""
        from ai_check.core import DetectionType

        assert DetectionType.FORGERY_PS.value == "forgery_ps"
        assert DetectionType.DUPLICATE_EXACT.value == "duplicate_exact"

    def test_anomaly_level_enum(self):
        """测试异常级别枚举"""
        from ai_check.core import AnomalyLevel

        assert AnomalyLevel.NORMAL.value == "normal"
        assert AnomalyLevel.ANOMALY.value == "anomaly"

    def test_bounding_box(self):
        """测试边界框"""
        from ai_check.core import BoundingBox

        box = BoundingBox(10, 20, 50, 60)
        assert box.width == 40
        assert box.height == 40
        assert box.area == 1600
        assert box.to_tuple() == (10, 20, 50, 60)

    def test_detection_result(self):
        """测试检测结果"""
        from ai_check.core import DetectionResult, DetectionType, AnomalyLevel

        result = DetectionResult(
            detector_name="test_detector",
            detection_type=DetectionType.FORGERY_PS,
            is_anomaly=True,
            anomaly_level=AnomalyLevel.ANOMALY,
            confidence=0.85,
            description="测试描述",
        )

        assert result.detector_name == "test_detector"
        assert result.is_anomaly is True
        assert result.confidence == 0.85

        result_dict = result.to_dict()
        assert result_dict["detector_name"] == "test_detector"
        assert result_dict["is_anomaly"] is True


class TestDetectorRegistry:
    """检测器注册表测试"""

    def test_register_decorator(self):
        """测试装饰器注册"""
        from ai_check.core import DetectorRegistry, DetectorBase, DetectionType

        @DetectorRegistry.register("test_detector_1")
        class TestDetector1(DetectorBase):
            def _initialize(self):
                return True

            def _detect(self, image_info):
                from ai_check.core import DetectionResult
                return DetectionResult(
                    detector_name=self._name,
                    detection_type=self._detection_type,
                )

        assert DetectorRegistry.is_registered("test_detector_1")
        assert "test_detector_1" in DetectorRegistry.list_registered()

    def test_create_detector(self):
        """测试创建检测器"""
        from ai_check.core import DetectorRegistry

        if DetectorRegistry.is_registered("test_detector_1"):
            detector = DetectorRegistry.create("test_detector_1")
            assert detector.name == "test_detector_1"

    def test_unregister(self):
        """测试注销检测器"""
        from ai_check.core import DetectorRegistry

        DetectorRegistry.unregister("test_detector_1")
        assert not DetectorRegistry.is_registered("test_detector_1")


class TestImageInfo:
    """图片信息测试"""

    def test_image_info_creation(self):
        """测试图片信息创建"""
        from ai_check.core import ImageInfo

        image = np.zeros((100, 100, 3), dtype=np.uint8)
        info = ImageInfo(
            path=Path("/tmp/test.png"),
            image=image,
            md5_hash="abc123",
        )

        assert info.width == 100
        assert info.height == 100
        assert info.md5_hash == "abc123"


class TestPipeline:
    """流水线测试"""

    def test_pipeline_creation(self):
        """测试流水线创建"""
        from ai_check.core import Pipeline, PipelineConfig

        config = PipelineConfig(
            enabled_detectors=["test"],
            parallel=True,
            max_workers=4,
        )
        pipeline = Pipeline(config)

        assert pipeline.config.parallel is True
        assert pipeline.config.max_workers == 4
