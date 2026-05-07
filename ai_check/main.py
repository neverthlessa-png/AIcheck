"""Image Checker 应用入口"""

import sys
from pathlib import Path

from loguru import logger

from ai_check.config.settings import settings
from ai_check.utils.log_utils import setup_logging


def setup_app() -> None:
    """初始化应用"""
    # 确保目录存在
    settings.ensure_directories()

    # 配置日志
    setup_logging(
        log_dir=settings.log_dir,
        level=settings.get("logging.level", "INFO"),
        max_size_mb=settings.get("logging.max_size_mb", 100),
        backup_count=settings.get("logging.backup_count", 5),
    )

    logger.info(f"启动 {settings.app_name} v{settings.app_version}")
    logger.info(f"数据目录: {settings.data_dir}")
    logger.info(f"模型目录: {settings.models_dir}")


def main() -> int:
    """主函数"""
    try:
        setup_app()

        # 启动GUI
        from ai_check.app.main_window import MainWindow

        app = MainWindow()
        return app.run()

    except Exception as e:
        logger.exception(f"应用启动失败: {e}")
        return 1


def main_cli() -> int:
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Image Checker - 图片AI检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="配置文件路径",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="不启动GUI，使用命令行模式",
    )
    parser.add_argument(
        "images",
        nargs="*",
        help="待检测的图片路径",
    )

    args = parser.parse_args()

    # 初始化
    setup_app()

    # 加载自定义配置
    if args.config:
        settings.load_config(args.config)

    if args.no_gui:
        # 命令行模式
        return run_cli(args.images)
    else:
        # GUI模式
        return main()


def run_cli(images: list[Path]) -> int:
    """命令行模式运行"""
    if not images:
        logger.error("请指定待检测的图片路径")
        return 1

    logger.info(f"检测 {len(images)} 张图片...")

    from ai_check.core import DetectorRegistry, Pipeline, PipelineConfig
    from ai_check.detectors.forgery.ps_detector import PSDetector
    from ai_check.detectors.duplicate.hash_detector import HashDetector
    from ai_check.utils.image_utils import load_image, compute_md5

    # 创建流水线
    config = PipelineConfig(enabled_detectors=["ps_detector", "hash_detector"])
    pipeline = Pipeline(config)

    # 添加检测器
    pipeline.add_detector(PSDetector())
    pipeline.add_detector(HashDetector())

    # 初始化
    pipeline.initialize()

    # 处理图片
    for image_path in images:
        image_path = Path(image_path)
        if not image_path.exists():
            logger.warning(f"图片不存在: {image_path}")
            continue

        try:
            image = load_image(image_path)
            from ai_check.core import ImageInfo
            image_info = ImageInfo(
                path=image_path,
                image=image,
                md5_hash=compute_md5(image_path),
            )

            result = pipeline.process_single(image_info)
            logger.info(f"检测结果: {image_path.name}")
            logger.info(f"  - 异常: {result.has_anomaly}")
            logger.info(f"  - 置信度: {result.max_confidence:.2%}")

            for r in result.results:
                logger.info(f"  - {r.detector_name}: {r.description}")

        except Exception as e:
            logger.error(f"处理失败 {image_path}: {e}")

    pipeline.cleanup()
    logger.info("检测完成")
    return 0


if __name__ == "__main__":
    sys.exit(main_cli())
