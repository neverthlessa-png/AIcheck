"""任务管理器"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Optional

from loguru import logger

from .detector_base import ImageInfo
from .pipeline import Pipeline, PipelineResult


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """检测任务"""
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    total_images: int = 0
    processed_images: int = 0
    results: list[PipelineResult] = field(default_factory=list)
    error_message: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    config: dict[str, Any] = field(default_factory=dict)

    @property
    def progress(self) -> float:
        """进度百分比"""
        if self.total_images == 0:
            return 0.0
        return (self.processed_images / self.total_images) * 100

    @property
    def duration_seconds(self) -> Optional[float]:
        """执行时长（秒）"""
        if self.started_at is None:
            return None
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "total_images": self.total_images,
            "processed_images": self.processed_images,
            "progress": self.progress,
            "duration_seconds": self.duration_seconds,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class TaskManager:
    """任务管理器"""

    def __init__(self, max_concurrent_tasks: int = 1) -> None:
        self.max_concurrent_tasks = max_concurrent_tasks
        self._tasks: dict[str, Task] = {}
        self._current_task: Optional[Task] = None
        self._pipeline: Optional[Pipeline] = None
        self._cancel_flag: bool = False
        self._pause_flag: bool = False

        # 回调函数
        self._on_progress: Optional[Callable[[Task], None]] = None
        self._on_complete: Optional[Callable[[Task], None]] = None
        self._on_error: Optional[Callable[[Task], None]] = None

    def set_callbacks(
        self,
        on_progress: Optional[Callable[[Task], None]] = None,
        on_complete: Optional[Callable[[Task], None]] = None,
        on_error: Optional[Callable[[Task], None]] = None,
    ) -> None:
        """设置回调函数"""
        self._on_progress = on_progress
        self._on_complete = on_complete
        self._on_error = on_error

    def create_task(
        self,
        name: str,
        images: list[ImageInfo],
        config: dict[str, Any] | None = None,
    ) -> Task:
        """
        创建检测任务

        Args:
            name: 任务名称
            images: 待检测图片列表
            config: 任务配置

        Returns:
            创建的任务
        """
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            name=name,
            total_images=len(images),
            config=config or {},
        )
        task.config["images"] = images

        self._tasks[task_id] = task
        logger.info(f"创建任务: {task_id} - {name}, 图片数: {len(images)}")

        return task

    def start_task(
        self,
        task_id: str,
        pipeline: Pipeline,
    ) -> None:
        """
        启动任务

        Args:
            task_id: 任务ID
            pipeline: 检测流水线
        """
        if task_id not in self._tasks:
            raise ValueError(f"任务不存在: {task_id}")

        task = self._tasks[task_id]
        if task.status != TaskStatus.PENDING:
            raise ValueError(f"任务状态不正确: {task.status.value}")

        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        self._current_task = task
        self._pipeline = pipeline
        self._cancel_flag = False
        self._pause_flag = False

        logger.info(f"启动任务: {task_id}")

        try:
            images: list[ImageInfo] = task.config.get("images", [])

            # 设置进度回调
            def progress_callback(current: int, total: int, path: str) -> None:
                task.processed_images = current
                if self._on_progress:
                    self._on_progress(task)

            pipeline.config.progress_callback = progress_callback

            # 执行检测
            results = []
            for i, image_info in enumerate(images):
                # 检查取消标志
                if self._cancel_flag:
                    task.status = TaskStatus.CANCELLED
                    task.completed_at = datetime.now()
                    logger.info(f"任务已取消: {task_id}")
                    return

                # 检查暂停标志
                while self._pause_flag:
                    task.status = TaskStatus.PAUSED
                    import time
                    time.sleep(0.5)

                task.status = TaskStatus.RUNNING

                # 处理单张图片
                result = pipeline.process_single(image_info)
                results.append(result)
                task.results = results
                task.processed_images = i + 1

                if self._on_progress:
                    self._on_progress(task)

            # 完成
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            logger.info(f"任务完成: {task_id}, 处理 {len(results)} 张图片")

            if self._on_complete:
                self._on_complete(task)

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            logger.error(f"任务失败: {task_id}, 错误: {e}")

            if self._on_error:
                self._on_error(task)

        finally:
            self._current_task = None

    def pause_task(self, task_id: str) -> None:
        """暂停任务"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.status == TaskStatus.RUNNING:
                self._pause_flag = True
                logger.info(f"暂停任务: {task_id}")

    def resume_task(self, task_id: str) -> None:
        """恢复任务"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.status == TaskStatus.PAUSED:
                self._pause_flag = False
                logger.info(f"恢复任务: {task_id}")

    def cancel_task(self, task_id: str) -> None:
        """取消任务"""
        if task_id in self._tasks:
            task = self._tasks[task_id]
            if task.status in [TaskStatus.RUNNING, TaskStatus.PAUSED]:
                self._cancel_flag = True
                logger.info(f"取消任务: {task_id}")

    def get_task(self, task_id: str) -> Optional[Task]:
        """获取任务"""
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[Task]:
        """获取所有任务"""
        return list(self._tasks.values())

    def get_running_tasks(self) -> list[Task]:
        """获取运行中的任务"""
        return [
            t for t in self._tasks.values()
            if t.status == TaskStatus.RUNNING
        ]

    def clear_completed_tasks(self) -> None:
        """清理已完成的任务"""
        to_remove = [
            tid for tid, task in self._tasks.items()
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]
        ]
        for tid in to_remove:
            del self._tasks[tid]
        logger.info(f"清理 {len(to_remove)} 个已完成任务")
