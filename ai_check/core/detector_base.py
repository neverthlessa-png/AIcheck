"""检测器基类定义"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional

import numpy as np


class DetectionType(Enum):
    """检测类型枚举"""
    FORGERY_PS = "forgery_ps"  # PS编辑检测
    FORGERY_AI = "forgery_ai"  # AI生成检测
    FORGERY_SPLICE = "forgery_splice"  # 拼接检测
    FORGERY_COPY_MOVE = "forgery_copy_move"  # 复制粘贴检测
    DUPLICATE_EXACT = "duplicate_exact"  # 精确重复
    DUPLICATE_SIMILAR = "duplicate_similar"  # 相似图片
    DOCUMENT_TAMPERING = "document_tampering"  # 文档篡改
    DOCUMENT_TEMPLATE = "document_template"  # 文档模板匹配
    CONTENT_OCR = "content_ocr"  # OCR内容
    CUSTOM = "custom"  # 自定义检测


class AnomalyLevel(Enum):
    """异常级别"""
    NORMAL = "normal"  # 正常
    SUSPICIOUS = "suspicious"  # 可疑
    ANOMALY = "anomaly"  # 异常
    CRITICAL = "critical"  # 严重异常


@dataclass
class BoundingBox:
    """边界框"""
    x1: int
    y1: int
    x2: int
    y2: int

    @property
    def width(self) -> int:
        return self.x2 - self.x1

    @property
    def height(self) -> int:
        return self.y2 - self.y1

    @property
    def area(self) -> int:
        return self.width * self.height

    def to_tuple(self) -> tuple[int, int, int, int]:
        return (self.x1, self.y1, self.x2, self.y2)

    def to_dict(self) -> dict[str, int]:
        return {"x1": self.x1, "y1": self.y1, "x2": self.x2, "y2": self.y2}


@dataclass
class DetectionResult:
    """检测结果"""
    detector_name: str
    detection_type: DetectionType
    is_anomaly: bool = False
    anomaly_level: AnomalyLevel = AnomalyLevel.NORMAL
    confidence: float = 0.0
    description: str = ""
    bounding_boxes: list[BoundingBox] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # 可视化数据
    visualization: Optional[np.ndarray] = None

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "detector_name": self.detector_name,
            "detection_type": self.detection_type.value,
            "is_anomaly": self.is_anomaly,
            "anomaly_level": self.anomaly_level.value,
            "confidence": self.confidence,
            "description": self.description,
            "bounding_boxes": [bb.to_dict() for bb in self.bounding_boxes],
            "metadata": self.metadata,
        }


@dataclass
class ImageInfo:
    """图片信息"""
    path: Path
    image: np.ndarray
    md5_hash: str = ""
    phash: str = ""
    width: int = 0
    height: int = 0
    format: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.width == 0 and self.image is not None:
            self.height, self.width = self.image.shape[:2]


class DetectorBase(ABC):
    """检测器基类"""

    def __init__(
        self,
        name: str,
        detection_type: DetectionType,
        config: dict[str, Any] | None = None,
    ) -> None:
        self._name = name
        self._detection_type = detection_type
        self._config = config or {}
        self._enabled = True
        self._initialized = False

    @property
    def name(self) -> str:
        """检测器名称"""
        return self._name

    @property
    def detection_type(self) -> DetectionType:
        """检测类型"""
        return self._detection_type

    @property
    def enabled(self) -> bool:
        """是否启用"""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def config(self) -> dict[str, Any]:
        """配置"""
        return self._config

    def initialize(self) -> bool:
        """
        初始化检测器（加载模型等）

        Returns:
            初始化是否成功
        """
        if self._initialized:
            return True

        try:
            success = self._initialize()
            self._initialized = success
            return success
        except Exception as e:
            from loguru import logger
            logger.error(f"检测器 {self._name} 初始化失败: {e}")
            return False

    @abstractmethod
    def _initialize(self) -> bool:
        """子类实现的初始化方法"""
        pass

    def detect(self, image_info: ImageInfo) -> DetectionResult:
        """
        执行检测

        Args:
            image_info: 图片信息

        Returns:
            检测结果
        """
        if not self._enabled:
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                description="检测器已禁用",
            )

        if not self._initialized:
            if not self.initialize():
                return DetectionResult(
                    detector_name=self._name,
                    detection_type=self._detection_type,
                    description="检测器初始化失败",
                )

        try:
            return self._detect(image_info)
        except Exception as e:
            from loguru import logger
            logger.exception(f"检测器 {self._name} 执行失败: {e}")
            return DetectionResult(
                detector_name=self._name,
                detection_type=self._detection_type,
                description=f"检测失败: {e}",
            )

    @abstractmethod
    def _detect(self, image_info: ImageInfo) -> DetectionResult:
        """子类实现的检测方法"""
        pass

    def detect_batch(
        self,
        images: list[ImageInfo],
    ) -> list[DetectionResult]:
        """
        批量检测

        Args:
            images: 图片列表

        Returns:
            检测结果列表
        """
        results = []
        for image_info in images:
            results.append(self.detect(image_info))
        return results

    def cleanup(self) -> None:
        """清理资源"""
        pass

    def get_info(self) -> dict[str, Any]:
        """获取检测器信息"""
        return {
            "name": self._name,
            "type": self._detection_type.value,
            "enabled": self._enabled,
            "initialized": self._initialized,
            "config": self._config,
        }
