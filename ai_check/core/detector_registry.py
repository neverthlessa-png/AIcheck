"""检测器注册表 - 支持动态注册和加载检测器"""

from typing import Any, Optional, Type

from loguru import logger

from .detector_base import DetectorBase


class DetectorRegistry:
    """
    检测器注册表

    支持通过装饰器或直接注册检测器类，实现可扩展的插件机制。
    """

    _detectors: dict[str, Type[DetectorBase]] = {}
    _instances: dict[str, DetectorBase] = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """
        装饰器方式注册检测器

        Args:
            name: 检测器名称

        Returns:
            装饰器函数

        Example:
            @DetectorRegistry.register("my_detector")
            class MyDetector(DetectorBase):
                ...
        """
        def decorator(detector_cls: Type[DetectorBase]) -> Type[DetectorBase]:
            cls._detectors[name] = detector_cls
            logger.debug(f"检测器已注册: {name} -> {detector_cls.__name__}")
            return detector_cls
        return decorator

    @classmethod
    def register_class(cls, name: str, detector_cls: Type[DetectorBase]) -> None:
        """
        直接注册检测器类

        Args:
            name: 检测器名称
            detector_cls: 检测器类
        """
        cls._detectors[name] = detector_cls
        logger.debug(f"检测器已注册: {name} -> {detector_cls.__name__}")

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        注销检测器

        Args:
            name: 检测器名称
        """
        if name in cls._detectors:
            del cls._detectors[name]
            logger.debug(f"检测器已注销: {name}")

        if name in cls._instances:
            cls._instances[name].cleanup()
            del cls._instances[name]

    @classmethod
    def create(
        cls,
        name: str,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> DetectorBase:
        """
        创建检测器实例

        Args:
            name: 检测器名称
            config: 配置字典
            **kwargs: 其他参数

        Returns:
            检测器实例

        Raises:
            KeyError: 检测器未注册
        """
        if name not in cls._detectors:
            raise KeyError(f"检测器未注册: {name}")

        detector_cls = cls._detectors[name]
        instance = detector_cls(name=name, config=config, **kwargs)
        cls._instances[name] = instance
        logger.info(f"创建检测器实例: {name}")
        return instance

    @classmethod
    def get(cls, name: str) -> Optional[DetectorBase]:
        """
        获取已创建的检测器实例

        Args:
            name: 检测器名称

        Returns:
            检测器实例，不存在则返回None
        """
        return cls._instances.get(name)

    @classmethod
    def get_or_create(
        cls,
        name: str,
        config: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> DetectorBase:
        """
        获取或创建检测器实例

        Args:
            name: 检测器名称
            config: 配置字典
            **kwargs: 其他参数

        Returns:
            检测器实例
        """
        instance = cls.get(name)
        if instance is None:
            instance = cls.create(name, config, **kwargs)
        return instance

    @classmethod
    def list_registered(cls) -> list[str]:
        """列出所有已注册的检测器"""
        return list(cls._detectors.keys())

    @classmethod
    def list_instances(cls) -> list[str]:
        """列出所有已创建实例的检测器"""
        return list(cls._instances.keys())

    @classmethod
    def get_detector_info(cls, name: str) -> dict[str, Any]:
        """获取检测器信息"""
        if name not in cls._detectors:
            return {"name": name, "registered": False}

        detector_cls = cls._detectors[name]
        instance = cls._instances.get(name)

        info = {
            "name": name,
            "registered": True,
            "class": detector_cls.__name__,
            "has_instance": instance is not None,
        }

        if instance:
            info.update(instance.get_info())

        return info

    @classmethod
    def cleanup_all(cls) -> None:
        """清理所有检测器实例"""
        for name, instance in cls._instances.items():
            try:
                instance.cleanup()
                logger.debug(f"清理检测器: {name}")
            except Exception as e:
                logger.warning(f"清理检测器 {name} 失败: {e}")

        cls._instances.clear()

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """检查检测器是否已注册"""
        return name in cls._detectors
