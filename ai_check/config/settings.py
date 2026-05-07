"""配置管理模块"""

from pathlib import Path
from typing import Any

import yaml
from loguru import logger


class Settings:
    """应用配置管理"""

    _instance: "Settings | None" = None
    _config: dict[str, Any] = {}

    def __new__(cls) -> "Settings":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._config:
            self._load_default_config()

    def _load_default_config(self) -> None:
        """加载默认配置"""
        config_path = Path(__file__).parent / "default_config.yaml"
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}
            logger.info(f"已加载配置文件: {config_path}")
        else:
            logger.warning("默认配置文件不存在，使用空配置")
            self._config = {}

    def load_config(self, config_path: Path | str) -> None:
        """加载自定义配置文件"""
        config_path = Path(config_path)
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                custom_config = yaml.safe_load(f) or {}
            self._merge_config(custom_config)
            logger.info(f"已加载自定义配置: {config_path}")

    def _merge_config(self, custom: dict[str, Any]) -> None:
        """合并配置（深度合并）"""
        def deep_merge(base: dict, override: dict) -> dict:
            for key, value in override.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        deep_merge(self._config, custom)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分隔的键路径

        Args:
            key: 配置键，如 "hardware.device"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key: str, value: Any) -> None:
        """
        设置配置值

        Args:
            key: 配置键，如 "hardware.device"
            value: 配置值
        """
        keys = key.split(".")
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value

    @property
    def app_name(self) -> str:
        return self.get("app.name", "AI Check")

    @property
    def app_version(self) -> str:
        return self.get("app.version", "0.1.0")

    @property
    def device(self) -> str:
        return self.get("hardware.device", "auto")

    @property
    def batch_size(self) -> int:
        return self.get("detection.batch_size", 32)

    @property
    def data_dir(self) -> Path:
        path = self.get("storage.database.path", "~/.ai_check/data")
        return Path(path).expanduser()

    @property
    def models_dir(self) -> Path:
        path = self.get("models.path", "~/.ai_check/models")
        return Path(path).expanduser()

    @property
    def cache_dir(self) -> Path:
        path = self.get("storage.cache.path", "~/.ai_check/cache")
        return Path(path).expanduser()

    @property
    def log_dir(self) -> Path:
        path = self.get("logging.path", "~/.ai_check/logs")
        return Path(path).expanduser()

    def ensure_directories(self) -> None:
        """确保必要的目录存在"""
        for dir_path in [self.data_dir, self.models_dir, self.cache_dir, self.log_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"目录已创建/确认: {dir_path}")


# 全局配置实例
settings = Settings()
