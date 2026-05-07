"""日志配置模块"""

import sys
from pathlib import Path

from loguru import logger


def setup_logging(
    log_dir: Path | str,
    level: str = "INFO",
    max_size_mb: int = 100,
    backup_count: int = 5,
) -> None:
    """
    配置日志系统

    Args:
        log_dir: 日志目录
        level: 日志级别
        max_size_mb: 单个日志文件最大大小(MB)
        backup_count: 保留的日志文件数量
    """
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # 移除默认处理器
    logger.remove()

    # 控制台输出 - 彩色格式
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
    )

    # 文件输出 - 详细格式
    log_file = log_dir / "image_checker_{time:YYYY-MM-DD}.log"
    logger.add(
        str(log_file),
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
               "{name}:{function}:{line} - {message}",
        rotation=f"{max_size_mb} MB",
        retention=backup_count,
        compression="zip",
        encoding="utf-8",
    )

    # 错误日志单独记录
    error_log = log_dir / "error_{time:YYYY-MM-DD}.log"
    logger.add(
        str(error_log),
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
               "{name}:{function}:{line} - {message}\n{exception}",
        rotation=f"{max_size_mb} MB",
        retention=backup_count,
        compression="zip",
        encoding="utf-8",
    )

    logger.info(f"日志系统已初始化，日志目录: {log_dir}")
