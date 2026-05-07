"""检测流水线"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

import numpy as np
from loguru import logger
from tqdm import tqdm

from .detector_base import DetectorBase, DetectionResult, ImageInfo
from .detector_registry import DetectorRegistry


@dataclass
class PipelineConfig:
    """流水线配置"""
    enabled_detectors: list[str] = field(default_factory=list)
    parallel: bool = True
    max_workers: int = 4
    batch_size: int = 32
    progress_callback: Optional[Callable[[int, int, str], None]] = None


@dataclass
class PipelineResult:
    """流水线结果"""
    image_path: Path
    image_info: ImageInfo
    results: list[DetectionResult] = field(default_factory=list)
    has_anomaly: bool = False
    max_confidence: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "image_path": str(self.image_path),
            "has_anomaly": self.has_anomaly,
            "max_confidence": self.max_confidence,
            "results": [r.to_dict() for r in self.results],
        }


class Pipeline:
    """
    检测流水线

    协调多个检测器执行检测任务，支持并行处理和进度回调。
    """

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self._detectors: list[DetectorBase] = []
        self._executor: Optional[ThreadPoolExecutor] = None

    def add_detector(self, detector: DetectorBase) -> None:
        """添加检测器"""
        self._detectors.append(detector)
        logger.info(f"流水线添加检测器: {detector.name}")

    def add_detector_by_name(
        self,
        name: str,
        config: dict[str, Any] | None = None,
    ) -> None:
        """通过名称添加检测器"""
        detector = DetectorRegistry.get_or_create(name, config)
        self.add_detector(detector)

    def remove_detector(self, name: str) -> None:
        """移除检测器"""
        self._detectors = [d for d in self._detectors if d.name != name]
        logger.info(f"流水线移除检测器: {name}")

    def setup_from_config(self, detector_configs: dict[str, dict[str, Any]]) -> None:
        """
        从配置设置检测器

        Args:
            detector_configs: 检测器配置字典 {detector_name: config}
        """
        for name in self.config.enabled_detectors:
            if DetectorRegistry.is_registered(name):
                cfg = detector_configs.get(name, {})
                self.add_detector_by_name(name, cfg)
            else:
                logger.warning(f"检测器未注册，跳过: {name}")

    def initialize(self) -> bool:
        """初始化所有检测器"""
        success = True
        for detector in self._detectors:
            if not detector.initialize():
                logger.error(f"检测器初始化失败: {detector.name}")
                success = False
        return success

    def process_single(self, image_info: ImageInfo) -> PipelineResult:
        """
        处理单张图片

        Args:
            image_info: 图片信息

        Returns:
            流水线结果
        """
        results = []

        for detector in self._detectors:
            if detector.enabled:
                try:
                    result = detector.detect(image_info)
                    results.append(result)
                except Exception as e:
                    logger.error(f"检测器 {detector.name} 执行失败: {e}")

        # 汇总结果
        has_anomaly = any(r.is_anomaly for r in results)
        max_confidence = max((r.confidence for r in results), default=0.0)

        return PipelineResult(
            image_path=image_info.path,
            image_info=image_info,
            results=results,
            has_anomaly=has_anomaly,
            max_confidence=max_confidence,
        )

    def process_batch(
        self,
        images: list[ImageInfo],
        show_progress: bool = True,
    ) -> list[PipelineResult]:
        """
        批量处理图片

        Args:
            images: 图片列表
            show_progress: 是否显示进度条

        Returns:
            结果列表
        """
        results: list[PipelineResult] = []
        total = len(images)

        if self.config.parallel and total > 1:
            results = self._process_parallel(images, show_progress)
        else:
            results = self._process_sequential(images, show_progress)

        return results

    def _process_sequential(
        self,
        images: list[ImageInfo],
        show_progress: bool,
    ) -> list[PipelineResult]:
        """顺序处理"""
        results = []
        iterator = tqdm(images, desc="检测进度") if show_progress else images

        for i, image_info in enumerate(iterator):
            result = self.process_single(image_info)
            results.append(result)

            if self.config.progress_callback:
                self.config.progress_callback(i + 1, len(images), str(image_info.path))

        return results

    def _process_parallel(
        self,
        images: list[ImageInfo],
        show_progress: bool,
    ) -> list[PipelineResult]:
        """并行处理"""
        results: list[PipelineResult] = [None] * len(images)  # type: ignore

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            futures = {
                executor.submit(self.process_single, img): i
                for i, img in enumerate(images)
            }

            if show_progress:
                futures_iter = tqdm(
                    as_completed(futures),
                    total=len(futures),
                    desc="检测进度",
                )
            else:
                futures_iter = as_completed(futures)

            completed = 0
            for future in futures_iter:
                idx = futures[future]
                results[idx] = future.result()
                completed += 1

                if self.config.progress_callback:
                    self.config.progress_callback(
                        completed,
                        len(images),
                        str(images[idx].path),
                    )

        return results

    def get_detector_names(self) -> list[str]:
        """获取所有检测器名称"""
        return [d.name for d in self._detectors]

    def get_detector_info(self) -> list[dict[str, Any]]:
        """获取所有检测器信息"""
        return [d.get_info() for d in self._detectors]

    def cleanup(self) -> None:
        """清理资源"""
        for detector in self._detectors:
            try:
                detector.cleanup()
            except Exception as e:
                logger.warning(f"清理检测器 {detector.name} 失败: {e}")

        if self._executor:
            self._executor.shutdown()
            self._executor = None


def create_pipeline_from_yaml(config_path: Path | str) -> Pipeline:
    """
    从YAML配置文件创建流水线

    Args:
        config_path: 配置文件路径

    Returns:
        流水线实例
    """
    import yaml

    config_path = Path(config_path)
    with open(config_path, encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    pipeline_config = PipelineConfig(
        enabled_detectors=config_data.get("enabled_detectors", []),
        parallel=config_data.get("parallel", True),
        max_workers=config_data.get("max_workers", 4),
        batch_size=config_data.get("batch_size", 32),
    )

    pipeline = Pipeline(pipeline_config)

    detector_configs = config_data.get("detector_configs", {})
    pipeline.setup_from_config(detector_configs)

    return pipeline
