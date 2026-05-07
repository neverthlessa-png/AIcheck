"""重复图片检测器（哈希方法）"""

from typing import Any

import numpy as np
from loguru import logger

from ai_check.core import (
    AnomalyLevel,
    DetectionResult,
    DetectionType,
    DetectorBase,
    ImageInfo,
)
from ai_check.utils.image_utils import compute_ahash, compute_dhash, compute_phash


@DetectorBase.register("hash_detector")
class HashDetector(DetectorBase):
    """
    哈希重复检测器

    使用感知哈希(pHash)、差异哈希(dHash)、平均哈希(aHash)检测重复图片。
    """

    def __init__(
        self,
        name: str = "hash_detector",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, DetectionType.DUPLICATE_EXACT, config)
        self.hash_type = self._config.get("hash_type", "phash")
        self.threshold = self._config.get("threshold", 0.9)  # 相似度阈值
        self._hash_database: dict[str, str] = {}  # hash -> image_path

    def _initialize(self) -> bool:
        """初始化"""
        logger.info(f"哈希检测器初始化完成，类型: {self.hash_type}")
        return True

    def _detect(self, image_info: ImageInfo) -> DetectionResult:
        """执行检测"""
        # 计算哈希
        if self.hash_type == "phash":
            hash_value = compute_phash(image_info.image)
        elif self.hash_type == "dhash":
            hash_value = compute_dhash(image_info.image)
        else:
            hash_value = compute_ahash(image_info.image)

        # 检查是否已存在
        duplicate_path = self._hash_database.get(hash_value)
        is_duplicate = duplicate_path is not None

        # 存入数据库
        if not is_duplicate:
            self._hash_database[hash_value] = str(image_info.path)

        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_duplicate,
            anomaly_level=AnomalyLevel.ANOMALY if is_duplicate else AnomalyLevel.NORMAL,
            confidence=1.0 if is_duplicate else 0.0,
            description=self._get_description(is_duplicate, duplicate_path),
            metadata={
                "hash_type": self.hash_type,
                "hash_value": hash_value,
                "duplicate_of": duplicate_path,
            },
        )

    def _get_description(self, is_duplicate: bool, duplicate_path: str | None) -> str:
        if not is_duplicate:
            return "未检测到重复图片"
        return f"检测到重复图片，与 {duplicate_path} 相同"

    def add_reference(self, image_path: str, hash_value: str) -> None:
        """添加参考图片到数据库"""
        self._hash_database[hash_value] = image_path

    def clear_database(self) -> None:
        """清空哈希数据库"""
        self._hash_database.clear()

    def get_database_size(self) -> int:
        """获取数据库大小"""
        return len(self._hash_database)
