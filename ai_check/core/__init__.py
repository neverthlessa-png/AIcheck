"""核心模块 - 流水线、检测器基类、任务管理"""

from .detector_base import (
    AnomalyLevel,
    BoundingBox,
    DetectionResult,
    DetectionType,
    DetectorBase,
    ImageInfo,
)
from .detector_registry import DetectorRegistry
from .pipeline import Pipeline, PipelineConfig, PipelineResult, create_pipeline_from_yaml
from .task_manager import Task, TaskManager, TaskStatus

__all__ = [
    # 检测器基类
    "DetectorBase",
    "DetectionResult",
    "DetectionType",
    "AnomalyLevel",
    "BoundingBox",
    "ImageInfo",
    # 注册表
    "DetectorRegistry",
    # 流水线
    "Pipeline",
    "PipelineConfig",
    "PipelineResult",
    "create_pipeline_from_yaml",
    # 任务管理
    "Task",
    "TaskManager",
    "TaskStatus",
]
