"""缓存管理模块"""

import hashlib
from pathlib import Path
from typing import Any

from loguru import logger
import json


class CacheManager:
    """文件缓存管理器"""

    def __init__(self, cache_dir: Path | str, max_size_mb: int = 1024) -> None:
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.metadata_file = self.cache_dir / "cache_metadata.json"
        self._metadata: dict[str, dict[str, Any]] = self._load_metadata()

    def _load_metadata(self) -> dict[str, dict[str, Any]]:
        """加载缓存元数据"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载缓存元数据失败: {e}")
        return {}

    def _save_metadata(self) -> None:
        """保存缓存元数据"""
        try:
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump(self._metadata, f, indent=2)
        except Exception as e:
            logger.warning(f"保存缓存元数据失败: {e}")

    def _get_cache_key(self, key: str) -> str:
        """生成缓存键"""
        return hashlib.md5(key.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """获取缓存文件路径"""
        cache_key = self._get_cache_key(key)
        return self.cache_dir / f"{cache_key}.cache"

    def get(self, key: str) -> Any | None:
        """
        获取缓存值

        Args:
            key: 缓存键

        Returns:
            缓存值，不存在则返回None
        """
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        try:
            with open(cache_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"读取缓存失败: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值
        """
        cache_path = self._get_cache_path(key)
        cache_key = self._get_cache_key(key)

        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(value, f, ensure_ascii=False)

            # 更新元数据
            self._metadata[cache_key] = {
                "key": key,
                "size": cache_path.stat().st_size,
                "path": str(cache_path),
            }
            self._save_metadata()

            # 检查缓存大小
            self._check_size()

        except Exception as e:
            logger.warning(f"写入缓存失败: {e}")

    def delete(self, key: str) -> None:
        """删除缓存"""
        cache_path = self._get_cache_path(key)
        cache_key = self._get_cache_key(key)

        if cache_path.exists():
            cache_path.unlink()

        if cache_key in self._metadata:
            del self._metadata[cache_key]
            self._save_metadata()

    def clear(self) -> None:
        """清空缓存"""
        for cache_file in self.cache_dir.glob("*.cache"):
            cache_file.unlink()

        self._metadata.clear()
        self._save_metadata()
        logger.info("缓存已清空")

    def _check_size(self) -> None:
        """检查缓存大小，超过限制则清理旧缓存"""
        total_size = sum(
            meta.get("size", 0) for meta in self._metadata.values()
        )

        if total_size > self.max_size_bytes:
            # 按访问时间排序，删除最旧的
            # 简化：删除一半的缓存
            logger.info(f"缓存大小超限({total_size / 1024 / 1024:.2f}MB)，开始清理")

            keys_to_delete = list(self._metadata.keys())[: len(self._metadata) // 2]
            for key in keys_to_delete:
                meta = self._metadata[key]
                cache_path = Path(meta.get("path", ""))
                if cache_path.exists():
                    cache_path.unlink()
                del self._metadata[key]

            self._save_metadata()
            logger.info(f"已清理 {len(keys_to_delete)} 个缓存项")

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        total_size = sum(meta.get("size", 0) for meta in self._metadata.values())
        return {
            "count": len(self._metadata),
            "total_size_mb": total_size / 1024 / 1024,
            "max_size_mb": self.max_size_bytes / 1024 / 1024,
            "usage_percent": (total_size / self.max_size_bytes) * 100,
        }
