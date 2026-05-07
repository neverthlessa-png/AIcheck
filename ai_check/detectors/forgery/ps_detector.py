"""PS编辑痕迹检测器"""

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


@DetectorBase.register("ps_detector")
class PSDetector(DetectorBase):
    """
    PS编辑痕迹检测器

    检测图片是否经过Photoshop等工具编辑。
    通过分析ELA(Error Level Analysis)和噪声模式来识别篡改区域。
    """

    def __init__(
        self,
        name: str = "ps_detector",
        config: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(name, DetectionType.FORGERY_PS, config)
        self.threshold = self._config.get("threshold", 0.6)
        self._model = None

    def _initialize(self) -> bool:
        """初始化检测器"""
        try:
            # TODO: 加载预训练模型
            # 这里使用简化的ELA分析方法
            logger.info(f"PS检测器初始化完成，阈值: {self.threshold}")
            return True
        except Exception as e:
            logger.error(f"PS检测器初始化失败: {e}")
            return False

    def _detect(self, image_info: ImageInfo) -> DetectionResult:
        """执行检测"""
        image = image_info.image

        # ELA分析
        ela_result = self._error_level_analysis(image)

        # 噪声分析
        noise_result = self._noise_analysis(image)

        # 综合判断
        combined_score = (ela_result["score"] + noise_result["score"]) / 2
        is_anomaly = combined_score > self.threshold

        if is_anomaly:
            level = AnomalyLevel.ANOMALY if combined_score > 0.8 else AnomalyLevel.SUSPICIOUS
        else:
            level = AnomalyLevel.NORMAL

        return DetectionResult(
            detector_name=self._name,
            detection_type=self._detection_type,
            is_anomaly=is_anomaly,
            anomaly_level=level,
            confidence=combined_score,
            description=self._get_description(is_anomaly, combined_score),
            bounding_boxes=ela_result.get("boxes", []),
            metadata={
                "ela_score": ela_result["score"],
                "noise_score": noise_result["score"],
            },
        )

    def _error_level_analysis(self, image: np.ndarray) -> dict[str, Any]:
        """
        Error Level Analysis

        通过重新压缩图片并比较差异来检测篡改区域
        """
        import cv2

        # 转换为JPEG并重新编码
        encode_param = [cv2.IMWRITE_JPEG_QUALITY, 90]
        _, encoded = cv2.imencode(".jpg", image, encode_param)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)

        # 计算差异
        diff = cv2.absdiff(image, decoded)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # 计算平均差异强度
        mean_diff = np.mean(diff_gray) / 255.0

        # 高差异区域可能是篡改区域
        _, binary = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        from ai_check.core import BoundingBox
        boxes = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 10 and h > 10:  # 过滤小区域
                boxes.append(BoundingBox(x, y, x + w, y + h))

        return {
            "score": min(mean_diff * 5, 1.0),  # 放大并限制到0-1
            "boxes": boxes,
        }

    def _noise_analysis(self, image: np.ndarray) -> dict[str, Any]:
        """
        噪声分析

        分析图片的噪声分布，不一致的噪声模式可能表示篡改
        """
        import cv2

        # 转灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 使用高通滤波提取噪声
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        noise = cv2.absdiff(gray, blur)

        # 计算噪声的方差（不一致性）
        noise_std = np.std(noise) / 255.0

        # 分析噪声分布的一致性
        # 分块分析
        h, w = noise.shape
        block_size = 64
        block_stds = []

        for y in range(0, h - block_size, block_size):
            for x in range(0, w - block_size, block_size):
                block = noise[y : y + block_size, x : x + block_size]
                block_stds.append(np.std(block))

        # 块间方差越大，表示噪声不一致
        if len(block_stds) > 1:
            inconsistency = np.std(block_stds) / 255.0
        else:
            inconsistency = 0

        score = min((noise_std * 2 + inconsistency * 3), 1.0)

        return {"score": score}

    def _get_description(self, is_anomaly: bool, score: float) -> str:
        """生成描述"""
        if not is_anomaly:
            return "未检测到明显的PS编辑痕迹"
        elif score > 0.8:
            return f"检测到明显的编辑痕迹，置信度: {score:.2%}"
        else:
            return f"检测到可疑的编辑痕迹，置信度: {score:.2%}"

    def cleanup(self) -> None:
        """清理资源"""
        self._model = None
        logger.debug("PS检测器资源已清理")
